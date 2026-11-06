# TRACK A • Task 1.2
# Your report must include:
# • A brief profile of the dataset using descriptive statistics or summary measures ✓
# • At least three distinct data quality issues found in customer_data ✓
# • A short explanation of how you detected each issue using evidence from the dataset ✓
# • A brief statement about why the identified issues matter for downstream analysis or reporting ✓

# config --------------------------------------------------------------------------------------------------

action = 'Data Quality Tests'
is_first_action = False

track, kind, module, task = 'A', 'task', 1, 2
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS)


# Data Quality Tests --------------------------------------------------------------------------------------

dq_tests_data = get_dq_test_data(df, RULES_CONFIG)
dq_tests_df, dq_tests_legend, dq_tests_report = get_dq_test_results(dq_tests_data)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................
dq_tests_table = style_table(
    build_dq_tests_labels(dq_tests_df), 
    track,
    min_width='44rem', 
    max_height='360px',
    sticky_first_col=True,
    bold_first_col=True,
)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`dq_tests`"
    , dq_tests_table
    , dq_tests_legend
    , dq_tests_report
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
