# cell_recorder.py ----------------------------------------------------------------------------------------------

"""Record every cell that starts with `# snippet: <id>` as snippets/<id>.py and outputs/<id>.html."""
import re
from html import escape
from pathlib import Path
from IPython import get_ipython

__all__ = ['install_cell_recorder']

_MARKER = re.compile(r'\s*#\s*snippet:\s*(\w+)[ \t]*(?:\n|$)')
_ANCHOR = re.compile(r"<a id=['\"][^'\"]*['\"]></a>")      # inlined copies would hijack the jump links


def _to_html(bundle):
    if 'text/html'     in bundle: return bundle['text/html']
    if 'text/markdown' in bundle: return _markdown_to_html(bundle['text/markdown'])
    return f"<pre>{escape(bundle.get('text/plain', ''))}</pre>"


def _markdown_to_html(text):
    try:
        from markdown_it import MarkdownIt                   # installed with `rich`
        return MarkdownIt('commonmark', {'html': True}).enable('table').render(text)
    except ImportError:
        return f'<pre>{escape(text)}</pre>'


def install_cell_recorder(root='/kaggle/working'):
    ip, root = get_ipython(), Path(root)
    state = {'id': None, 'chunks': []}

    # everything a cell shows through display() passes through the publisher
    pub      = ip.display_pub
    original = getattr(pub, '_snippet_original', pub.publish)   # safe to install twice
    pub._snippet_original = original

    def publish(data, *args, **kwargs):
        if state['id']:
            state['chunks'].append(_to_html(data))
        return original(data, *args, **kwargs)
    pub.publish = publish

    def before(info):
        m = _MARKER.match(info.raw_cell)
        state['id'], state['chunks'] = (m.group(1) if m else None), []

    def after(result):
        sid, chunks = state['id'], state['chunks']
        state['id'] = None
        if not sid or result.error_in_exec:
            return
        if result.result is not None:                           # a value returned by the last line
            bundle, _ = ip.display_formatter.format(result.result)
            chunks.append(_to_html(bundle))

        raw  = result.info.raw_cell
        code = raw[_MARKER.match(raw).end():].strip('\n')
        html = _ANCHOR.sub('', ''.join(chunks))

        (root / 'snippets').mkdir(parents=True, exist_ok=True)
        (root / 'snippets' / f'{sid}.py').write_text(code + '\n', encoding='utf-8')
        if html.strip():
            (root / 'outputs').mkdir(parents=True, exist_ok=True)
            (root / 'outputs' / f'{sid}.html').write_text(html, encoding='utf-8')

    for ev, fn in getattr(ip, '_snippet_hooks', []):            # no duplicate hooks on re-run
        ip.events.unregister(ev, fn)
    ip.events.register(   'pre_run_cell', before)
    ip.events.register(  'post_run_cell', after )
    ip._snippet_hooks = [('pre_run_cell', before), ('post_run_cell', after)]
