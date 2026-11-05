# config.py -----------------------------------------------------------------------------------------------

# --- libraries: authored ---
from identity import TRACKS

# --- libraries: standard ---
from pathlib import Path

# overall .................................................................................................

LOW_CARDIN_THRESH = 10
CORE_DISTRIBUTION = [0, 0.25, 0.5, 0.75, 1]

reports = {}

PATH_SNIPPETS = Path('snippets')
OUTPUT_EXT    = 'png'

PROFILING_LEGEND = {'Null': 'null percentage', 'nNulls': 'non-null count', 'num': 'numerical',
                    'cat': 'categorical', 'dtype': 'data type'}

DQ_TESTS_LEGEND  = {'Affected': 'rows affected', '%': 'share of rows affected'}

# toc & comparison ........................................................................................

PROGRAMS = {   # key used in the registry -> (full name, link)
    'Coursera': ('Data Quality Specialization · Coursera',
                 'https://www.coursera.org/specializations/data-quality-analyst-validation-debugging-and-monitoring'),
    'DataKitchen': ('Data Observability and Data Quality Testing Certification · DataKitchen',
                    'https://datakitchen.io/certifications/data-observability-and-data-quality-testing/'),
}

MODULES = {
    ('Coursera', 1): 'Data Quality · Profiling & Tests'
}

TASKS = [   # (program, kind, module, task, title): the single source of truth, ordered by program, module
    ('Coursera', 'task',     1, 1, 'Profile a dataset and surface quality risks'),
    ('Coursera', 'task',     1, 2, 'Run validation checks and flag errors'),
    ('Coursera', 'task',     1, 3, 'Reconcile data across systems'),
    ('Coursera', 'job_task', 1, 1, 'Profile a dataset and surface quality risks'),
]
TITLES = {(k, m, t): title for _, k, m, t, title in TASKS}

# guards: loud on purpose
_ids = [(k, m, t) for _, k, m, t, _ in TASKS]
assert len(_ids) == len(set(_ids)), 'Cell IDs must be unique across programs: give the newcomer its own kind'

TASK_OUTPUT_FILES = {
    "1_1": "dq_audit_report.md",
    "1_2": "dq_validation_findings.md",
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
    ('Coursera', 'job_task', 1, 1, 'Data Quality Tests'),
]

# guards: loud on purpose
_missing = {r[:4] for r in COMPARISON} - {r[:4] for r in TASKS}
assert not _missing, f'COMPARISON refers to tasks missing from TASKS: {sorted(_missing)}'

# code cells ..............................................................................................

CODE_HEADER = """
{anchors}
<div class="bn t-{track}">
<div class="bn-eb">Track {TRACK}</div>
<h3>{task_title}</h3>

{report}

</div>
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
