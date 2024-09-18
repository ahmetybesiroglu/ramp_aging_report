from src.report import generate_combined_report
from src.report import generate_entity_reports

# Generate individual reports for each entity
generate_entity_reports("31-08-2024")

# Generate a combined report for all entities
generate_combined_report("31-08-2024")
