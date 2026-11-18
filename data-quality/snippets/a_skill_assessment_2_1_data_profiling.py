# TRACK A • Skill Assessment 2.1 • Profile a dataset and surface quality risks

# Output file: mean, median, N_missing

# config --------------------------------------------------------------------------------------------------

action = 'None'
is_first_action = False
show_title = False

track, kind, module, task = 'A', 'task', 2, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# load ----------------------------------------------------------------------------------------------------

raw_data_df = pd.read_csv(PATH_IN_FILES['sa_2_1_sales_performance'])


# profile • raw -------------------------------------------------------------------------------------------

profile_raw = use('get_data_profile', 3)(raw_data_df, track)


# profile • actual vs target ------------------------------------------------------------------------------

actual_vs_target = (raw_data_df['profit'] - raw_data_df['target_profit']).to_frame(name='actual_vs_target')
profile_actual_vs_target = use('get_data_profile', 3)(actual_vs_target, track)


# actual vs target ----------------------------------------------------------------------------------------

t_2_1_output = pd.DataFrame({
    'metric': ['mean', 'median', 'N_missing'],
    'value': [
        raw_data_df['profit'].mean(),
        raw_data_df['profit'].median(),
        raw_data_df['profit'].isna().sum()
    ]
})

t_2_1_output.to_csv(PATH_OUT_REPORTS['a_task_2_1'], index=False)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................

raw_data_table = style_raw_table(raw_data_df, track, sticky_first_col=True)

profile_raw_sections    =  ["### Profile · Raw" , "`profile_raw`"] + profile_raw.sections(show_help=False)
profile_a_vs_t_sections = (["### Profile · Actual vs Target" , "`profile_actual_vs_target`"] 
                        + profile_actual_vs_target.sections(show_help=False))

sections = [
      f'<div class="t-{track.lower()}">'
    , "\n### Skill Assessment 2.1: Profile a dataset and surface quality risk"
    , "`raw_data`"
    , raw_data_table
    , *profile_raw_sections
    , *profile_a_vs_t_sections
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
