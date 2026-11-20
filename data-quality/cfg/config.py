# config.py -----------------------------------------------------------------------------------------------

# --- libraries: authored ---
from identity import TRACKS

# --- libraries: standard ---
import warnings
import pandas      as pd
from   pathlib     import Path
from   collections import Counter
from   dataclasses import dataclass

# development flags .......................................................................................

@dataclass
class DevFlags:
    max_rows                : int  = 200
    chart_dpi               : int  = 150
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

_LOADERS = {
    '.csv' : pd.read_csv,
    '.xlsx': pd.read_excel,
    '.xls' : pd.read_excel,
}

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

DQ = 'Data Quality'
C_LINK  = 'https://www.coursera.org/specializations/data-quality-analyst-validation-debugging-and-monitoring'
DK_LINK = 'https://datakitchen.io/certifications/data-observability-and-data-quality-testing/'

PROGRAMS = {   # key used in the Tracks comparison registry -> (full name, link)
    'Coursera'    : (f'{DQ} Specialization · Coursera', C_LINK),
    'DataKitchen' : (f'Data Observability and {DQ} Testing Certification · DataKitchen', DK_LINK),
}

_MODULES_TREE = {
    'Coursera': {
        1: 'Profiling & Tests',
        2: 'Validation & Debugging',
        3: 'Monitoring & Prevention',
    }
}

KINDS = {
    'task': 'Task', 
    'job_task': 'Job Task', 
    'skill_assessment': 'Skill Assessment'
}

DP   = 'Data Profiling'
DQ_T = f'{DQ} Tests'
DR   = 'Data Reconciliation'
MISS = 'Missing Data'
DIC  = 'Data Imputation (\u26a0\ufe0e use with caution)'
U    = 'Uniqueness'
ACTION_TYPES = (DP, DQ_T, DR, MISS, DIC, U)
NO_ACTION    = 'Just display'

_TASK_TREE = {
    ('Coursera', 1): {
        'task': [
            (1, 'Profile a dataset and surface quality risks', [DP, DQ_T]),
            (2, 'Run validation checks and flag errors',       [DP, DQ_T]),
            (3, 'Reconcile data across systems',               [DR]),
        ],
        'job_task': [
            (1, 'Profile a dataset and surface quality risks', [DP]),
            (2, 'Run validation checks and flag errors',       [DP, DQ_T]),
            (3, 'Reconcile data across systems',               [DR]),
        ],
    },
    ('Coursera', 2): {
        'skill_assessment': [
            (1, 'Profile a dataset and surface quality risks', [DP]),
        ],
        'job_task': [
            (1, 'Analyze missing data',                        [DP, MISS, DIC]),
            (2, 'Ensure data uniqueness',                      [DP, U]),
        ],
    },
}

TOOLS = {'a': 'pandas', 'b': 'dbt · SQL'}

MODULES = {
    (prog, num): f'{DQ} · {title}'
    for prog, modules in _MODULES_TREE.items()
    for num, title in modules.items()
}

TASKS = [
    (prog, kind, mod, task, title)
    for (prog, mod), kinds in _TASK_TREE.items()
    for kind, tasks        in kinds.items()
    for task, title, _     in tasks
]

def get_prog_acr(program):
    return 'cr' if program == 'Coursera' else 'dk'

TASK_IDS = [f'{get_prog_acr(p)}_{k[0]}_{m}_{t}' for p, k, m, t, _ in TASKS]

ACTIONS = {
    (prog, kind, mod, task): actions
    for (prog, mod), kinds in _TASK_TREE.items()
    for kind, tasks in kinds.items()
    for task, _, actions in tasks
}

TASK_TITLES = {(p, k, m, t): title for p, k, m, t, title in TASKS}

# --- files ---

INPUT_FILES = {  # id: filename (ids follow the task ids: program, kind, module, task)
    'cr_t_1_1'        : 'customer_data.csv',
    'cr_t_1_1_rules'  : 'dq_rules.txt',
    'cr_j_1_1_city'   : 'city_data.xlsx',
    'cr_j_1_1_retail' : 'retail_data.xlsx',
    'cr_j_1_1_inv'    : 'product_inventory.csv',
    'cr_j_1_2'        : 'service_tickets.csv',
    'cr_j_1_2_rules'  : 'service_tickets_rules.txt',
    'cr_j_1_3_source' : 'sales_source.csv',
    'cr_j_1_3_target' : 'sales_target.csv',
    'cr_s_2_1'        : 'sales_performance.csv',
    'cr_j_2_1'        : 'transactions_obt_w_missing_data.csv',
    'cr_j_2_2'        : 'sales_data.csv',
}

