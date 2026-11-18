# TRACK A • Job Task 1.3

# config --------------------------------------------------------------------------------------------------

action = 'Data Reconciliation'
is_first_action = True
show_title = True

track, kind, module, task = 'A', 'job_task', 1, 3
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)

reconciliation_df = pd.DataFrame(
    data=[
        [  "Source System A", 42385],
        ["Warehouse Table A", 42127],
    ],
    columns=["System", "Record Count"],
)


# load ----------------------------------------------------------------------------------------------------

source_df = pd.read_csv(PATH_IN_FILES['jt_1_3_sales_source'])
target_df = pd.read_csv(PATH_IN_FILES['jt_1_3_sales_target'])


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................

source_table = style_raw_table(source_df, track, sticky_first_col=True)
target_table = style_raw_table(target_df, track, sticky_first_col=True)

result = reconcile_tables(source_df, target_df)
reconciliation_report = build_reconciliation_report(result, track)

report_sections = [
      "### Reconciliation report"
    , f'<div class="t-{track.lower()} card">'
    , reconciliation_report
]

sections = [
      f'<div class="t-{track.lower()}">'
    , "### Data reconciliation"
    , "`target_table`"
    , target_table
    , "`source_table`"
    , source_table
    , '<br>'
    , *report_sections
    , '</div>'
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
