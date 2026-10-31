# views.py -----------------------------------------------------------------------------------------------------

# --- libraries: authored ---
from identity import *

# --- libraries: standard ---
from operator  import itemgetter
from itertools import groupby
from html      import escape

# toc .....................................................................................................

TOC_CSS = TRACK_CSS + '<style>.toc{' + ''.join(
    f'--ix-{k.replace("_", "-")}:{v};' for k, v in IX.items()
) + '}' + """
.toc{max-width:32rem;background:var(--ix-bg);color:var(--ix-fg);border:1px solid var(--ix-line);border-radius:10px;
     padding:16px 22px;font:14px/1.5 system-ui,-apple-system,'Segoe UI',sans-serif}
.toc a{text-decoration:none!important}
.toc .hint{margin:0 0 12px;color:var(--ix-muted);font-size:12px;font-style:italic}
.toc .tracks{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px}
.toc a.track{display:block;padding:.5em 1em;border:1px solid var(--rl);border-radius:12px;background:var(--bg);line-height:1.3}
.toc a.track:hover{background:var(--hbg)}
.toc .track b{display:block;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--hfg)}
.toc .track span{font-size:12.5px;color:var(--fg)}
.toc .row{display:flex;align-items:baseline;gap:10px;padding:3px 0}
.toc .txt{flex:1}
.toc .kind{flex:none;min-width:5.6em;color:var(--ix-muted)}
.toc .mod{font-weight:700;margin-top:10px;padding-top:10px;border-top:1px solid var(--ix-line)}
.toc .pills{flex:none;white-space:nowrap}
.toc a.pill{display:inline-block;margin-left:4px;padding:.15em .75em;border:1px solid var(--rl);border-radius:999px;
            background:var(--bg);color:var(--hfg)!important;font-size:11px;font-weight:600;letter-spacing:.08em}
.toc a.pill:hover{background:var(--rl);color:var(--bg)!important}
</style>"""


def _pills(anchor):
    return '<span class="pills">' + ''.join(
        f'<a class="pill t-{k}" href="#{anchor(k)}">{k.upper()}</a>' for k in TRACKS) + '</span>'


def render_toc(tasks, kinds, modules):
    tracks = ''.join(f'<a class="track t-{k}" href="#{k}"><b>Track {k.upper()}</b><span>{escape(v)}</span></a>'
                     for k, v in TRACKS.items())
    rows = ['<p class="hint">Click a pill to jump to that task.</p>', f'<div class="tracks">{tracks}</div>']
    for module, m_rows in groupby(tasks, key=itemgetter(1)):
        pills = _pills(lambda k: f'{k}{module}')
        rows.append(f'<div class="row mod"><span class="txt">{module} · {escape(modules[module])}</span>{pills}</div>')
        for kind, _, task, title in m_rows:
            pills = _pills(lambda k: make_cell_id(k, kind, module, task))
            rows.append(f'<div class="row"><span class="kind">{kinds[kind]} {task}</span>'
                        f'<span class="txt">{escape(title)}</span>{pills}</div>')
    return f'{TOC_CSS}<div class="toc">{"".join(rows)}</div><br><hr>'


# comparison ..............................................................................................

COMPARISON_CSS = TRACK_CSS + '<style>.cmp-wrap{' + ''.join(
    f'--ix-{k.replace("_", "-")}:{v};' for k, v in IX.items()
) + '}' + """
.cmp-wrap{container-type:inline-size;overflow:auto;border:1px solid var(--ix-line);border-radius:10px;
          box-shadow:0 1px 3px rgba(15,23,42,.10)}
.cmp-wrap .cmp{table-layout:auto;border-collapse:separate;border-spacing:0;width:100%;
               font:clamp(10px,2.2cqw,13px)/1.45 system-ui,-apple-system,'Segoe UI',sans-serif}

/* one baseline for every cell: beats the host notebook's th/td styles */
.cmp-wrap .cmp :is(th,td){font:inherit;text-align:left;text-transform:none;letter-spacing:normal;vertical-align:top;
                          padding:.7em .9em;overflow-wrap:break-word;border-bottom:1px solid var(--ix-line)}
.cmp-wrap .cmp thead th{font-size:.85em;font-weight:600;border-bottom-width:3px}

/* index columns: Task, Action, Specifier */
.cmp-wrap .cmp .ix{background:var(--ix-bg);color:var(--ix-fg);font-weight:500}
.cmp-wrap .cmp thead .ix{background:var(--ix-head-bg);color:var(--ix-head-fg);font-size:.95em;font-weight:600;
                         border-bottom-color:var(--ix-muted)}
.cmp-wrap .cmp .ix strong{font-weight:700}
.cmp-wrap .cmp .ix small{color:var(--ix-muted);font-size:.9em}
.cmp-wrap .cmp .ix a{color:var(--ix-link);text-decoration:none;font-weight:500}
.cmp-wrap .cmp .ix a:hover{text-decoration:underline}

/* track columns */
.cmp-wrap .cmp thead :is(.t-a,.t-b){background:var(--hbg);color:var(--hfg);border-bottom-color:var(--rl);
                                    text-transform:uppercase;letter-spacing:.08em}
.cmp-wrap .cmp td:is(.t-a,.t-b){background:var(--bg);color:var(--fg);border-bottom-color:var(--ln)}
4444
/* pills */
.cmp details{margin:0 0 .5em}
.cmp summary{display:inline-block;list-style:none;cursor:pointer;user-select:none;padding:.35em .8em;
             border:1px solid var(--rl);border-radius:999px;color:var(--hfg);
             font-size:.85em;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.cmp summary::-webkit-details-marker{display:none}
.cmp summary::before{content:'▸';display:inline-block;width:1em;transition:transform .15s}
.cmp details[open]>summary{background:var(--rl);color:var(--bg)}
.cmp details[open]>summary::before{transform:rotate(90deg)}
.cmp pre{width:0;min-width:100%;margin:.5em 0 0;max-height:420px;overflow:auto;
         font:.92em/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.cmp img{max-width:100%;height:auto;border-radius:6px}
</style>"""


