# TRACK A • Job Task 2.1 • Analyze Missing Data

# Your code for visualizing missing data
# Create bar chart of missing values
# Optional: Create additional visualizations


# config --------------------------------------------------------------------------------------------------

action = 'None'
is_first_action = False
show_title = False

track, kind, module, task = 'A', 'job_task', 2, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# load ----------------------------------------------------------------------------------------------------

df = pd.read_csv(PATH_IN_FILES['jt_2_1_missing_data'])


# missing data --------------------------------------------------------------------------------------------

target_col = 'Gender'
rate_by_col_group, overall_missingness = get_missing_rates(df, target_col)

# observational insights ..................................................................................

t = THEMES[track.lower()]
observational_insights = f"""
<br>

In a lively read from these **synthetic data**:  
↳ <span style='color: {t['warn']};'>
People named Michael Williams, born in October 2005, who spend not a lot per transaction 
may not like to fill in their gender in forms.
</span>  
↳ <span style='color: {t['ok']};'>
People buying at Smith Group seem to be more than glad to tell their gender.
</span>
    """

# display -------------------------------------------------------------------------------------------------

render_missing_rates(target_col, rate_by_col_group, overall_missingness, observational_insights, track)
