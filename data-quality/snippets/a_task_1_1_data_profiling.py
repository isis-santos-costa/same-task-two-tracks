# TRACK A • Task 1.1
# Your report must include:
# • A brief profile of the dataset using descriptive statistics or summary measures ✓
# • At least three distinct data quality issues found in customer_data
# • A short explanation of how you detected each issue using evidence from the dataset
# • A brief statement about why the identified issues matter for downstream analysis or reporting


# config --------------------------------------------------------------------------------------------------

action = 'Data Profiling'
is_first_action = True


# Data Profiling ------------------------------------------------------------------------------------------

profiling_data, profiling_report = get_data_profiling(df)

profiling_df = profiling_data.rename(
    columns={
          'column_name'    : 'Column'
        , 'dtype'          : 'Data type'
        , 'field_class'    : 'Field class'
        , 'field_subclass' : 'Field subclass'
        , 'non_null_cnt'   : 'Non-nulls'
        , 'null_pct'       : '% Null'
        , 'details'        : 'Details'
    }
)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................
profiling_table = style_table(profiling_df, track, index=False)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`customer_data_profiling`"
    , profiling_table
    , profiling_report
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (in DEV_MODE) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV_MODE)