OUTPUT_FILES = {
    'cr_t_1_1' : 'dq_audit_report.md',
    'cr_t_1_2' : 'dq_validation_findings.md',
    'cr_j_2_1' : 'actual_vs_profit_data.csv',
}

# --- cell spec ---

@dataclass(frozen=True)
class CellSpec:
    track   : str
    program : str
    kind    : str
    module  : int
    task    : int
    action  : str = NO_ACTION

    def __post_init__(self):
        assert  self.track.lower()         in TRACKS  ,   f'Not in TRACKS registry:  {self.track}'
        assert  self.program               in PROGRAMS, f'Not in PROGRAMS registry:  {self.program}'
        assert  self.kind                  in KINDS   ,     f'Not in KIDS registry:  {self.kind}'
        assert (self.program, self.module) in MODULES ,  f'Not in MODULES registry: {(self.program, self.module)}'
        assert  self.key                   in ACTIONS ,  f'Not in ACTIONS registry:  {self.key}'
        assert  self.action in ACTION_TYPES or self.action == NO_ACTION, f'Unknown action: {self.action}'

    @property
    def key(self) -> tuple[str, str, int, int]:
        return (self.program, self.kind, self.module, self.task)

    @property
    def default_file_id(self) -> str:
        return f'{get_prog_acr(self.program)}_{self.kind[0]}_{self.module}_{self.task}'

    def file_id(self, suffix: str = '') -> str:
        return f'{self.default_file_id}_{suffix}' if suffix else self.default_file_id    

    @property
    def is_first_action_in_task(self) -> bool:
        task_actions = ACTIONS.get(self.key, [])
        return bool(task_actions) and self.action == task_actions[0]

# --- integrity assertions: uniqueness ---

_ids = [(k, m, t) for _, k, m, t, _ in TASKS]
assert len(_ids) == len(set(_ids)), (
    'Cell IDs must be unique across programs: give the newcomer its own kind')

assert len(KINDS) == len({k[0] for k in KINDS}), 'KINDS keys must have unique first letters'

assert len(TASK_IDS) == len(set(TASK_IDS)), f'Duplicate TASK_IDS found: {[k for k, v in Counter(TASK_IDS).items() if v > 1]}'

# --- integrity assertions: referential ---

missing_programs = {prog for prog, _ in MODULES} - PROGRAMS.keys()
assert not missing_programs, f'Programs in MODULES not in the PROGRAMS registry: {missing_programs}'

missing_programs = {prog for prog, *_ in TASKS} - PROGRAMS.keys()
assert not missing_programs, f'Programs in TASKS not in the PROGRAMS registry: {missing_programs}'

missing_modules = {(prog, mod) for prog, _, mod, _, _ in TASKS} - MODULES.keys()
assert not missing_modules, f'(Program, module) pairs in TASKS not listed in the MODULES registry: {missing_modules}'

missing_input_id = [tid[0:8] for tid in INPUT_FILES if tid[0:8] not in TASK_IDS]
assert missing_input_id == [], f'Not in TASK_IDS registry: {missing_input_id}'

missing_output_id = [tid[0:8] for tid in OUTPUT_FILES if tid[0:8] not in TASK_IDS]
assert missing_output_id == [], f'Not in TASK_IDS registry: {missing_output_id}'

# comparison ..............................................................................................

WIDTHS = dict(task=12, action=10, a=39, b=39)   # preferred share, %
assert sum(WIDTHS.values()) == 100

COMPARISON = [
    (prog, kind, mod, task, action)
    for prog, kind, mod, task, _ in TASKS
    for action in ACTIONS[(prog, kind, mod, task)]
]

# --- integrity assertions: referential ---

valid_actions = set(ACTION_TYPES)
bad_actions = {a for acts in ACTIONS.values() for a in acts} - valid_actions
assert not bad_actions, f'Unregistered ACTION_TYPES used in ACTIONS: {bad_actions}'

bad_kinds = {kind for _, kind, _, _, _ in TASKS} - KINDS.keys()
assert not bad_kinds, f'Unregistered KINDS used in TASKS: {bad_kinds}'

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

PROFILE_FMT = {'Null': '{:.1%}', 'nNulls': '{:,}'}
PROFILE_RIGHT_COLS = ('Null', 'nNulls') if DEV.record_version else ('Core profile', 'Null', 'nNulls')

PROFILE_CLASS_ORDER    = ['num', 'cat']
PROFILE_SUBCLASS_ORDER = ['integer', 'float', 'date', 'low-cardinality', 'high-cardinality']

