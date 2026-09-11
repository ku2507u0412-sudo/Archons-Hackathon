import sqlite3
import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# 1. Detect DB Path
db_path = "database/mine_data.db" if os.path.exists("database/mine_data.db") else "mine_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Ensure daily_production table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_production (
        log_id INTEGER PRIMARY KEY,
        date TEXT,
        planned_tonnage REAL,
        actual_tonnage REAL,
        rainfall_mm REAL,
        equipment_downtime_hours REAL
    )
''')

# 3. Auto-populate sample production data if empty
cursor.execute("SELECT COUNT(*) FROM daily_production")
if cursor.fetchone()[0] == 0:
    sample_prod = [
        (1, '2026-03-01', 5000.0, 4850.0, 0.0, 1.5),
        (2, '2026-03-02', 5000.0, 4920.0, 0.0, 0.5),
        (3, '2026-03-03', 5000.0, 4100.0, 12.5, 4.0),
        (4, '2026-03-04', 5000.0, 3200.0, 48.0, 6.5),
        (5, '2026-03-05', 5000.0, 3800.0, 5.0, 5.0)
    ]
    cursor.executemany('''
        INSERT INTO daily_production (log_id, date, planned_tonnage, actual_tonnage, rainfall_mm, equipment_downtime_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_prod)
    conn.commit()

# 4. Fetch data & compute shortfall % target
df_prod = pd.read_sql_query("SELECT planned_tonnage, actual_tonnage, rainfall_mm, equipment_downtime_hours FROM daily_production", conn)
conn.close()

df_prod['shortfall_percent'] = ((df_prod['planned_tonnage'] - df_prod['actual_tonnage']) / df_prod['planned_tonnage']) * 100

# 5. Train Regressor Model
X = df_prod[['rainfall_mm', 'equipment_downtime_hours']]
y = df_prod['shortfall_percent']

rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(X, y)

# 6. Save trained model to disk (.pkl file)
os.makedirs("models", exist_ok=True)
with open("models/shortfall_model.pkl", "wb") as f:
    pickle.dump(rf_regressor, f)

print("[✓] Production Shortfall Model Trained & Saved to 'models/shortfall_model.pkl'")