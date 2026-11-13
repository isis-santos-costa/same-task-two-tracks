# TRACK A • Job Task 1.1

# Data Profiling
# 1. After loading product_inventory.csv, what is the mean (average) of the stock_quantity column? Round to one decimal point. ✓
# 2. Which product category has the highest frequency (i.e., is the mode) in the dataset? ✓
# 3. Select ALL of the data quality issues that are present in this dataset. ✓
#    ☑ The date_added column has inconsistent date formats.
#    ☐ All values in the stock_quantity column are missing (null).
#    ☑ The price column contains negative values.
#    ☑ The product_id column contains duplicate values. 
# 4. For the issues you found, it's important to explain how you found them and what their business impact is. ✓


# config --------------------------------------------------------------------------------------------------

action = 'None'
is_first_action = True
show_title = True

track, kind, module, task = 'A', 'job_task', 1, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# profile • raw -------------------------------------------------------------------------------------------

profile_raw = use('get_data_profile', 3)(raw_inventory_df, track)


# processed • dates, negative price, profile --------------------------------------------------------------

processed_inventory_df = get_iso_date(raw_inventory_df.copy(), 'date_added')
processed_inventory_df = processed_inventory_df.loc[~(processed_inventory_df['price'] < 0), :]
profile_processed      = use('get_data_profile', 3)(processed_inventory_df, track)


# price mean ----------------------------------------------------------------------------------------------

raw_s  =       raw_inventory_df['stock_quantity']
proc_s = processed_inventory_df['stock_quantity']

(
    stock_quantity_mean_raw, 
    stock_quantity_mean_processed, 
    stock_quantity_mean_pct_diff
) = get_metric_shift(raw_s, proc_s, lambda s: s.mean())


# observational insights ----------------------------------------------------------------------------------

observational_insights = f"""
<hr>
\n ### Observational Insights

<br>

The profile for the raw table reveals some data quality issues:
* The date format is mixed
* There is a negative price
* There is a repeated product ID

The repeated ID happens for the entity with negative price. 
Processed data standardizes date as ISO and removes this entity.

This is how the processing reviews values for the `stock_quantity`:
* Raw:          {stock_quantity_mean_raw       :,.2f}  
* Processed:    {stock_quantity_mean_processed :,.2f}  
* % Difference: {stock_quantity_mean_pct_diff  :+,.0%}  

The date fix ensures correct sorting and aggregation.
Eliminating duplicate items is important for all metrics.

<hr>
"""


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................

profile_raw_sections       = ["### Profile · Raw" , "`profile_raw`"] + profile_raw.sections(show_help=True)
profile_processed_sections = ["### Profile · Processed", "`profile_processed`"] + profile_processed.sections()

sections = [
      f'<div class="t-{track.lower()}">'
    , *profile_raw_sections
    , observational_insights
    , *profile_processed_sections
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
