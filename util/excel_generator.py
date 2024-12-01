import pandas as pd
import json

def generate_expense_report(user_id, start_date, end_date):
    file_path = f"user_{user_id}.json"
    try:
        with open(file_path, "r") as file:
            user_data = json.load(file)
    except FileNotFoundError:
        return "No data found for the user."

    outcomes = user_data["outcomes"]
    filtered_outcomes = [o for o in outcomes if start_date <= o["date"] <= end_date]

    if not filtered_outcomes:
        return "No expenses found in the given date range."

    df = pd.DataFrame(filtered_outcomes)
    excel_file = f"user_{user_id}_expenses_{start_date}_to_{end_date}.xlsx"
    df.to_excel(excel_file, index=False)

    return f"Report generated: {excel_file}"
