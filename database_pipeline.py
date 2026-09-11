import sqlite3
import pandas as pd
from datetime import datetime


DB_PATH = "database/mine_data.db"
conn = sqlite3.connect(DB_PATH)

print("[✓] Connected to SQLite Database successfully.")


query = "SELECT log_id, date, planned_tonnage, actual_tonnage, rainfall_mm, equipment_downtime_hours FROM daily_production"
df_production = pd.read_sql_query(query, conn)

print("\n--- Fetched Daily Production Logs ---")
print(df_production.head(5))


# Shortfall % = ((Planned - Actual) / Planned) * 100
df_production['predicted_shortfall_percent'] = (
    (df_production['planned_tonnage'] - df_production['actual_tonnage']) / df_production['planned_tonnage']
) * 100

# Classify risk levels based on predicted shortfall thresholds
def assign_risk(shortfall):
    if shortfall >= 30.0:
        return 'HIGH'
    elif shortfall >= 15.0:
        return 'MEDIUM'
    return 'LOW'

df_production['risk_level'] = df_production['predicted_shortfall_percent'].apply(assign_risk)


cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS shortfall_predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        forecast_date TEXT,
        predicted_shortfall_percent REAL,
        risk_level TEXT
    )
''')


for index, row in df_production.iterrows():
    cursor.execute('''
        INSERT INTO shortfall_predictions (forecast_date, predicted_shortfall_percent, risk_level)
        VALUES (?, ?, ?)
    ''', (row['date'], round(row['predicted_shortfall_percent'], 2), row['risk_level']))


conn.commit()
print(f"\n[✓] Successfully inserted {len(df_production)} predictions into 'shortfall_predictions' table.")

conn.close()
print("[✓] Database connection closed safely.")