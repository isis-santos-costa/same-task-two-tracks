# TRACK A • Task 1.1
# Your report must include:
# • A brief profile of the dataset using descriptive statistics or summary measures ✓
# • At least three distinct data quality issues found in customer_data
# • A short explanation of how you detected each issue using evidence from the dataset
# • A brief statement about why the identified issues matter for downstream analysis or reporting


# config --------------------------------------------------------------------------------------------------

action = 'Data Profiling'
is_first_action = True
show_title = False

track, kind, module, task = 'A', 'task', 1, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# Data Profiling ------------------------------------------------------------------------------------------

profile = use('get_data_profile', 1)(df)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................
profile_styled = style_table(
    profile.table, 
    track,
    min_width='44rem', 
    max_height='360px',
    sticky_first_col=True,
    right_cols=('Mean', 'Median', 'Min', 'Max'),
)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`customer_data_profile`"
    , profile_styled
    , profile.legend
    , profile.see_also
    , profile.report
    , profile.report_help
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
