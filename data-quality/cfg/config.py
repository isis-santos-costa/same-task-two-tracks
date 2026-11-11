# config.py -----------------------------------------------------------------------------------------------

# --- libraries: authored ---
from identity import TRACKS

# --- libraries: standard ---
import warnings
from pathlib import Path

# development flags .......................................................................................

from dataclasses import dataclass

@dataclass
class DevFlags:
    record_version          : bool = False
    allow_version_overwrite : bool = True
    export_zip              : bool = True
    render_md               : bool = False

DEV = DevFlags()

# overall .................................................................................................

LOW_CARDIN_THRESH = 10
CORE_DISTRIBUTION = [0, 0.25, 0.5, 0.75, 1]

reports = {}

PATH_SNIPPETS = Path('snippets')
OUTPUT_EXT    = 'png'

PROFILE_LEGEND = {
    'RCV': 'robust coefficient of variation <a href="#ref-3">[1]</a>',
    'Null': 'null percentage', 'nNulls': 'non-null count', 'num': 'numerical',
    'cat': 'categorical', 'dtype': 'data type'
}

DQ_TESTS_LEGEND  = {'Affected': 'rows affected', '%': 'share of rows affected'}

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

SMOOTH_HR = """
<hr style="border: none; height: 1px; background-color: rgba(150, 150, 150, 0.2); margin: 20px 0;" />
"""

# version registry for autored functions ..................................................................

VERSION_NOTES = {   # function -> {version: (snippet id of the cell that showcases it, note)}
    'get_data_profile': {
        1: ('a_task_1_1_data_profiling', 'baseline: dtype, mean, median, min, max, nulls, null %'),
        2: ('a_task_1_2_data_profiling', 'with a « Core profile » tailored to column field type'),
        3: ('a_job_task_1_1_data_profiling', 'with an extended « Core profile » monitoring outliers'),
    },
    'get_dq_tests_result': {
        1: ('a_task_1_1_data_quality_tests', 'baseline: result, affected rows, class, code'),
        2: ('a_task_1_2_data_quality_tests', 'with details and relevance for each rule'),
    },
}

# toc & comparison ........................................................................................

PROGRAMS = {   # key used in the registry -> (full name, link)
    'Coursera': ('Data Quality Specialization · Coursera',
                 'https://www.coursera.org/specializations/data-quality-analyst-validation-debugging-and-monitoring'),
    'DataKitchen': ('Data Observability and Data Quality Testing Certification · DataKitchen',
                    'https://datakitchen.io/certifications/data-observability-and-data-quality-testing/'),
}

MODULES = {
    ('Coursera', 1): 'Data Quality · Profiling & Tests',
    ('Coursera', 2): 'Data Quality · Validation & Debugging',
    ('Coursera', 3): 'Data Quality · Monitoring & Prevention',
}

TASKS = [   # (program, kind, module, task, title): the single source of truth, ordered by program, module
    ('Coursera', 'task',     1, 1, 'Profile a dataset and surface quality risks'),
    ('Coursera', 'task',     1, 2, 'Run validation checks and flag errors'),
    ('Coursera', 'task',     1, 3, 'Reconcile data across systems'),
    ('Coursera', 'job_task', 1, 1, 'Profile a dataset and surface quality risks'),
    ('Coursera', 'job_task', 1, 2, 'Run validation checks and flag capture errors'),
    ('Coursera', 'job_task', 1, 3, 'Reconcile data across systems'),
]
TITLES = {(k, m, t): title for _, k, m, t, title in TASKS}

_ids = [(k, m, t) for _, k, m, t, _ in TASKS]
assert len(_ids) == len(set(_ids)), 'Cell IDs must be unique across programs: give the newcomer its own kind'

TASK_OUTPUT_FILES = {
    '1_1': 'dq_audit_report.md',
    '1_2': 'dq_validation_findings.md',
}

KINDS  = {'task': 'Task', 'job_task': 'Job Task'}

# comparison ..............................................................................................

WIDTHS = dict(task=12, action=10, a=39, b=39)   # preferred share, %
assert sum(WIDTHS.values()) == 100

COMPARISON = [   # (program, kind, module, task, action): keep each task's rows together
    ('Coursera', 'task',     1, 1, 'Data Profiling'),
    ('Coursera', 'task',     1, 1, 'Data Quality Tests'),
    ('Coursera', 'task',     1, 2, 'Data Profiling'),
    ('Coursera', 'task',     1, 2, 'Data Quality Tests'),
    ('Coursera', 'task',     1, 3, 'Data Reconciliation'),
    ('Coursera', 'job_task', 1, 1, 'Data Profiling'),
    ('Coursera', 'job_task', 1, 2, 'Data Profiling'),
    ('Coursera', 'job_task', 1, 2, 'Data Quality Tests'),
]

# guards: loud on purpose
_missing = {r[:4] for r in COMPARISON} - {r[:4] for r in TASKS}
assert not _missing, f'COMPARISON refers to tasks missing from TASKS: {sorted(_missing)}'

# code cells ..............................................................................................

CODE_HEADER = """
{anchors}
<div class="bn t-{track}">
<div class="bn-eb">Track {TRACK}{eyebrow_suffix}</div>
{task_title}

{report}

</div>
"""

# Data Profiling ..........................................................................................

PROFILE_RIGHT_COLS = ('Null', 'nNulls') if DEV.record_version else ('Core profile', 'Null', 'nNulls')