def _slug(s):
    return re.sub(r'\W+', '_', s.lower()).strip('_')


def _snippet(sid, cfg):
    f = cfg['path'] / f'{sid}.py'
    if f.exists():
        code  = f.read_text().rstrip()
        n     = sum(1 for l in code.splitlines() if l.strip() and not l.strip().startswith('#'))
        label = f'Code · {n} lines'
        body  = f'<pre><code>{escape(code)}</code></pre>'
        out   = f'<img loading="lazy" src="{cfg["repo_raw"]}/outputs/{sid}.{cfg["ext"]}" alt="Output of {sid}">'
    else:
        label, body, out = 'Code', '<pre><code>[Code]</code></pre>', '[Output]'
    return (f'<details><summary>{label}</summary>{body}</details>'
            f'<details><summary>Output</summary>{out}</details>')


def render_comparison(comparison, kinds, titles, cfg):
    cols = ''.join(f'<col style="width:{w}%">' for w in WIDTHS.values())
    head = ('<thead><tr><th class="ix">Task</th><th class="ix">Action</th><th class="ix">Specifier</th>'
            '<th class="t-a">Track A · From scratch</th><th class="t-b">Track B · Off the shelf</th></tr></thead>')
    trs = []
    for (kind, module, task), t_rows in groupby(comparison, key=itemgetter(0, 1, 2)):
        t_rows, first = list(t_rows), True
        sid   = f'{kind}_{module}_{task}'                        # task_1_1 · job_task_1_1
        label = f'{kinds[kind]} {module}.{task}'
        title = titles[(kind, module, task)]
        for action, a_rows in groupby(t_rows, key=itemgetter(3)):
            a_rows = list(a_rows)
            for i, row in enumerate(a_rows):
                spec, cells = row[4], []
                if first:
                    jump = ' · '.join(f'<a href="#{t}_{sid}">Track {t.upper()}</a>' for t in 'ab')
                    cells.append(f'<th class="ix" scope="rowgroup" rowspan="{len(t_rows)}"><strong>{label}</strong><br>'
                                 f'{escape(title)}<br><small>{jump}</small></th>')
                    first = False
                if i == 0:
                    cells.append(f'<th class="ix" scope="rowgroup" rowspan="{len(a_rows)}">{escape(action)}</th>')
                key = '_'.join(filter(None, [sid, _slug(action), _slug(spec)]))
                cells += [f'<th class="ix" scope="row">{escape(spec) or "—"}</th>',
                          f'<td class="t-a">{_snippet("a_" + key, cfg)}</td>',
                          f'<td class="t-b">{_snippet("b_" + key, cfg)}</td>']
                trs.append('<tr>' + ''.join(cells) + '</tr>')
    return (f'{COMPARISON_CSS}<div class="cmp-wrap"><table class="cmp"><colgroup>{cols}</colgroup>'
            f'{head}<tbody>{"".join(trs)}</tbody></table></div><br><hr>')


# code cells ..............................................................................................

CODE_HEADER = """
<a id='{cell_id}'></a>

<div class="bn t-{track}">
<div class="bn-eb">Track {TRACK}</div>
<h3>{title}</h3>

{report}

</div>
"""
