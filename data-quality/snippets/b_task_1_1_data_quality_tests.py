# TRACK B • Task 1.1
# Your report must include:
# • A brief profile of the dataset using descriptive statistics or summary measures ✓
# • At least three distinct data quality issues found in customer_data ✓
# • A short explanation of how you detected each issue using evidence from the dataset ✓
# • A brief statement about why the identified issues matter for downstream analysis or reporting ✓

# config --------------------------------------------------------------------------------------------------

action = 'Data Quality Tests'
is_first_action = False


# Data Quality Tests --------------------------------------------------------------------------------------

dq_tests = []
failed_row_cnt = {}
failed_row_pct = {}
test_results   = {}
result_details = {}

for i, cfg in enumerate(RULES_CONFIG, start=1):
    
    k = cfg['key']
    bad_items = cfg['eval_fn'](df)
    cnt, msg  = get_dq_test_findings(bad_items, cfg['noun'])
    
    failed_row_cnt[k] = cnt
    result_details[k] = msg
    test_results  [k] = '✅ Passed' if cnt == 0 else '❌ Failed'
    failed_row_pct[k] = f'{failed_row_cnt[k] / len(df):.1%}'
    
    dq_tests.append({
            'ID'            : f"Rule {i:02d}"
          , 'Dimension'     : cfg['dim']
          , 'Field'         : cfg['field']
          , 'Rule'          : cfg['rule']
          , 'Test result'   : test_results  [k]
          , 'Rows affected' : failed_row_cnt[k]
          , '% Affected'    : failed_row_pct[k]
          , 'Details'       : result_details[k]
          , 'Relevance'     : cfg['relevance']
          , 'Test class'    : cfg['class']
          , 'Test code'     : get_eval_code(cfg['eval_fn'])
      })

dq_tests_df, dq_tests_report = get_dq_test_results(dq_tests)


# report -------------------------------------------------------------------------------------------------------

# build ...................................................................................................
dq_tests_table = style_table(dq_tests_df, track, index=True)

sections = [
      f'<div class="t-{track.lower()}">'
    , f"\n### {action}"
    , "`dq_tests`"
    , dq_tests_table
    , dq_tests_report
    , '</div>'
]

report_text = "\n\n".join(sections)

# display, save, and (in DEV_MODE) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV_MODE)
