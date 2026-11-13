# TRACK A • Job Task 1.2

# Task:
# 1. Open and read the validation_rules.txt file. According to these rules, what is the required format for the ticket_id?
# 2. The validation_rules.txt file states that the priority field must be an integer between 1 and 5, inclusive. 
#    How many records in service_tickets.csv have a priority value that violates this rule?
# 3. The validation_rules.txt states that the agent_id field must not be empty. 
#    After checking service_tickets.csv, what is the outcome for this rule?
# 4. The validation_rules.txt specifies that the status column must only contain one of three values: 
#    'Open', 'In Progress', or 'Closed'. Your audit has found a fourth, non-compliant status in the dataset. 
#    What is this invalid status value?


# config --------------------------------------------------------------------------------------------------

action = 'Data Profiling'
is_first_action = True
show_title = False

track, kind, module, task = 'A', 'job_task', 1, 2
task_id, task_title, path_out = get_cell_meta(track, kind, module, task, PATH_OUT_REPORTS, show_title)


# profile • raw -------------------------------------------------------------------------------------------

profile_raw = use('get_data_profile', 3)(raw_data, track)


# report --------------------------------------------------------------------------------------------------

# build ...................................................................................................

profile_raw_sections = ["### Profile · Raw" , "`profile_raw`"] + profile_raw.sections(show_help=False)

sections = ([
      f'<div class="t-{track.lower()}">'
] 
+ profile_raw_sections
)

report_text = "\n\n".join(sections)

# display, save, and (if flag in ON) read from file .........................................................
finish_cell(task_id, task_title, action, report_text, track, is_first_action, path_out, DEV.render_md)
