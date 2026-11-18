# TRACK A • Job Task 2.1 • Analyze Missing Data

# Your code for visualizing missing data
# Create bar chart of missing values
# Optional: Create additional visualizations


# config --------------------------------------------------------------------------------------------------

action = 'None'
is_first_action = False
show_title = True

track, kind, module, task = 'A', 'job_task', 2, 1
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# load ----------------------------------------------------------------------------------------------------

df = pd.read_csv(PATH_IN_FILES['jt_2_1_missing_data'])


# data imputation (⚠ use with caution) --------------------------------------------------------------------

target = 'Gender'

dist_df, overall = get_missing_col_distribution_by_other_cols_group(df, target)

groups_df = dist_df[dist_df['column'] != 'OVERALL']
top_row   = groups_df.iloc[0]
group_col = top_row['column'] if top_row['max_group_gap'] >= 0.05 else None

df_imputed = impute_by_group_dist(df, target, dist_df, group_col=group_col)

df_mode = df.copy()
df_mode[target] = df_mode[target].fillna(df_mode[target].mode()[0])

raw_dist  =         df[target].value_counts(normalize=True)
prop_dist = df_imputed[target].value_counts(normalize=True)
mode_dist =    df_mode[target].value_counts(normalize=True)

raw_miss_cnt       =         df[target].isna().sum()
remaining_miss_cnt = df_imputed[target].isna().sum()

min_effect = 0.03

imputation_summary_table = build_imputation_summary_table(raw_dist, prop_dist, mode_dist, min_effect=min_effect)
imputation_proportional  = render_imputation_before_after(df, df_imputed, target, track, group_col=group_col)
imputation_naive         = render_imputation_before_after(df, df_mode   , target, track, group_col=group_col)

audit_df, cat_cols = build_full_imputation_audit(df, df_imputed, df_mode, target)

fmt = {'n (before)': '{:,.0f}', 'n (after)': '{:,.0f}', 'imputation_drift': '{:.2%}', 'naive_imputation_drift': '{:.2%}'}
for c in cat_cols:
    fmt[f'{c} (before)'] = '{:.1%}'
    fmt[f'{c} (after)']  = '{:.1%}'
audit_table = style_table(
    audit_df,
    track,
    caption=f"Full cross-column imputation distribution audit · {target}",
    formats=fmt,
    cell_styles={'naive_imputation_drift': make_lift_style(track, min_effect=0.03)},
    max_height='420px',
)

fmt = {'n': '{:,}', 'F': '{:.1%}', 'M': '{:.1%}'}
dist_table = style_table(
    dist_df,
    track,
    caption=f"Pre-imputation distributions · {target}",
    formats=fmt,
    row_styles=[make_lift_row_style(track, min_effect=0.03, col='max_group_gap')],
    max_height='420px',
    right_cols=['dominant_gap'],
    hide_cols=['max_group_gap']
)

max_group_shift = top_row['max_group_gap']

# imputation report .......................................................................................

cats       = raw_dist.index
prop_drift = float((prop_dist.reindex(cats, fill_value=0) - raw_dist).abs().max())
mode_drift = float((mode_dist.reindex(cats, fill_value=0) - raw_dist).abs().max())

kpis = build_kpi_strip([
    ('Remaining missing',                f'{remaining_miss_cnt:,}', f'from {raw_miss_cnt:,}'),
    ('Max overall drift · proportional', f'{prop_drift:.2%}',       'vs observed'),
    ('Max overall drift · mode',         f'{mode_drift:.2%}',       'vs observed'),
])

imputation_report = f"""
<div class='t-{track.lower()} card'>

<div class='hd'>Data Imputation <small>⚠ use with caution</small></div><br>

<div class='qa'>
<b>Question for you</b><span><span style='font-size:26px;'>👉</span> &nbsp;
What are your thoughts on data imputation?</span></div><br>

<div class='qa'><b>My take</b><span>This was part of the course syllabus. 
I'd mostly avoid it, exclude it from analyses, and use it only to meet legacy non-null enforcement, 
flagged with <code>is_&lt;column&gt;_imputed</code>.</span></div><br>

<div class='sh'>Proportional <em>vs.</em> mode method</div>

<div class='note'>
Proportional to <code>Merchant Name</code> · largest group gap before imputation ({100*max_group_shift:.1f} pp)
</div>

{kpis}

{imputation_summary_table}

<div class='sh'>Proportional method · before <em>vs.</em> after</div>

{imputation_proportional}

<div class='sh'>Naive method (mode) · before <em>vs.</em> after</div>

{imputation_naive}

{audit_table}

<br>{SMOOTH_HR}

<div class='sh'>Proportional method breakdown · Conditioner selection</div>
<div class='note'><strong>Dominant gap</strong>:
largest category shift (in pp) between a group and the overall value</div>

{dist_table}

</div>
"""

# display -------------------------------------------------------------------------------------------------

display_markdown(imputation_report, raw=True)
