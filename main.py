from src.report import generate_combined_report, generate_entity_reports, generate_reconciliation_report

# Generate individual reports for each entity
generate_entity_reports("31-08-2024")

# Generate a combined report for all entities
generate_combined_report("31-08-2024")

# Generate reconciliation report
ramp_report_path = "/Users/ahmetbesiroglu/Projects/ramp_aging_report/masterworks_administrative_services,_llc_open_bills_aging_report_as_of_31-08-2024.csv"
netsuite_report_path = "/Users/ahmetbesiroglu/Projects/ramp_aging_report/A_PAgingSummary18.xls"
output_path = "reconciliation_report.csv"

generate_reconciliation_report(ramp_report_path, netsuite_report_path, output_path)