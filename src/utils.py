from datetime import datetime, timedelta

def convert_to_iso8601(date_str):
    dt = datetime.strptime(date_str, "%d-%m-%Y")
    return dt.strftime("%Y-%m-%dT23:59:59Z")

def categorize_aging(row, cut_off_date):
    due_date = row['due_at']
    delta = (cut_off_date - due_date).days
    if delta < 0:
        return 'Current'
    elif delta < 30:
        return f'{(cut_off_date - timedelta(days=29)).strftime("%Y-%m-%d")} - {cut_off_date.strftime("%Y-%m-%d")} (30)'
    elif delta < 60:
        return f'{(cut_off_date - timedelta(days=59)).strftime("%Y-%m-%d")} - {(cut_off_date - timedelta(days=30)).strftime("%Y-%m-%d")} (60)'
    elif delta < 90:
        return f'{(cut_off_date - timedelta(days=89)).strftime("%Y-%m-%d")} - {(cut_off_date - timedelta(days=60)).strftime("%Y-%m-%d")} (90)'
    else:
        return f'Before {(cut_off_date - timedelta(days=90)).strftime("%Y-%m-%d")} (>90)'

def generate_column_names(cut_off_date):
    current_col = 'Current'
    col_30 = f'{(cut_off_date - timedelta(days=29)).strftime("%Y-%m-%d")} - {cut_off_date.strftime("%Y-%m-%d")} (30)'
    col_60 = f'{(cut_off_date - timedelta(days=59)).strftime("%Y-%m-%d")} - {(cut_off_date - timedelta(days=30)).strftime("%Y-%m-%d")} (60)'
    col_90 = f'{(cut_off_date - timedelta(days=89)).strftime("%Y-%m-%d")} - {(cut_off_date - timedelta(days=60)).strftime("%Y-%m-%d")} (90)'
    col_90_plus = f'Before {(cut_off_date - timedelta(days=90)).strftime("%Y-%m-%d")} (>90)'
    return ['Vendor Name', current_col, col_30, col_60, col_90, col_90_plus, 'Total']
