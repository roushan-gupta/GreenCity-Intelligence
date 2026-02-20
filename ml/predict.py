# Prediction script
import joblib
import numpy as np
from datetime import datetime
import mysql.connector

model = joblib.load("ml/aqi_model.pkl")

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rs@969383",
        database="pollution_db"
    )

def predict_next_day():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(record_date) FROM aqi_readings")
    last_date = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT record_date)
        FROM aqi_readings
    """)
    total_days = cursor.fetchone()[0]

    conn.close()

    next_day_numeric = total_days + 1

    prediction = model.predict([[next_day_numeric]])

    return round(float(prediction[0]), 2)