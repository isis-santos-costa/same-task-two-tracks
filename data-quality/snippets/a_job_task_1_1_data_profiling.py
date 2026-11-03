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


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................
profiling_table = style_table(profiling_df, track, index=False)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`airline_data_profiling`"
    , profiling_table
    , profiling_report
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (in DEV_MODE) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV_MODE)
