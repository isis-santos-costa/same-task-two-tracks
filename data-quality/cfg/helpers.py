# helpers.py ----------------------------------------------------------------------------------------------

# --- libraries • authored ---
from identity import *
from config   import *

# --- libraries • standard ---
import io
import os
import re
import math
import base64
import inspect
import zipfile
import subprocess
from typing        import NamedTuple
from rich.console  import Console
from pathlib       import Path

# --- libraries • third-party ---
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt

# --- libraries • display ---
from rich.markdown    import Markdown
from IPython.display  import FileLink
from IPython.display  import display_markdown
from pandas.api.types import CategoricalDtype
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


def sort_cat(col_name, cat_order):
    """Sort categorical"""
    return lambda df: df[col_name].astype(CategoricalDtype(categories=cat_order, ordered=True))


def get_clean_dict(d):
    """Return a dictionary without string quotation marks on keys."""
    content = ", ".join(f"{k}: {v}" for k, v in d.items())
    return f"{{{content}}}"


def style_raw_table(df, track, sticky_first_col=True):
    return style_table(
        df, 
        track,
        min_width='44rem', 
        max_height='360px',
        sticky_first_col=True,
    )


def get_metric_shift(raw_series, proc_series, func):
    """Compute raw value, processed value, and % change (processed vs raw)."""
    raw_val, proc_val = func(raw_series), func(proc_series)
    return raw_val, proc_val, proc_val / raw_val - 1
    

def get_iso_date(df, date_col_name):
    """
    Replace mixed date values with ISO format.
    Raises ValueError if any unparsed values or nulls are detected.
    """
    new_col_name = date_col_name + '_iso'
    
    parsed_dates = pd.to_datetime(
        df[date_col_name], 
        format='mixed', 
        errors='coerce'
    )

    unparsed_sample = df.loc[parsed_dates.isna(), date_col_name].unique()[:5]
    
    nat_count = parsed_dates.isna().sum()
    if nat_count > 0:
        raise ValueError(
            f"Date parsing error: Found {nat_count} unparsed or missing entry(ies) "
            f"in column '{date_col_name}'. First 5: {unparsed_sample}"
        )
    
    df[new_col_name] = parsed_dates.dt.strftime('%Y-%m-%d')
    df = df.drop(columns=date_col_name)
    
    return df
    

# code cells ..............................................................................................

class CellMeta(NamedTuple):
    task_id:    str
    task_title: str
    path_out:   Path | None


def get_cell_meta(track, kind, module, task, path_out_reports, show_title=False):
    """
    Cell metadata from the TASKS registry: task_id, task_title, path_out.
    Note: raises KeyError for unregistered `title`: loud on purpose.
    """
    tid   = make_task_id(track, kind, module, task)
    title = f'<h3>{KINDS[kind]} {module}.{task}: {TITLES[(kind, module, task)]}</h3>' if show_title else ''
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
    t = task_id.upper().split('_')
    task_short = f"{t[1]} {'.'.join(t[2:])}"
    eyebrow_suffix = f' · {task_short}' if not task_title else ''
    title_html = f'{task_title}'
    display_markdown(CODE_HEADER.format(
        anchors=anchors, track=track.lower(), TRACK=track.upper(), eyebrow_suffix=eyebrow_suffix,
        action=action, task_title=title_html, report=report_text), raw=True)


# Data Profiling ..............................................................................

class ProfileResult(NamedTuple):
    table         : object
    legend        : str    = ''
    report        : str    = ''
    report_help   : str    = ''
    see_also      : str    = ''
    styled        : object = None
    distributions : object = None

    def sections(self, show_help=False):
        parts = [self.styled, self.legend, self.see_also, self.report,
                 self.report_help if show_help else '', self.distributions]
        return [p for p in parts if p]


# --- versions ---

