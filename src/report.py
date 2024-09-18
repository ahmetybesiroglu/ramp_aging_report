import pandas as pd
from .utils import convert_to_iso8601, categorize_aging, generate_column_names
from .api import get_ramp_api_token, get_entities, get_bills
from datetime import datetime

def filter_open_as_of(df, cut_off_date):
    """
    Filters bills that were still open as of the specified cutoff date.
    If a bill has a paid_at date after the cutoff, it's considered open as of that date.
    """
    # Convert 'paid_at' to datetime, if it exists
    df['paid_at'] = pd.to_datetime(df['paid_at'], errors='coerce').dt.tz_localize(None)

    # A bill is considered open if it was not paid or was paid after the cutoff date
    open_as_of_cutoff = (df['paid_at'].isna()) | (df['paid_at'] > cut_off_date)

    # Filter bills that were open as of the cutoff date
    return df.loc[open_as_of_cutoff].copy()  # Use .loc[] and .copy() to avoid the warning

def generate_entity_reports(specified_date):
    """
    Generates aging reports for each individual entity and saves them as CSV files.
    Additionally, saves the raw bills data for each entity.
    """
    # Get the API access token
    access_token = get_ramp_api_token()

    # Convert the user-friendly specified date to ISO 8601 format
    cut_off_date_iso8601 = convert_to_iso8601(specified_date)
    cut_off_date = datetime.strptime(cut_off_date_iso8601, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=None)

    # Fetch all entities
    entities = get_entities(access_token)

    # Loop through each entity and generate the individual report
    for entity in entities:
        entity_id = entity['id']
        entity_name = entity['entity_name']

        # Get bills for the entity (fetches all, no payment status filter)
        bills_data = get_bills(access_token, entity_id, cut_off_date_iso8601)

        if bills_data:
            # Load the bills data into a DataFrame
            df = pd.DataFrame(bills_data)

            # Ensure due_at and issued_at are in the correct datetime format
            df['due_at'] = pd.to_datetime(df['due_at']).dt.tz_localize(None)
            df['issued_at'] = pd.to_datetime(df['issued_at']).dt.tz_localize(None)

            # Extract amount and vendor information
            df['amount'] = df['amount'].apply(lambda x: x['amount'] if isinstance(x, dict) else x)
            df['vendor_name'] = df['vendor'].apply(lambda x: x['remote_name'] if isinstance(x, dict) else x)

            # Filter for bills that were still open as of the cutoff date
            df_open = filter_open_as_of(df, cut_off_date)

            if df_open.empty:
                print(f"No bills were open as of {specified_date} for entity {entity_name}")
                continue

            # Apply categorization based on the cutoff date
            df_open['aging_bucket'] = df_open.apply(lambda row: categorize_aging(row, cut_off_date), axis=1)

            # Group by vendor and aging bucket, and sum the amounts
            aging_report = df_open.groupby(['vendor_name', 'aging_bucket']).agg({'amount': 'sum'}).unstack(fill_value=0).reset_index()

            # Flatten the column multi-index
            aging_report.columns = ['Vendor Name'] + [f'{col[1]}' for col in aging_report.columns[1:]]

            # Calculate the total for each vendor
            aging_report['Total'] = aging_report.iloc[:, 1:].sum(axis=1)

            # Generate dynamic column names based on the cutoff date
            sorted_columns = generate_column_names(cut_off_date)

            # Ensure the columns are ordered as specified
            aging_report = aging_report.reindex(columns=sorted_columns, fill_value=0)

            # Create a new column for sorting in the aging report
            aging_report['Vendor Name Sort'] = aging_report['Vendor Name'].str.strip().str.lower()

            # Sort rows by the new sorting column and drop it afterwards
            aging_report = aging_report.sort_values(by='Vendor Name Sort').drop(columns=['Vendor Name Sort'])

            # Calculate the sum for each column to get the totals
            totals_row = pd.DataFrame(aging_report.iloc[:, 1:].sum(axis=0)).T
            totals_row['Vendor Name'] = 'Total'

            # Append the totals row to the aging report using pd.concat
            aging_report = pd.concat([aging_report, totals_row], ignore_index=True)

            # Save the aging report as a CSV file for this entity
            filename = f'{entity_name.replace(" ", "_").lower()}_open_bills_aging_report_as_of_{specified_date}.csv'
            aging_report.to_csv(filename, index=False)

            print(f"Aging report generated for entity: {entity_name}")
        else:
            print(f"No bills data for entity {entity_name}")