PROFILE_ANALYSIS_TEMPLATE = """
<br>

The Data Profiling reviewed **{total_records:,} customer records** on completeness and quality. 
{completeness_text} {outlier_text} {date_assessment}
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

# --- task 1.1 ---

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
        , "class"     : "UNIQUE"
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
        , "class"     : "RANGE"
        , "noun"      : "out-of-range age"
        , "eval_fn"   : lambda df: df.loc[df['age'] < MIN_AGE, 'age'].tolist() + df.loc[df['age'] > MAX_AGE, 'age'].tolist()
    },
    {
          "key"       : "r04"
        , "dim"       : "Validity"
        , "field"     : "email"
        , "rule"      : 'Must have an "@"'
        , "relevance" : "Email without an @ is not directly actionable via machine."
        , "class"     : "FORMAT"
        , "noun"      : "invalid email"
        , "eval_fn"   : lambda df: df.loc[~df['email'].str.contains('@', na=False), 'email'].tolist()
    },
    {
          "key"       : "r05"
        , "dim"       : "Validity"
        , "field"     : "state"
        , "rule"      : "Must be within domain"
        , "relevance" : "Valid category options are essential for accurate group reporting."
        , "class"     : "DOMAIN"
        , "noun"      : "invalid state"
        , "eval_fn"   : lambda df: df.loc[~df['state'].isin(STATE_DOMAIN), 'state'].tolist()
    },
    {
          "key"       : "r06"
        , "dim"       : "Validity"
        , "field"     : "purchase_amount"
        , "rule"      : "Must be ≥ 0"
        , "relevance" : "Non-negative purchases are required for P&L accuracy."
        , "class"     : "RANGE"
        , "noun"      : "negative purchase"
        , "eval_fn"   : lambda df: df.loc[df['purchase_amount'] < 0, 'purchase_amount'].tolist()
    },
    {
          "key"       : "r07"
        , "dim"       : "Validity"
        , "field"     : "loyalty_tier"
        , "rule"      : "Must be within domain"
        , "relevance" : "Valid category options are essential for accurate group reporting."
        , "class"     : "DOMAIN"
        , "noun"      : "invalid loyalty tier"
        , "eval_fn"   : lambda df: df.loc[~df['loyalty_tier'].isin(TIER_DOMAIN), 'loyalty_tier'].tolist()
    },
]

# --- job task 1.2 ---

RULES_CONFIG_SERVICE_TICKETS = [
    {
          'key'       : 'r01'
        , 'dim'       : 'Validity'
        , 'field'     : 'ticket_id'
        , 'rule'      : 'Must start with "T-" followed by four digits (e.g., T-1234).'
        , 'relevance' : 'Valid IDs are crucial for cross-table analyses (JOIN).'
        , 'class'     : 'FORMAT'
        , 'noun'      : 'invalid ticket_id'
        , 'eval_fn'   : lambda df: df.loc[~df['ticket_id'].str.contains(r'^T-\d{4}$', regex=True, na=False), 'ticket_id'].tolist()
        
    },
    {
          'key'       : 'r02'
        , 'dim'       : 'Validity'
        , 'field'     : 'priority'
        , 'rule'      : 'Must be integer [1, 5]'
        , 'relevance' : 'Valid category options are essential for accurate group reporting.'
        , 'class'     : 'RANGE'
        , 'noun'      : 'invalid priority value'
        , 'eval_fn'   : lambda df: df.loc[~(lambda s: s.between(1, 5) & (s % 1 == 0))(pd.to_numeric(df['priority'], errors='coerce')), 'priority'].tolist()
    },
    {
          'key'       : 'r03'
        , 'dim'       : 'Validity'
        , 'field'     : 'status'
        , 'rule'      : 'Is one of "Open", "In Progress", "Closed"'
        , 'relevance' : 'Valid category options are essential for accurate group reporting.'
        , 'class'     : 'DOMAIN'
        , 'noun'      : 'invalid status value'
        , 'eval_fn'   : lambda df: df.loc[~df['status'].isin(['Open', 'In Progress', 'Closed']), 'status'].tolist()
    },
    {
          'key'       : 'r04'
        , 'dim'       : 'Completeness'
        , 'field'     : 'agent_id'
        , 'rule'      : 'Non-nullable'
        , 'relevance' : 'Tickets with NULL agent_id would keep open and unassigned.'
        , 'class'     : 'NULL'
        , 'noun'      : 'null agent_id'
        , 'eval_fn'   : lambda df: df.loc[df['agent_id'].isna(), 'agent_id'].tolist()
    },
]

# --- assertions ---

DQ_TESTS_CLASSES = {'NULL', 'UNIQUE', 'RANGE', 'DOMAIN', 'FORMAT'}

for _rules in (RULES_CONFIG, RULES_CONFIG_SERVICE_TICKETS):
    _bad = {r['class'] for r in _rules} - DQ_TESTS_CLASSES
    assert not _bad, f'Unregistered rule classes: {_bad}'
