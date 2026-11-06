# helpers.py ----------------------------------------------------------------------------------------------

# --- libraries • authored ---
from identity import *
from config   import *

# --- libraries • standard ---
import os
import re
import inspect
import zipfile
import subprocess
from typing        import NamedTuple
from rich.console  import Console
from pathlib       import Path

# --- libraries • third-party ---
import pandas as pd

# --- libraries • display ---
from rich.markdown    import Markdown
from IPython.display  import FileLink
from IPython.display  import display_markdown
from pandas.api.types import is_numeric_dtype as is_num
from pandas.api.types import is_integer_dtype as is_int
from pandas.api.types import is_float_dtype   as is_float
from pandas.api.types import is_bool_dtype    as is_bool

# authored functions versioning ...........................................................................

_REGISTRY = {}

def versioned(name, version):
    def wrap(fn):
        versions = _REGISTRY.setdefault(name, {})
        assert DEV.allow_version_overwrite or version not in versions, f'{name} v{version} already registered'
        versions[version] = fn
        fn.__version__ = version
        return fn
    return wrap


def use(name, version=None):
    versions = _REGISTRY[name]
    return versions[max(versions) if version is None else version]


def build_see_also(name, current, function_title):
    versions = VERSION_NOTES[name]
    latest = max(versions)
    if current == latest:
        return ''
    anchor, note = versions[latest]
    return f'<p class="legend"><strong>See also · <a href="#{anchor}">{function_title} v{latest}</a></strong>, {note}.</p>'

# overall .................................................................................................

def style_table(df, track, caption=None, min_width=None, max_height=None, sticky_first_col=False, bold_first_col=False, right_cols=(), nowrap_cols=()):
    """
    Track-themed DataFrame -> HTML. 
    Always fits: wraps text, scales the font, scrolls as a last resort.
    """

    index = False if len(df) <= 10 else True
    t = THEMES[track.lower()]

    styler = df.style
    if not index:
        styler = styler.hide(axis='index')
    if caption:
        styler = styler.set_caption(caption)

    fit   = [('overflow-wrap', 'break-word'), ('white-space', 'normal')]
    body  =  ('tbody td'                   , 'tbody th'                   )
    zebra =  ('tbody tr:nth-child(even) td', 'tbody tr:nth-child(even) th')
    hover =  ('tbody tr:hover td'          , 'tbody tr:hover th'          )
    base  = [('border-collapse', 'separate'), ('border-spacing', '0'), ('width', '100%'),
            ('table-layout', 'auto'), ('font-family', FONT), ('font-size', 'clamp(10px, 2.4cqw, 13px)')]
    
    if min_width:
        base.append(('min-width', min_width))

    styles = [
        {'selector': '', 'props': [('border-collapse', 'separate'), ('border-spacing',  '0'), ('width', '100%'),
                                   ('table-layout'   , 'auto'    ), ('font-family'   , FONT),
                                   ('font-size'      , 'clamp(10px, 2.4cqw, 13px)')]},
        {'selector': 'caption', 'props': [('caption-side', 'top'), ('text-align', 'left'), ('padding', '0 0 .6em'),
                                          ('color', t['head_fg']), ('font-weight', '600')]},
        {'selector': 'thead th', 'props': [('background-color', t['head_bg']), ('color', t['head_fg']),
                                           ('position', 'sticky'), ('top', '0'), ('z-index', '2'),
                                           ('font-size', '.85em'), ('font-weight', '600'),
                                           ('letter-spacing', '.08em'), ('text-transform', 'uppercase'),
                                           ('text-align', 'left'), ('padding', '.8em .9em'),
                                           ('border-bottom', f"2px solid {t['rule']}")] + fit},
    ]
    styles += [{'selector': s, 'props': [('background-color', t['body_bg']), ('color', t['body_fg']),
                                         ('padding', '.6em .9em'), ('border-bottom', f"1px solid {t['line']}"),
                                         ('font-variant-numeric', 'tabular-nums')] + fit} for s in body]
    styles += [{'selector': s, 'props': [('background-color', t['zebra'])]} for s in zebra]
    styles += [{'selector': s, 'props': [('background-color', t['hover'])]} for s in hover]

    if sticky_first_col:
        styles += [
            {'selector': 'tbody td:first-child', 'props': [('position', 'sticky'), ('left', '0'), ('z-index', '1'),
                                                           ('max-width', '11rem'), ('box-shadow', f"1px 0 0 {t['line']}")]},
            {'selector': 'thead th:first-child', 'props': [('left', '0'), ('z-index', '4')]},
        ]

    if bold_first_col:
        styles += [{'selector': 'tbody td:first-child, tbody th:first-child', 'props': [('font-weight', '600')]}]

    offset  = 1 if index else 0
    visible = list(df.columns)

    right = {c for c in df.columns if is_num(df[c]) and df[c].dtype != bool}
    right |= set(right_cols)
    
    for name in right:
        n = visible.index(name) + 1 + offset
        styles += [
            {'selector': f'thead th:nth-child({n})', 'props': [('text-align', 'right')]},
            {'selector': f'tbody td:nth-child({n})', 'props': [('text-align', 'right')]},
        ]

    for name in nowrap_cols:
        n = visible.index(name) + 1 + offset
        styles += [{'selector': f'tbody td:nth-child({n})',
                    'props': [('white-space', 'nowrap'), ('overflow-wrap', 'normal')]}]

    html = styler.set_table_styles(styles).to_html()
    box  = f'max-height:{max_height}; ' if max_height else ''
    
    return (f'<div style="container-type:inline-size; overflow:auto; max-width:100%; {box}border:1px solid {t["outer"]}; '
            f'border-radius:8px; box-shadow:{t["shadow"]}; background:{t["body_bg"]};">{html}</div>')


