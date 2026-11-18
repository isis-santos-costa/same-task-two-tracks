# TRACK A • Job Task 2.1 • Analyze Missing Data

# Your code for visualizing missing data
# Create bar chart of missing values
# Optional: Create additional visualizations


# config --------------------------------------------------------------------------------------------------

action = 'None'
is_first_action = True
show_title = True

track, kind, module, task = 'A', 'job_task', 2, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# load ----------------------------------------------------------------------------------------------------

df = pd.read_csv(PATH_IN_FILES['jt_2_1_missing_data'])


# profile • raw -------------------------------------------------------------------------------------------

profile_raw = use('get_data_profile', 3)(df, track)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................

raw_data_table = style_raw_table(df, track, sticky_first_col=True)

profile_raw_sections    =  ["### Profile · Raw" , "`profile_raw`"] + profile_raw.sections(show_help=False)

sections = [
      f'<div class="t-{track.lower()}">'
    , "`raw_data`"
    , raw_data_table
    , '<br>'
    , *profile_raw_sections
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