PROFILE_CLASS_ORDER    = ['num', 'cat']
PROFILE_SUBCLASS_ORDER = ['integer', 'float', 'date', 'low-cardinality', 'high-cardinality']

PROFILE_ANALYSIS_TEMPLATE = """
<br>

The Data Profiling reviewed **{total_records} customer records** on completeness and quality. 
{completeness_text} {outlier_text}
    """

PROFILE_ANALYSIS_HELP_TEMPLATE = """

`Core profile` boils down field information by class:  
 
* For **numerical** fields ({num_str}), it informs on central tendency and dispersion via core distribution
(min/max: q0/100, median: q50, interquartile ends: q25/75), average, and—for **non-date fields**—outliers range and count,
plus, in the Data Profiling v3+, a robust coefficient of variation [[1]](#ref-3).

* For **low-cardinality** fields ({low_cardin_str})—with up to {low_cardin_thresh} categories—
it breaks down the values count for each category, shedding light onto consistency, distribution, and balance.  

* For **high-cardinality** fields ({high_cardin_str}), the `Core profile` is given by uniqueness, 
as a measure of distinctiveness across entities and of identifier integrity. 
Primary identifiers (IDs) are expected to be 100% unique. Business identifiers may tolerate a limited % of reuse, e.g., 
phone number. There are also high-cardinality fields for which uniqueness is expected to be lower, like state. 

The `Core profile` supports anomaly detection such as out-of-bound values or invalid ages or dates.  
Numerical field distributions (in v3+) complement this.

<br>
    """

# Data Quality Tests ......................................................................................

AUDIT_ANALYSIS_TEMPLATE = """
<br>
    
**Data Quality validation checks** were performed against **{total_tests} rules**, assessing overall _accuracy_, 
_completeness_, and _plausibility_ of data according to defined domains. {class_context}   

Each test actively monitors critical quality risks, such as **entity integrity** for cross-table joins, 
**boundary constraints** for numerical metrics, and **structural validity** for categorical domains. 
Resolving these any failures found ensures that downstream summaries, segmentation models, 
and P&L calculations reflect true operational reality.

{status_str}

<br>
    """

# task 1.1 ................................................................................................

MIN_AGE =  18
MAX_AGE = 120

STATE_DOMAIN = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

TIER_DOMAIN = [
      'Bronze'
    , 'Silver'
    , 'Gold'
    , 'Platinum'
]

RULES_CONFIG = [
    {
          "key"       : "r01"
        , "dim"       : "Completeness"
        , "field"     : "customer_id"
        , "rule"      : "Non-nullable"
        , "relevance" : "Entity integrity is crucial for cross-table analyses (JOIN)."
        , "class"     : "NULL"
        , "noun"      : "NULL value"
        , "eval_fn"   : lambda df: df.loc[df['customer_id'].isna(), 'customer_id'].tolist()
        
    },
    {
          "key"       : "r02"
        , "dim"       : "Uniqueness"
        , "field"     : "customer_id"
        , "rule"      : "Index"
        , "relevance" : "Entity integrity is crucial for cross-table analyses (JOIN)."
        , "class"     : "Uniques"
        , "noun"      : "duplicate ID"
        , "eval_fn"   : lambda df: df[df['customer_id'].duplicated()]['customer_id'].tolist()
    },
    {
          "key"       : "r03"
        , "dim"       : "Validity"
        , "field"     : "age"
        , "rule"      : f"[{MIN_AGE}, {MAX_AGE}]"
        , "relevance" : ("Non-valid values can distort non-robust summarizing metrics, like"
                       " the mean.")
        , "class"     : "Range"
        , "noun"      : "out-of-range age"
        , "eval_fn"   : lambda df: df.loc[df['age'] < MIN_AGE, 'age'].tolist() + df.loc[df['age'] > MAX_AGE, 'age'].tolist()
    },
    {
          "key"       : "r04"
        , "dim"       : "Validity"
        , "field"     : "email"
        , "rule"      : 'Must have an "@"'
        , "relevance" : "Email without an @ is not directly actionable via machine."
        , "class"     : "String"
        , "noun"      : "invalid email"
        , "eval_fn"   : lambda df: df.loc[~df['email'].str.contains('@'), 'email'].tolist()
    },
    {
          "key"       : "r05"
        , "dim"       : "Validity"
        , "field"     : "state"
        , "rule"      : "Must be within domain"
        , "relevance" : "Valid category options are essential for accurate group reporting."
        , "class"     : "Domain"
        , "noun"      : "invalid state"
        , "eval_fn"   : lambda df: df.loc[~df['state'].isin(STATE_DOMAIN), 'state'].tolist()
    },
    {
          "key"       : "r06"
        , "dim"       : "Validity"
        , "field"     : "purchase_amount"
        , "rule"      : "Must be > 0"
        , "relevance" : "Non-negative purchases are required for P&L accuracy."
        , "class"     : "Non-negative"
        , "noun"      : "negative purchase"
        , "eval_fn"   : lambda df: df.loc[df['purchase_amount'] < 0, 'purchase_amount'].tolist()
    },
    {
          "key"       : "r07"
        , "dim"       : "Validity"
        , "field"     : "loyalty_tier"
        , "rule"      : "Must be within domain"
        , "relevance" : "Valid category options are essential for accurate group reporting."
        , "class"     : "Domain"
        , "noun"      : "invalid loyalty tier"
        , "eval_fn"   : lambda df: df.loc[~df['loyalty_tier'].isin(TIER_DOMAIN), 'loyalty_tier'].tolist()
    },
]