def get_code_from_eval(eval_fn):
  """
  Extract the code string from an eval function or lambda.
  Cleans up dictionary keys and multiline wrappers.
  """
  try:
    lines, _ = inspect.getsourcelines(eval_fn)
    full_source = ''.join(lines).strip()

    lambda_idx = full_source.find('lambda')
    if lambda_idx != -1:
      colon_idx = full_source.find(':', lambda_idx)
      if colon_idx != -1:
        expr = full_source[colon_idx + 1 :]
        return expr.strip().rstrip(',')

    return full_source
  except (TypeError, OSError):
    return 'lambda'


def display_txt_as_md(file_path):
    console = Console()
    
    try:
        text_content   = read_from_md(file_path)
        formatted_text = re.sub(r"(?=R\d{2}_)", "\n", text_content)
        formatted_text = formatted_text.lstrip("\n")
        
        md = Markdown(formatted_text)
        console.print(md)
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")

    return


def read_from_md(file_path):
  """Reads and returns the report content from the markdown file."""
  with open(file_path, "r", encoding="utf-8") as f:
    return f.read()


def save_to_md(content, file_path):
    """
    Saves the compiled report string to a markdown file,
    automatically creating parent directories if they don't exist.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def is_date(df_col):
    
    if pd.api.types.is_datetime64_any_dtype(df_col):
        return True
    if pd.api.types.is_numeric_dtype(df_col):
        return False
    non_nulls = df_col.dropna()
    if non_nulls.empty:
        return False
    
    # Looks for standard separators like 2023-01-01, 12/31/2025, or 15.08.2024:
    date_pattern = re.compile(r'^\d{2,4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}')    
    sample = non_nulls.astype(str).head(100)
    matches_pattern = sample.apply(lambda x: bool(date_pattern.search(x))).mean() > 0.5
    
    if matches_pattern:
        try:
            parsed = pd.to_datetime(sample, errors='coerce')
            return parsed.notnull().mean() > 0.5
        except Exception:
            return False
            
    return False


def to_dt(df_col):
    return pd.to_datetime(df_col)


def to_iso_dt(dt):
    return dt.strftime('%Y-%m-%d')


def record_zip(root, name='recorded.zip'):
    root = Path(root)
    with zipfile.ZipFile(root / name, 'w', zipfile.ZIP_DEFLATED) as z:
        for folder in ('snippets', 'outputs'):
            for p in sorted((root / folder).rglob('*')):
                if p.is_file():
                    z.write(p, p.relative_to(root))
    return FileLink(name)


def build_legend(items):
    """items: {term: meaning} -> one themed legend line."""
    body = ' · '.join(f'<b>{k}</b>: {v}' for k, v in items.items())
    return f'<p class="legend"><b>Legend</b> · {body}</p>'


def short_sha(repo_dir):
    """Get identifier of Git commit in use."""
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_dir), 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Cannot read commit from {repo_dir}: {e.stderr.strip()}') from e
    return result.stdout.strip()

# code cells ..............................................................................................

class CellMeta(NamedTuple):
    task_id:    str
    task_title: str
    path_out:   Path | None


def get_cell_meta(track, kind, module, task, path_out_reports):
    """
    Cell metadata from the TASKS registry: task_id, task_title, path_out.
    Note: raises KeyError for unregistered `title`: loud on purpose.
    """
    tid   = make_task_id(track, kind, module, task)
    title = f'{KINDS[kind]} {module}.{task}: {TITLES[(kind, module, task)]}'
    return CellMeta(tid, title, path_out_reports.get(tid))


def finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, dev_render_md=False):
    """Close a task cell: show the report, save it, and (in dev mode) read it back."""
    render_cell(task_id, task_title, action, report_text, track, is_first_action)
    if not path_out:
        return
    save_to_md(report_text, path_out)
    if dev_render_md:
        display_txt_as_md(path_out)
    return


def render_cell(task_id, task_title, action, report_text, track='a', is_first_action=False):
    snippet_id = make_snippet_id(task_id, action)
    anchors = (f"<a id='{task_id}'></a>" if is_first_action else '') + f"<a id='{snippet_id}'></a>"
    display_markdown(CODE_HEADER.format(
        anchors=anchors, track=track.lower(), TRACK=track.upper(),
        action=action, task_title=task_title, report=report_text), raw=True)

# Data Profiling ..............................................................................

class ProfilingResult(NamedTuple):
    table    : object
    legend   : str = ''
    report   : str = ''
    see_also : str = ''

@versioned('get_data_profiling', 2)
def get_data_profiling_v2(df):
    
    field_class    = [use('get_field_class'   , 1)(df[col])  for col in df]
    field_subclass = [use('get_field_subclass', 1)(df[col])  for col in df]
    
    column_name    = [col                                    for col in df.columns]
    non_null_cnt   = [df[col].notnull().sum()                for col in df.columns]
    null_pct       = [f"{(1 - num / len(df)):.1%}"           for num in non_null_cnt]
    data_type      = [str(df[col].dtype)                     for col in df]
    
    core_profile = []

    def _fmt_value(x, kind):
        if kind == 'date':
            return x.date().isoformat()
        x = float(x)
        if kind == 'int':
            return int(x) if x.is_integer() else round(x, 1)
        return round(x, 2)
                
    for i, col in enumerate(df):
        txt = ''
        if field_class[i]=='num':
            kind = 'date' if is_date(df[col]) else 'int' if is_int(df[col]) else 'float'
            series = to_dt(df[col]) if kind == 'date' else df[col]
            
            txt = '[mean]-q0-25-50-75-100: '
            try:
                mean      = _fmt_value(series.mean(), kind)
                quantiles = [_fmt_value(q, kind) for q in series.quantile(CORE_DISTRIBUTION)]
                txt += str([[mean]] + quantiles)
            except Exception as e:
                txt += f'error ({type(e).__name__})'
        else:
            if field_subclass[i]=='high-cardinality':
                pct_unique = int(100.0 * df[col].nunique() / len(df[col]))
                txt += f'% unique: {pct_unique}'
            elif field_subclass[i]=='low-cardinality':
                txt += str(df[col].value_counts().to_dict())
            else:
                txt += 'error'

        core_profile.append(txt)
    
    profiling_data = (
        pd.DataFrame({
            'column_name'    : column_name,
            'core_profile'   : core_profile,
            'null_pct'       : null_pct,
            'non_null_cnt'   : non_null_cnt,
            'field_subclass' : field_subclass,
            'field_class'    : field_class,
            'data_type'      : data_type,
        })
        .sort_values(
            by=['field_class', 'field_subclass'],
            ascending=False,
        )
        .reset_index(drop=True)
    )

    profiling_report = get_profiling_report(profiling_data)
    
    profiling_df = profiling_data.rename(
        columns={
              'column_name'    : 'Column'
            , 'core_profile'   : 'Core profile'
            , 'null_pct'       : 'Null'
            , 'non_null_cnt'   : 'nNulls'
            , 'field_subclass' : 'Subclass'
            , 'field_class'    : 'Class'
            , 'data_type'      : 'dType'
        }
    )

    profiling_legend = build_legend(PROFILING_LEGEND)

    return ProfilingResult(
        table  = profiling_df, 
        legend = profiling_legend, 
        report = profiling_report
    )


@versioned('get_data_profiling', 1)
def get_data_profiling_v1(df):

    total_rows = len(df)
    
    column_name  = list(df.columns)
    non_null_cnt = [df[col].notnull().sum() for col in df]
    null_pct     = [f"{(1 - cnt / total_rows):.1%}" if total_rows > 0 else "0.0%" for cnt in non_null_cnt]
    data_type    = [str(df[col].dtype) for col in df]

    p_mean   = [f"{df[col].mean():.1f}"   if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    p_median = [f"{df[col].median():.1f}" if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    p_min    = [f"{df[col].min():.1f}"    if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    p_max    = [f"{df[col].max():.1f}"    if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    
    profiling_data = (
        pd.DataFrame(
            zip(
                column_name,
                data_type,
                null_pct,
                non_null_cnt,
                p_mean,
                p_median,
                p_min,
                p_max,
            ),
            columns=[
                'column_name',
                'data_type',
                'null_pct',
                'non_null_cnt',
                'mean',
                'median',
                'min',
                'max',
            ],
        )
        .sort_values(
            by=['data_type', 'column_name'],
            ascending=True,
        )
        .reset_index(drop=True)
    )
    
    profiling_df = profiling_data.rename(
        columns={
              'column_name'    : 'Column'
            , 'dtype'          : 'dType'
            , 'null_pct'       : 'Null'
            , 'non_null_cnt'   : 'nNulls'
            , 'mean'           : 'Mean'
            , 'median'         : 'Median'
            , 'min'            : 'Min'
            , 'max'            : 'Max'
        }
    )

    see_also_note = build_see_also('get_data_profiling', 1, 'Data Profiling')

    return ProfilingResult(
        table    = profiling_df, 
        see_also = see_also_note
    )


def get_profiling_report(df):
    
    total_records = int(df["non_null_cnt"].max())

    incomplete_rows = df[df["non_null_cnt"] < total_records]
    if incomplete_rows.empty:
        completeness_text = (
            "The assessment confirms complete data across all fields with zero"
            " missing values."
        )
    else:
        missing_summary = ", ".join(
            f"`{row['column_name']}`" for _, row in incomplete_rows.iterrows()
        )
        completeness_text = (
            f"The assessment identified **missing values** in: {missing_summary}."
        )
    
    high_card_cols = df[df["field_subclass"] == "high-cardinality"][
      "column_name"
    ].tolist()
    low_card_cols = df[df["field_subclass"] == "low-cardinality"][
      "column_name"
    ].tolist()
    num_cols = df[df["field_subclass"].isin(["integer", "float", "date"])][
      "column_name"
    ].tolist()
    
    high_cardin_str = "`" + "`, `".join(high_card_cols) + "`"
    low_cardin_str  = "`" + "`, `".join( low_card_cols) + "`"
    num_str  = "`" + "`, `".join(      num_cols) + "`"
    
    report_paragraph = PROFILING_ANALYSIS_TEMPLATE.format(
        total_records     = total_records,
        completeness_text = completeness_text,
        high_cardin_str   = high_cardin_str,
        low_cardin_str    = low_cardin_str,
        num_str           = num_str
    ).strip()
    
    return report_paragraph


@versioned('get_field_subclass', 1)
def get_field_subclass_v1(df_col):
    try:
        if use('get_field_class', 1)(df_col)=='cat':
            if df_col.nunique()<=LOW_CARDIN_THRESH:
                field_subclass = 'low-cardinality'
            else:
                field_subclass = 'high-cardinality'
        elif is_date (df_col): field_subclass = 'date'
        elif is_int  (df_col): field_subclass = 'integer'
        elif is_float(df_col): field_subclass = 'float'
        else: return 'unknown'
        return field_subclass
    except NameError:
        return 'unknown field_class'


@versioned('get_field_class', 1)
def get_field_class_v1(df_col):
    if (not is_num(df_col) and not is_date(df_col)):
        field_class = 'cat'
    elif df_col.dtype=='bool':
        field_class = 'cat'
    else:
        field_class = 'num'
    return field_class


# Data Audit ..................................................................................

def get_dq_test_results(dq_tests):
    """
    For the full suite of Data Quality tests:
    Returns a summary df and a report.
    """
    
    dq_tests_df = pd.DataFrame(dq_tests)
    dq_tests_df.set_index(['ID', 'Dimension', 'Field', 'Rule'], inplace=True)
    dq_tests_report = get_dq_tests_report(dq_tests_df)

    dq_tests_legend = build_legend(DQ_TESTS_LEGEND)
    
    return dq_tests_df, dq_tests_legend, dq_tests_report
    
    
def get_dq_tests_report(dq_tests_df):
    """
    Generates a dynamic narrative summary from the Data Quality tests DataFrame,
    evaluating overall accuracy, completeness, plausibility, and test outcomes.
    """

    df_eval     = dq_tests_df.reset_index()
    col_mapping = {c.lower().strip(): c for c in df_eval.columns}
    res_col   = _find_col(df_eval, 'result')
    class_col = _find_col(df_eval, 'class')
    total_tests = len(df_eval)
    
    failed_mask = df_eval[res_col].astype(str).str.contains("Fail", case=False, na=False)
    failed_cnt  = failed_mask.sum()
    passed_cnt  = total_tests - failed_cnt
    
    if failed_cnt == 0:
        status_str = f"**✅ All {total_tests} tests passed successfully.**"
    elif passed_cnt == 0:
        status_str = f"""
