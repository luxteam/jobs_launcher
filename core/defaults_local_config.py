tool_name = 'Renderer'
report_type = 'default'
show_skipped_groups = True
# --- Tracked metrics ---
# metrics should be configured by the following way -> 'name_of_metric_in_report': {'param1': 'value1'}
# Params:
# * metric_name (optional) - set other name for metric if it's necessary
# * displaying_name - name of metrich which is displayed on chart
# * function - specify how to calculate tracked metrics
# Existing functions:
#   * avrg - calculate averange value of some field
#   * sum - caulculate sum of some field
#   * match - calculate how many times values match pattern
# pattern (optional; use with match function) - pattern for match function
# displaying_unit (optional) - units of metric which is displayed on chart
# separation_field (optional) - specify name of field values from which are used for make a cartesian product with current metric
# (e.g., separation_field=tool; values of tool: rml, winml; metric_name=render_time; result: render_time_rml, render_time_winml)
# display_zeros (optional) - display zero values on chart (default - false)
tracked_metrics = {}
tracked_metrics_files_number = 10