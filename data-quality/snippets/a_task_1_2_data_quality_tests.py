# TRACK A • Task 1.2
# Your report must include:
# • A brief profile of the dataset using descriptive statistics or summary measures ✓
# • At least three distinct data quality issues found in customer_data ✓
# • A short explanation of how you detected each issue using evidence from the dataset ✓
# • A brief statement about why the identified issues matter for downstream analysis or reporting ✓

# config --------------------------------------------------------------------------------------------------

action = 'Data Quality Tests'
is_first_action = False
show_title = False

track, kind, module, task = 'A', 'task', 1, 2
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# Data Quality Tests --------------------------------------------------------------------------------------

tests = get_dq_tests(df, RULES_CONFIG, version=2)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................

tests_styled = style_table(
    build_dq_tests_labels(tests.table), 
    track,
    min_width='44rem', 
    max_height='360px',
    sticky_first_col=True,
    bold_first_col=True
)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`dq_tests`"
    , tests_styled
    , tests.legend
    , tests.report
    , tests.see_also
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