@versioned('get_data_profile', 1)
def get_data_profile_v1(df):

    total_rows = len(df)
    
    column_name  = list(df.columns)
    non_null_cnt = [df[col].notnull().sum() for col in df]
    null_pct     = [f"{(1 - cnt / total_rows):.1%}" if total_rows > 0 else '0.0%' for cnt in non_null_cnt]
    data_type    = [str(df[col].dtype) for col in df]

    p_mean   = [f"{df[col].mean():.1f}"   if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    p_median = [f"{df[col].median():.1f}" if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    p_min    = [f"{df[col].min():.1f}"    if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    p_max    = [f"{df[col].max():.1f}"    if (is_num(df[col]) and not is_bool(df[col])) else '---' for col in df]
    
    profile_data = (
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
    
    profile_df = profile_data.rename(
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

    profile_see_also = build_see_also('get_data_profile', 1, 'Data Profiling')

    return ProfileResult(
        table    = profile_df, 
        see_also = profile_see_also
    )


@versioned('get_data_profile', 2)
def get_data_profile_v2(df):

    
    def _fmt_value(x, kind, is_pct=False):
        if is_pct:
            return f'{x:.0%}'
        if kind == 'date':
            return x.date().isoformat()
        if kind == 'date':
            return x.date().isoformat()
        x = float(x)
        if kind == 'int':
            return int(x) if x.is_integer() else round(x, 1)
        return round(x, 2)
        

    p = {
        'column_name'    : [],
        'core_profile'   : [],
        'non_null_cnt'   : [],
        'null_pct'       : [],
        'field_subclass' : [],
        'field_class'    : [],
        'data_type'      : [],
    }
    
    for c in df:
        
        non_null_cnt = df[c].notnull().sum()
        
        p['column_name']   .append(c)
        p['non_null_cnt']  .append(non_null_cnt)
        p['null_pct']      .append(f"{(1 - non_null_cnt / len(df)):.1%}")
        p['field_subclass'].append(use('get_field_subclass', 1)(df[c]))
        p['field_class']   .append(use('get_field_class'   , 1)(df[c]))
        p['data_type']     .append(str(df[c].dtype))
    
    core_profile = []
   
    for col, f_class, f_subclass in zip(df.columns, p['field_class'], p['field_subclass']):
        
        txt = ''
        
        if f_class == 'num':
            
            is_dt  = is_date(df[col])
            kind   = 'date' if is_dt else ('int' if is_int(df[col]) else 'float')
            series = to_dt(df[col]) if is_dt else df[col]

            prefix = ('[rcv]-' if not is_dt else '') + '[mean]-[q0-25-50-75-100]]⸺'
            
            try:
                mean_val  =  _fmt_value(series.mean(), kind)
                quantiles = [_fmt_value(q, kind) for q in series.quantile(CORE_DISTRIBUTION)]

                if is_dt:
                    payload = [[mean_val], quantiles]
                    
                else:
                    iqr     = quantiles[3] - quantiles[1]
                    median  = quantiles[2]
                    rcv     = _fmt_value(3/4 * iqr / median, kind, is_pct=True)
                    payload = [[rcv], [mean_val], quantiles]

                txt = prefix + str(payload).replace("'", "")
            
            except Exception as e:
                txt += f'error ({type(e).__name__})'
                
        else:
            if f_subclass == 'high-cardinality':
                pct_unique = int(100.0 * df[col].nunique() / len(df[col]))
                txt += f'% unique: {pct_unique}'
                
            elif f_subclass == 'low-cardinality':
                freq_pct = (df[col].value_counts() / df[col].notnull().sum()).map(lambda x: f"{x:.0%}")
                txt += str(freq_pct.to_dict()).replace("'", "")
                
            else:
                txt += 'error'

        p['core_profile'].append(txt)
    
    profile_data = (
        pd.DataFrame(p)
        .sort_values(
            by=['field_class', 'field_subclass'],
            ascending=False,
        )
        .assign(
            field_class   =sort_cat('field_class'   , PROFILE_CLASS_ORDER   ),
            field_subclass=sort_cat('field_subclass', PROFILE_SUBCLASS_ORDER),
        )
        .reset_index(drop=True)
    )
    
    profile_df = profile_data.rename(
        columns={
              'column_name'    : 'Column'
            , 'core_profile'   : 'Core profile'
            , 'non_null_cnt'   : 'nNulls'
            , 'null_pct'       : 'Null'
            , 'field_subclass' : 'Subclass'
            , 'field_class'    : 'Class'
            , 'data_type'      : 'dType'
        }
    )

    profile_legend = build_legend(PROFILE_LEGEND)
    profile_report, profile_report_help = get_profile_report(profile_data)

    profile_see_also = build_see_also('get_data_profile', 2, 'Data Profiling')

    return ProfileResult(
        table       = profile_df, 
        legend      = profile_legend, 
        report      = profile_report,
        report_help = profile_report_help,
        see_also    = profile_see_also,
    )


@versioned('get_data_profile', 3)   # current
def get_data_profile_v3(df, track):

    
    def _fmt_value(x, kind):
        if kind == 'date':
            return x.date().isoformat()
        x = float(x)
        if kind == 'int':
            return int(x) if x.is_integer() else round(x, 1)
        return round(x, 2)

    p = {
        'column_name'    : [],
        'core_profile'   : [],
        'non_null_cnt'   : [],
        'null_pct'       : [],
        'field_subclass' : [],
        'field_class'    : [],
        'data_type'      : [],
        'outlier_cnt'    : [],
    }
    
    for c in df:
        
        non_null_cnt = df[c].notnull().sum()
        
        p['column_name']   .append(c)
        p['non_null_cnt']  .append(non_null_cnt)
        p['null_pct']      .append(f"{(1 - non_null_cnt / len(df)):.1%}")
        p['field_subclass'].append(use('get_field_subclass', 1)(df[c]))
        p['field_class']   .append(use('get_field_class'   , 1)(df[c]))
        p['data_type']     .append(str(df[c].dtype))
    
    core_profile = []
   
    for col, f_class, f_subclass in zip(df.columns, p['field_class'], p['field_subclass']):
        
        txt, n_out = '', 0
        
        if f_class == 'num':
            
            is_dt  = is_date(df[col])
            kind   = 'date' if is_dt else ('int' if is_int(df[col]) else 'float')
            series = to_dt(df[col]) if is_dt else df[col]

            try:
                q     = series.quantile(CORE_DISTRIBUTION)
                parts = [('mean', _fmt_value(series.mean(), kind)),
                         ('q0-25-50-75-100', ', '.join(str(_fmt_value(v, kind)) for v in q))]

                if not is_dt:
                    q1, med, q3 = q.iloc[1], q.iloc[2], q.iloc[3]
                    iqr    = q3 - q1
                    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                    n_lo, n_hi = int((series < lo).sum()), int((series > hi).sum())
                    n_out = n_lo + n_hi
                    out = ', '.join(s for s in (
                        f'<{_fmt_value(lo, kind)}: {n_lo}' if n_lo else '',
                        f'>{_fmt_value(hi, kind)}: {n_hi}' if n_hi else '') if s) or 'none'
                    parts.insert(0, ('out', out))
                    parts.insert(0, ('rcv', f'{0.75 * iqr / med:.0%}' if med else 'n/a'))

                txt = ( '-'.join(f'[{n}]' for n, _ in parts) + '⸺['
                     + ', '.join(f'[{v}]' for _, v in parts) + ']')

            except Exception as e:
                txt = f'error ({type(e).__name__})'
                
        else:
            if f_subclass == 'high-cardinality':
                pct_unique = int(100.0 * df[col].nunique() / len(df[col]))
                txt += f'% unique: {pct_unique}'
                
            elif f_subclass == 'low-cardinality':
                freq_pct = (df[col].value_counts() / df[col].notnull().sum()).map(lambda x: f"{x:.0%}")
                txt += str(freq_pct.to_dict()).replace("'", "")
                
            else:
                txt += 'error'

        p['core_profile'].append(txt)
        p['outlier_cnt'] .append(n_out)
    
    profile_data = (
        pd.DataFrame(p)
        .sort_values(
            by=['field_class', 'field_subclass'],
            ascending=False,
        )
        .assign(
            field_class   =sort_cat('field_class'   , PROFILE_CLASS_ORDER   ),
            field_subclass=sort_cat('field_subclass', PROFILE_SUBCLASS_ORDER),
        )
        .reset_index(drop=True)
    )
    
    profile_df = profile_data.drop(columns='outlier_cnt').rename(
        columns={
              'column_name'    : 'Column'
            , 'core_profile'   : 'Core profile'
            , 'non_null_cnt'   : 'nNulls'
            , 'null_pct'       : 'Null'
            , 'field_subclass' : 'Subclass'
            , 'field_class'    : 'Class'
            , 'data_type'      : 'dType'
        }
    )

    profile_legend = build_legend(PROFILE_LEGEND)
    profile_report, profile_report_help = get_profile_report(profile_data)
    profile_distributions = get_distributions_html(df, track, show_box_plot=True)
    profile_styled =style_profile_table(profile_df, track)

    profile_see_also = build_see_also('get_data_profile', 3, 'Data Profiling')

    profile_core_sections = [
          profile_styled
        , profile_legend
        , profile_see_also
        , profile_report
        , profile_report_help
        , profile_distributions
    ]

    return ProfileResult(
        table         = profile_df,
        legend        = profile_legend,
        report        = profile_report,
        report_help   = profile_report_help,
        distributions = profile_distributions,
        styled        = profile_styled,
        see_also      = profile_see_also,
    )


# --- helpers ---

def get_profile_report(df):
    
    total_records = int(df['non_null_cnt'].max())

    incomplete_rows = df[df['non_null_cnt'] < total_records]
    if incomplete_rows.empty:
        completeness_text = (
            "The assessment confirms complete data across all fields, with no"
            " missing values."
        )
    else:
        missing_summary = ", ".join(
            f"`{row['column_name']}`" for _, row in incomplete_rows.iterrows()
        )
        completeness_text = (
            f"**Missing values** were detected in: {missing_summary}."
        )
    
    high_card_cols = df[df['field_subclass'] == 'high-cardinality'][
      'column_name'
    ].tolist()
    low_card_cols = df[df['field_subclass'] == 'low-cardinality'][
      'column_name'
    ].tolist()
    num_cols = df[df['field_subclass'].isin(['integer', 'float', 'date'])][
      'column_name'
    ].tolist()
    
    high_cardin_str = "`" + "`, `".join(high_card_cols) + "`"
    low_cardin_str  = "`" + "`, `".join( low_card_cols) + "`"
    num_str         = "`" + "`, `".join(      num_cols) + "`"

    counts   = df['outlier_cnt'] if 'outlier_cnt' in df.columns else pd.Series(0, index=df.index)
    out_cols = df.loc[counts > 0, 'column_name']
    outlier_text = '' if out_cols.empty else (
        ' **Outliers** (beyond 1.5×IQR from the quartiles) were flagged in: '
        + ', '.join(f'`{c}`' for c in out_cols) + '.')
    
    profiling_analysis = PROFILE_ANALYSIS_TEMPLATE.format(
        total_records      = total_records,
        completeness_text  = completeness_text,
        outlier_text       = outlier_text,
    ).strip()

    profiling_analysis_help = PROFILE_ANALYSIS_HELP_TEMPLATE.format(
        num_str            = num_str,
        low_cardin_thresh  = LOW_CARDIN_THRESH,
        low_cardin_str     = low_cardin_str,
        high_cardin_str    = high_cardin_str,
    ).strip()
    
    return profiling_analysis, profiling_analysis_help


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
    
    
def get_distributions_html(df, track, show_box_plot=False, max_per_row=6):
    """Histogram per numerical field, plus box plots below them if show_box_plot."""
    t    = THEMES[track.lower()]
    cols = [c for c, s in df.items() if is_num(s) and not pd.api.types.is_bool_dtype(s)]

    def draw_hist(ax, data):
        ax.hist(data, bins=20, color=t['rule'], edgecolor=t['body_bg'])

    def draw_box(ax, data):
        ax.boxplot(data, vert=False, widths=0.6, patch_artist=True,
                   boxprops=dict(facecolor=t['rule'], edgecolor=t['body_fg']),
                   medianprops=dict(color=t['body_bg'], linewidth=2),
                   whiskerprops=dict(color=t['body_fg']), capprops=dict(color=t['body_fg']),
                   flierprops=dict(marker='o', markerfacecolor=t['body_fg'],
                                   markeredgecolor=t['body_fg'], markersize=4))
        ax.set_yticks([])

    def make_img(col, draw):
        fig, ax = plt.subplots(figsize=(3, 2.4))
        fig.subplots_adjust(left=0.2, right=0.96, bottom=0.2, top=0.82)
        draw(ax, df[col].dropna())
        ax.set_title(col, fontsize=18, color=t['body_fg'])
        ax.tick_params(colors=t['body_fg'], labelsize=14)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        for s in ('left', 'bottom'):
            ax.spines[s].set_color(t['line'])
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, dpi=150)
        plt.close(fig)
        img = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f'<img src="data:image/png;base64,{img}" alt="{col}" />'

    def make_rows(items):
        n_rows = math.ceil(len(items) / max_per_row)
        base, extra = divmod(len(items), n_rows)
        rows, start = [], 0
        for i in range(n_rows):
            end = start + base + (1 if i < extra else 0)
            cells = ''.join(f'<div>{x}</div>' for x in items[start:end])
            rows.append(f'<div class="dist-row" style="--n:{max_per_row}">{cells}</div>')
            start = end
        return ''.join(rows)

    if not cols:
        return ''
    html = make_rows([make_img(c, draw_hist) for c in cols])
    if show_box_plot:
        html += make_rows([make_img(c, draw_box) for c in cols])
    return html


def get_missing_summary(df, target_col, group_col, top_n=LOW_CARDIN_THRESH):
    """Compute sorted missingness percentage for a dimension as a dictionary."""
    summary = (
        df[target_col]
        .isna()
        .groupby(df[group_col])
        .mean()
        .mul(100)
        .round(2)
        .sort_values(ascending=False)
    )
    if top_n:
        summary = summary.head(top_n)
    return get_clean_dict(summary.to_dict())


def extract_outlier_thresholds(df, col):
    """Extract low/high thresholds from the Data Profiling Core profile"""
    
    core_profile = df.table.set_index('Column', drop=True).loc[col, 'Core profile']
    low_match  = re.search(r'<\s*([0-9.]+)\s*:', core_profile)
    high_match = re.search(r'>\s*([0-9.]+)\s*:', core_profile)
    
    outlier_thresh_low  = float( low_match.group(1)) if  low_match else None
    outlier_thresh_high = float(high_match.group(1)) if high_match else None

    return outlier_thresh_low, outlier_thresh_high


def style_profile_table(table, track):
    return style_table(
        table,
        track,
        min_width='44rem',
        max_height='360px',
        sticky_first_col=True,
        right_cols=PROFILE_RIGHT_COLS,
        nowrap_cols=('Core profile',),
    )

# Data Quality Tests ..........................................................................

class TestsResult(NamedTuple):
    table    : object
    legend   : str = ''
    report   : str = ''
    see_also : str = ''
    

# --- rules ---

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


# --- orchestrator ---

def get_dq_tests(df, rules_config, version=None):
    """Entry point: run the rules with the chosen version and package the result."""
    name      = 'get_dq_tests_result'
    rows      = use(name, version)(df, rules_config)
    shown     = version or max(_REGISTRY[name])
    table     = pd.DataFrame(rows).set_index(['ID', 'Dimension', 'Field', 'Rule'])
    return TestsResult(
        table    = table,
        legend   = build_legend(DQ_TESTS_LEGEND),
        report   = get_dq_tests_report(table),
        see_also = build_see_also(name, shown, 'Data Quality Tests'),
    )


# --- versions ---

@versioned('get_dq_tests_result', 1)
def get_dq_tests_result_v1(df, rules_config):
    """Evaluate df against Data Quality rules."""
    dq_test_data = []
    for i, cfg in enumerate(rules_config, start=1):
        failed_dq_test_rows = cfg['eval_fn'](df)
        cnt = len(failed_dq_test_rows)
        dq_test_data.append({
              'ID'        : f"Rule {i:02d}"
            , 'Dimension' : cfg['dim']
            , 'Field'     : cfg['field']
            , 'Rule'      : cfg['rule']
            , 'Result'    : '✅&nbsp;Passed' if cnt == 0 else '❌&nbsp;Failed'
            , 'Affected'  : cnt
            , '%'         : f'{cnt / len(df):.1%}'
            , 'Class'     : cfg['class']
            , 'Code' : get_code_from_eval(cfg['eval_fn'])
        })
    return dq_test_data


@versioned('get_dq_tests_result', 2)
def get_dq_tests_result_v2(df, rules_config):
    """
    Evaluate df against Data Quality rules.
    v2 Adds 'Details' and 'Relevance'
    """
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
            , 'Class'     : cfg['class']
            , 'Code' : get_code_from_eval(cfg['eval_fn'])
            , 'Details'   : msg
            , 'Relevance' : cfg['relevance']
        })
    return dq_test_data
    

# --- report ---

def get_dq_tests_report(dq_tests_df):
    """
    Generates a dynamic narrative summary from the Data Quality tests DataFrame,
    evaluating overall accuracy, completeness, plausibility, and test outcomes.
    """

    df_eval     = dq_tests_df.reset_index()
    # col_mapping = {c.lower().strip(): c for c in df_eval.columns}
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


# --- helpers ---

def get_dq_test_findings(items, noun='value'):
    """
    For each Data Quality test:
    Calculates count and returns a clean, pluralized detail string.
    """
    
    cnt    = len(items)
    plural = 's' if cnt > 1 else ''
    msg    = f"{cnt} {noun}{plural} found: {items}" if cnt > 0 else 'All clean.'
    
    return cnt, msg
    

def _find_col(df, keyword):
    """
    Find a column matching a specific keyword.
    StopIteration if missing: loud on purpose.
    """
    return next(c for c in df.columns if keyword in c.lower())


def build_dq_tests_labels(df):
    """Combine index fields for UI convenience."""
    cols = ['ID', 'Dimension', 'Field', 'Rule']
    out = df.reset_index()
    out.insert(
        0, 'Test', out[cols].astype(str).agg(' · '.join, axis=1)
    )
    return out.drop(columns=cols)


# Data Reconciliation .........................................................................

class ReconcileResult(NamedTuple):
    reconciled : bool
    notes      : list
    mismatches : object = None


def build_reconciliation_report(result, track):
    status = '✅ **Reconciled**' if result.reconciled else '❌ **Not reconciled**'
    parts  = [status] + [f'* {n}' for n in result.notes]
    if result.mismatches is not None:
        parts += [
            style_table(result.mismatches.reset_index(), track,
                        min_width='30rem', max_height='360px', sticky_first_col=True),
        ]
    return '\n\n'.join(parts)
    

def reconcile_tables(source_df, target_df):
    """
    Assess whether a source and a target table identically macht.
    Return:
    • reconciled (bool)
    • notes (str list)
    • mismatches matrix (df)
    """
    
    if target_df.equals(source_df):
        reconciled = True
        notes = 'Reconciled: Target is identical to source.'
        mismatch_df = None
        return ReconcileResult(reconciled, notes, mismatch_df)

    reconciled = False
    notes = []
    
    if source_df.shape != target_df.shape:
        notes.append(f'Shape mismatch -> Source: {source_df.shape}, Target: {target_df.shape}<br>')
    
    key_col = source_df.columns[0]
    is_key_unique = source_df[key_col].is_unique
    
    if is_key_unique:
        src_indexed = source_df.set_index(key_col)
        tgt_indexed = target_df.set_index(key_col)
        tgt_aligned = tgt_indexed.reindex(src_indexed.index).reset_index()
        src_aligned = src_indexed.reset_index()
        row_identifier = src_aligned[key_col]
    else:
        src_aligned = source_df.copy().reset_index(drop=True)
        tgt_aligned = target_df.copy().reset_index(drop=True)
        
        if len(tgt_aligned) < len(src_aligned):
            padding = pd.DataFrame(
                np.nan, 
                index=range(len(src_aligned) - len(tgt_aligned)), 
                columns=tgt_aligned.columns
            )
            tgt_aligned = pd.concat([tgt_aligned, padding], ignore_index=True)
            
        row_identifier = pd.Series([f'row #{i+1}' for i in range(len(src_aligned))])
    
    if is_key_unique:
        missing_keys = set(src_indexed.index) - set(tgt_indexed.index)
        extra_keys   = set(tgt_indexed.index) - set(src_indexed.index)
        if missing_keys:
            notes.append(f'Missing rows in target (Keys: {list(missing_keys)})')
        if extra_keys:
            notes.append(f'Extra rows in target (Keys: {list(extra_keys)})')
    
    common_cols = [c for c in source_df.columns if c in target_df.columns and c != key_col]

    mismatch_df_rows = []
    for col in common_cols:
        s_col = src_aligned[col]
        t_col = tgt_aligned[col]
        
        diff_mask = (t_col != s_col) | (t_col.isna() ^ s_col.isna())
        
        if diff_mask.any():
            row_df = pd.DataFrame({
                'row_id': src_aligned.loc[diff_mask, key_col],
                'column': col,
                'target_value': t_col[diff_mask].fillna('empty'),
                'source_value': s_col[diff_mask].fillna('empty'),
            })
            mismatch_df_rows.append(row_df)

    mismatch_df = pd.DataFrame()
    
    if mismatch_df_rows:
        mismatch_df = (
            pd.concat(mismatch_df_rows, ignore_index=True)
            .sort_values(by='row_id', key=lambda s: s.astype(str))
            .set_index('row_id', drop=True)
        )

    total = len(mismatch_df)
    if total > 200:
        mismatch_df = mismatch_df.head(200)
        notes.append(f'Differences found (showing 200 of {total}):')
    else:
        notes.append('Differences found:')
    
    return ReconcileResult(reconciled, notes, mismatch_df)
