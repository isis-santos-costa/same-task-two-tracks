# TRACK A • Task 1.3
# Ponder about the questions below.

# config --------------------------------------------------------------------------------------------------

action = 'Data Reconciliation'
is_first_action = True

track, kind, module, task = 'A', 'task', 1, 3
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS)

reconciliation_df = pd.DataFrame(
    data=[
        [  "Source System A", 42385],
        ["Warehouse Table A", 42127],
    ],
    columns=["System", "Record Count"],
)


# initializing --------------------------------------------------------------------------------------------

df = pd.read_csv(PATH_IN_T_1_1_DATA)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................
reconciliation_table = style_table(
    reconciliation_df, 
    track,
    min_width='44rem', 
    max_height='360px',
    sticky_first_col=True,
)

sections = [
      f'<div class="t-{track.lower()}">'
    , "\n#### Ponder about the questions below"
    , "<br>"
    , "**1. What can cause the situation in the table?**"
    , reconciliation_table
    , "<br>"
    , (
        "**2. What can be affirmed from the assertion below?**<br>"
        "« A reconciliation check compares total invoice counts between "
        "two systems and finds that the source has 8,215 records while "
        "the target has 8,215 records. »"
      )
    , "<br>"
    , (
        "**3. What can be concluded?**<br>"
        "« A source system contains 15,200 customer records. "
        "After loading to a reporting table, the target contains 15,200 records, "
        "but a spot check shows several customer IDs in the target do not match "
        "the corresponding IDs in the source. »"
      )
    , "<br>"
    , '</div>'
]

report_text = "\n\n".join(sections)


# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
