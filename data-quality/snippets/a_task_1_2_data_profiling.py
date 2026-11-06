# TRACK A • Task 1.2
# Your report must include:
# • A brief profile of the dataset using descriptive statistics or summary measures ✓
# • At least three distinct data quality issues found in customer_data
# • A short explanation of how you detected each issue using evidence from the dataset
# • A brief statement about why the identified issues matter for downstream analysis or reporting

# config --------------------------------------------------------------------------------------------------

action = 'Data Profiling'
is_first_action = True

track, kind, module, task = 'A', 'task', 1, 2
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS)


# initializing --------------------------------------------------------------------------------------------

df = pd.read_csv(PATH_IN_T_1_1_DATA)


# Data Profiling ------------------------------------------------------------------------------------------

profiling = use('get_data_profiling', 2)(df)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................
profiling_styled = style_table(
    profiling.table, 
    track,
    min_width='44rem', 
    max_height='360px',
    sticky_first_col=True,
    right_cols=('Core profile', 'Null', 'nNulls'),
)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`customer_data_profile`"
    , profiling_styled
    , profiling.legend
    , profiling.report
    , profiling.see_also
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
