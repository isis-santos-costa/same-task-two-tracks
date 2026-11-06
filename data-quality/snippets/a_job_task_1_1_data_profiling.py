# TRACK A • Job Task 1.1

# For an Airline dataset:
# → Calculate “Measure of Frequency” metrics (count, null count, null%, uniques, unique %, freq by cat for low-card)
# → Calculate “Measure of Central Tendency” metrics (mean & median)
# → Calculate “Measure of Dispersion” metrics (core distribution, variance, normalized std dev, coefficient of variation, range, spread)
# → Use in-built functions for additional data quality metrics
# → Create a custom function to calculate descriptive statistics on any given dataset
# → Transform data
# → Handle outliers and missing values

# Flights & Routes
# Flights: flight_id, date, airline, airplane_model, dep_time, time_take, stop, arr_time, price
# Routes: flight_id, from, to

# config --------------------------------------------------------------------------------------------------

action = 'Data Profiling'
is_first_action = True

track, kind, module, task = 'A', 'job_task', 1, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS)


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