def generate_combined_report(specified_date):
    """
    Generates a combined aging report for all entities and saves it as a single CSV file.
    Additionally, saves the combined raw bills data for later analysis.
    """
    # Get the API access token
    access_token = get_ramp_api_token()

    # Convert the user-friendly specified date to ISO 8601 format
    cut_off_date_iso8601 = convert_to_iso8601(specified_date)
    cut_off_date = datetime.strptime(cut_off_date_iso8601, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=None)

    # Fetch all entities
    entities = get_entities(access_token)

    # Create an empty DataFrame to store combined data
    combined_bills_data = pd.DataFrame()

    # Loop through each entity and fetch its bills
    for entity in entities:
        entity_id = entity['id']
        entity_name = entity['entity_name']

        # Get bills for the entity (fetches all, no payment status filter)
        bills_data = get_bills(access_token, entity_id, cut_off_date_iso8601)

        if bills_data:
            # Load the bills data into a DataFrame
            df = pd.DataFrame(bills_data)

            # Ensure due_at and issued_at are in the correct datetime format
            df['due_at'] = pd.to_datetime(df['due_at']).dt.tz_localize(None)
            df['issued_at'] = pd.to_datetime(df['issued_at']).dt.tz_localize(None)

            # Extract amount and vendor information
            df['amount'] = df['amount'].apply(lambda x: x['amount'] if isinstance(x, dict) else x)
            df['vendor_name'] = df['vendor'].apply(lambda x: x['remote_name'] if isinstance(x, dict) else x)

            # Filter for bills that were still open as of the cutoff date
            df_open = filter_open_as_of(df, cut_off_date)

            # Add the filtered DataFrame to the combined DataFrame
            combined_bills_data = pd.concat([combined_bills_data, df_open], ignore_index=True)

    # If no bills data was retrieved, exit early
    if combined_bills_data.empty:
        print("No bills data was retrieved from any entity.")
        return

    # Apply categorization based on the cutoff date
    combined_bills_data['aging_bucket'] = combined_bills_data.apply(lambda row: categorize_aging(row, cut_off_date), axis=1)

    # Group by vendor and aging bucket, and sum the amounts
    aging_report = combined_bills_data.groupby(['vendor_name', 'aging_bucket']).agg({'amount': 'sum'}).unstack(fill_value=0).reset_index()

    # Flatten the column multi-index
    aging_report.columns = ['Vendor Name'] + [f'{col[1]}' for col in aging_report.columns[1:]]

    # Calculate the total for each vendor
    aging_report['Total'] = aging_report.iloc[:, 1:].sum(axis=1)

    # Generate dynamic column names based on the cutoff date
    sorted_columns = generate_column_names(cut_off_date)

    # Ensure the columns are ordered as specified
    aging_report = aging_report.reindex(columns=sorted_columns, fill_value=0)

    # Create a new column for sorting in the aging report
    aging_report['Vendor Name Sort'] = aging_report['Vendor Name'].str.strip().str.lower()

    # Sort rows by the new sorting column and drop it afterwards
    aging_report = aging_report.sort_values(by='Vendor Name Sort').drop(columns=['Vendor Name Sort'])

    # Calculate the sum for each column to get the totals
    totals_row = pd.DataFrame(aging_report.iloc[:, 1:].sum(axis=0)).T
    totals_row['Vendor Name'] = 'Total'

    # Append the totals row to the aging report using pd.concat
    aging_report = pd.concat([aging_report, totals_row], ignore_index=True)

    # Save the combined aging report as a CSV file
    filename = f'combined_open_bills_aging_report_as_of_{specified_date}.csv'
    aging_report.to_csv(filename, index=False)

    # Print the aging report
    print(f"Combined aging report as of {specified_date}:")
    print(aging_report)