**❌ All {total_tests} tests failed (Total: {total_tests}).**  
The overall quality of raw data is low, and warrants ample review.
        """
    else:
        status_str = f"""
**❌ Failed tests: {failed_cnt}**, ✅ Passed: {passed_cnt} (Total: {total_tests}).  
The overall quality of raw data is mixed, and some fields require cleaning.
        """
    try:
        classes_found = df_eval[class_col].unique().tolist()
        class_str = ", ".join(str(c).strip() for c in classes_found)
        class_context = f"The test covers checks for the following classes: {class_str}."
    except Exception:
       class_context = "Tests span completeness, uniqueness, and validity dimensions."
    
    report_paragraph = AUDIT_ANALYSIS_TEMPLATE.format(
        total_tests   = total_tests,
        class_context = class_context,
        status_str    = status_str,
    ).strip()
    
    return report_paragraph


def get_dq_test_data(df, rules_config):
    """One row per rule: evaluate the rule on df and describe the outcome."""
    dq_test_data = []
    for i, cfg in enumerate(rules_config, start=1):
        bad_items = cfg['eval_fn'](df)
        cnt, msg  = get_dq_test_findings(bad_items, cfg['noun'])
        dq_test_data.append({
              'ID'        : f"Rule {i:02d}"
            , 'Dimension' : cfg['dim']
            , 'Field'     : cfg['field']
            , 'Rule'      : cfg['rule']
            , 'Result'    : '✅&nbsp;Passed' if cnt == 0 else '❌&nbsp;Failed'
            , 'Affected'  : cnt
            , '%'         : f'{cnt / len(df):.1%}'
            , 'Details'   : msg
            , 'Relevance' : cfg['relevance']
            , 'Class'     : cfg['class']
            , 'Code'      : get_code_from_eval(cfg['eval_fn'])
        })
    return dq_test_data


def _find_col(df, keyword):
    """
    Find a column matching a specific keyword.
    StopIteration if missing: loud on purpose.
    """
    return next(c for c in df.columns if keyword in c.lower())


def get_dq_test_findings(items, noun='value'):
    """
    For each Data Quality test:
    Calculates count and returns a clean, pluralized detail string.
    """
    
    cnt    = len(items)
    plural = 's' if cnt > 1 else ''
    msg    = f"{cnt} {noun}{plural} found: {items}" if cnt > 0 else 'All clean.'
    
    return cnt, msg


def get_rules_from_file(file_path, track='a', header_shift=3):
  """
  Reads the Rules Markdown file, normalizes headings, restores rule-level line breaks,
  and wraps it in a card themed by the track.
  """
  text_content   = read_from_md(file_path)
  formatted_text = re.sub(r'(?=\bR\d{2}_)', '\n', text_content)

  def shift_header(match):
    return '#' * (len(match.group(1)) + header_shift) + match.group(2)

  normalized_text = re.sub(r'^(#{1,6})( .+$)', shift_header, formatted_text, flags=re.MULTILINE)

  return f'{TRACK_CSS}\n\n<div class="t-{track.lower()} card">\n\n{normalized_text.strip()}\n\n</div>\n'


def build_dq_tests_labels(df):
    """Combine index fields for UI convenience."""
    cols = ['ID', 'Dimension', 'Field', 'Rule']
    out = df.reset_index()
    out.insert(
        0, 'Test', out[cols].astype(str).agg(' · '.join, axis=1)
    )
    return out.drop(columns=cols)
