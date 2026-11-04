# helpers.py ----------------------------------------------------------------------------------------------

# --- libraries • authored ---
from identity import *
from config   import *

# --- libraries • standard ---
import os
import re
import inspect
import zipfile
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

# overall .................................................................................................

def style_table(df, track, index=False, caption=None, min_width=None, max_height=None, sticky_first_col=False):
    """
    Track-themed DataFrame -> HTML. 
    Always fits: wraps text, scales the font, scrolls as a last resort.
    """
    
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

    html = styler.set_table_styles(styles).to_html()
    box  = f'max-height:{max_height}; ' if max_height else ''
    
    return (f'<div style="container-type:inline-size; overflow:auto; max-width:100%; {box}border:1px solid {t["outer"]}; '
            f'border-radius:8px; box-shadow:{t["shadow"]}; background:{t["body_bg"]};">{html}</div>')


def get_eval_code(eval_fn):
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

def get_data_profiling(df):
    
    p_cols         = [col                          for col in df.columns]
    p_non_nulls    = [df[col].notnull().sum()      for col in df.columns]
    p_pct_null     = [f"{(1 - num / len(df)):.1%}" for num in p_non_nulls]
    p_dtype        = [df[col].dtype                for col in df]
    p_numcat       = [get_field_class     (df[col])    for col in df]
    p_numcat_class = [get_field_subclass(df[col])    for col in df]
    
    p_details = []
    for col in df:
        txt = ''
        if get_field_class(df[col])=='num':
            txt = 'mean-q0-25-50-75-100: '
            try:
                
                # date
                if is_date(df[col]):
                    avg       = to_iso_dt(to_dt(df[col]).mean())
                    quantiles = to_iso_dt(to_dt(to_dt(df[col]).quantile(CORE_DISTRIBUTION)).dt).tolist()
                    txt += str([avg] + quantiles)
    
                # int
                elif is_int(df[col]):
                    txt += str([int(df[col].mean())] + df[col].quantile(CORE_DISTRIBUTION).astype(int).tolist())
    
                # float
                elif is_float(df[col]):
                    txt += str([float(round(df[col].mean(), 2))] + df[col].quantile(CORE_DISTRIBUTION).round(2).tolist())
            except Exception:
                txt += 'error'
        else:
            if get_field_subclass(df[col])=='high-cardinality':
                pct_unique = int(100.0 * df[col].nunique() / len(df[col]))
                txt += f'% unique: {pct_unique}'
            elif get_field_subclass(df[col])=='low-cardinality':
                txt += str(df[col].value_counts().to_dict())
            else:
                txt += 'error'
        p_details.append(txt)
    
    profiling_df = pd.DataFrame(zip(
          p_cols
        , p_dtype
        , p_numcat
        , p_numcat_class
        , p_non_nulls
        , p_pct_null
        , p_details
    ), columns=[
          'column_name'
        , 'dtype'
        , 'field_class'
        , 'field_subclass'
        , 'non_null_cnt'
        , 'null_pct'
        , 'Details'
    ]).sort_values(by=['field_class', 'field_subclass']).reset_index(drop=True)

    profiling_report = get_profiling_report(profiling_df)

    return profiling_df, profiling_report


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
    
    high_str = "`" + "`, `".join(high_card_cols) + "`"
    low_str  = "`" + "`, `".join( low_card_cols) + "`"
    num_str  = "`" + "`, `".join(      num_cols) + "`"
    
    report_paragraph = f"""
<br>

The Data Profiling reviewed **{total_records} customer records** to evaluate overall completeness and quality. 
{completeness_text} 
The evaluation shown in `Details` breaks down across three core field classifications: 
high-cardinality identifiers, low-cardinality categories, and numerical metrics. 
    
For **high-cardinality fields** ({high_str}), uniqueness checks verify entity separation and identifier integrity. 
Primary identifiers (IDs) are expected to be 100% unique. Business identifiers may tolerate a limited % of reuse, e.g., 
phone number. There are also high-cardinality fields for which uniqueness is expected to be lower, like `state`.
For **low-cardinality fields** ({low_str}), the analysis inspects categorical consistency, distribution, and balance. 
For **numerical metrics** ({num_str}), the validation monitors the average and the core distribution for the field, 
with q0, q100 being the min/max values, q50 the median, and q25, q75 the boundaries of the interquartile range. 
This set of metrics enables the inspection of value ranges, distribution boundaries, 
and anomaly detection to flag logical errors such as out-of-bound values or invalid dates. 

<br>
    """.strip()
    
    return report_paragraph


def get_field_subclass(df_col):
    try:
        if get_field_class(df_col)=='cat':
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


def get_field_class(df_col):
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
    
    return dq_tests_df, dq_tests_report
    
    
def get_dq_tests_report(dq_tests_df):
    """
    Generates a dynamic narrative summary from the Data Quality tests DataFrame,
    evaluating overall accuracy, completeness, plausibility, and test outcomes.
    """

    df_eval     = dq_tests_df.reset_index()
    col_mapping = {c.lower().strip(): c for c in df_eval.columns}
    res_col   = _find_col(df_eval, 'test result')
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
    
    report_paragraph = f"""
<br>
    
**Data Quality validation checks** were performed against **{total_tests} rules**, assessing overall _accuracy_, 
_completeness_, and _plausibility_ of data according to defined domains. {class_context}   

Each test actively monitors critical quality risks, such as **entity integrity** for cross-table joins, 
**boundary constraints** for numerical metrics, and **structural validity** for categorical domains. 
Resolving these any failures found ensures that downstream summaries, segmentation models, 
and P&L calculations reflect true operational reality.

{status_str}

<br>
    """.strip()
    
    return report_paragraph


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
        0, 'Data Quality Test', out[cols].astype(str).agg(' · '.join, axis=1)
    )
    return out.drop(columns=cols)
