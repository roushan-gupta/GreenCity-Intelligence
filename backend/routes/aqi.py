from flask import Blueprint, jsonify, request
from db import get_db_connection
from ml.predict import predict_next_day

aqi_bp = Blueprint("aqi", __name__)

def get_aqi_category(aqi):
    if aqi <= 50:
        return {
            "category": "Good",
            "color": "Green",
            "health_message": "Air quality is good. Enjoy outdoor activities."
        }
    elif aqi <= 100:
        return {
            "category": "Satisfactory",
            "color": "Light Green",
            "health_message": "Minor breathing discomfort to sensitive people."
        }
    elif aqi <= 200:
        return {
            "category": "Moderate",
            "color": "Yellow",
            "health_message": "Breathing discomfort to people with lung disease."
        }
    elif aqi <= 300:
        return {
            "category": "Poor",
            "color": "Orange",
            "health_message": "Breathing discomfort to most people on prolonged exposure."
        }
    elif aqi <= 400:
        return {
            "category": "Very Poor",
            "color": "Red",
            "health_message": "Respiratory illness on prolonged exposure."
        }
    else:
        return {
            "category": "Severe",
            "color": "Dark Red",
            "health_message": "Serious health impacts. Avoid outdoor activities."
        }

@aqi_bp.route("/aqi", methods=["GET"])

def get_aqi():
    location_id = request.args.get("location_id")

    if not location_id:
        return jsonify({"message": "location_id is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT l.name, a.pm25, a.pm10, a.aqi, a.recorded_at
        FROM aqi_readings a
        JOIN locations l ON a.location_id = l.location_id
        WHERE a.location_id = %s
        ORDER BY a.recorded_at DESC
        LIMIT 1
        """
        cursor.execute(query, (location_id,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not data:
            return jsonify({"message": "No AQI data found"}), 404

        severity = get_aqi_category(data["aqi"])
        data.update(severity)
        
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@aqi_bp.route("/aqi/all", methods=["GET"])
def get_all_aqi():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            l.name AS location_name,
            a.aqi
        FROM aqi_readings a
        LEFT JOIN locations l ON a.location_id = l.location_id
        ORDER BY a.recorded_at DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        result = []
        for r in rows:
            severity = get_aqi_category(r["aqi"])
            r.update(severity)
            result.append(r)

        cursor.close()
        conn.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def convert_pm25_to_aqi(pm25):
    if pm25 <= 30:
        return 50
    elif pm25 <= 60:
        return 100
    elif pm25 <= 90:
        return 200
    elif pm25 <= 120:
        return 300
    elif pm25 <= 250:
        return 400
    else:
        return 500

#  ...existing code...

import requests

@aqi_bp.route("/aqi/current", methods=["GET"])
def current_location_aqi():
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if not lat or not lng:
        return jsonify({
            "aqi": None,
            "category": "Unavailable",
            "health_message": "Location not provided",
            "source": "System"
        })

    try:
        # Try OpenAQ first
        url = "https://api.openaq.org/v2/latest"
        params = {
            "coordinates": f"{lat},{lng}",
            "radius": 50000,  # 50km radius
            "parameter": "pm25",
            "limit": 10
        }

        headers = {
            "User-Agent": "GreenCity-Intelligence"
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            from datetime import datetime
            from db import get_db_connection

            if results:
                for result in results:
                    measurements = result.get("measurements", [])
                    if measurements:
                        pm25 = measurements[0]["value"]
                        aqi = convert_pm25_to_aqi(pm25)
                        category_data = get_aqi_category(aqi)

                        # ==============================
                        # 🔹 STORE IN DATABASE (HERE)
                        # ==============================

                        conn = get_db_connection()
                        cursor = conn.cursor(dictionary=True)

                        today = datetime.now().date()

                        station_name = result.get("location", "Unknown")
                        city_name = result.get("city", "Unknown")

                        # 1️⃣ Check / Insert City
                        cursor.execute("SELECT city_id FROM cities WHERE city_name=%s", (city_name,))
                        city = cursor.fetchone()

                        if not city:
                            cursor.execute("INSERT INTO cities (city_name) VALUES (%s)", (city_name,))
                            conn.commit()
                            city_id = cursor.lastrowid
                        else:
                            city_id = city["city_id"]

                        # 2️⃣ Check / Insert Location
                        cursor.execute("""
                            SELECT location_id FROM locations
                            WHERE name=%s AND city_id=%s
                        """, (station_name, city_id))

                        location = cursor.fetchone()

                        if not location:
                            cursor.execute("""
                                INSERT INTO locations (name, latitude, longitude, city_id)
                                VALUES (%s, %s, %s, %s)
                            """, (station_name, lat, lng, city_id))
                            conn.commit()
                            location_id = cursor.lastrowid
                        else:
                            location_id = location["location_id"]

                        # 3️⃣ Insert AQI (Unique per day)
                        cursor.execute("""
                            SELECT reading_id FROM aqi_readings
                            WHERE location_id=%s AND record_date=%s
                        """, (location_id, today))

                        existing = cursor.fetchone()

                        if not existing:
                            cursor.execute("""
                                INSERT INTO aqi_readings
                                (location_id, pm25, aqi, record_date)
                                VALUES (%s, %s, %s, %s)
                            """, (location_id, pm25, aqi, today))
                            conn.commit()

                        cursor.close()
                        conn.close()

                        # ==============================
                        # 🔹 THEN RETURN RESPONSE
                        # ==============================

                        return jsonify({
                            "aqi": aqi,
                            "pm25": pm25,
                            "category": category_data["category"],
                            "health_message": category_data["health_message"],
                            "source": "OpenAQ",
                            "station": station_name,
                            "distance_info": "Station within 50km"
                        })

        # Fallback: Use WAQI (World Air Quality Index) - No API key needed for basic access
        WAQI_API_KEY = "752f88867cdc07ae8736875beb47539dbdc3c544"
        waqi_url = f"https://api.waqi.info/feed/geo:{lat};{lng}/?token={WAQI_API_KEY}"
        
        waqi_response = requests.get(waqi_url, timeout=10)
        
        if waqi_response.status_code == 200:
            waqi_data = waqi_response.json()
            
            from datetime import datetime
            from db import get_db_connection

            if waqi_data.get("status") == "ok":
                aqi = waqi_data["data"]["aqi"]
                category_data = get_aqi_category(aqi)

                # ==============================
                # 🔹 STORE WAQI DATA IN DB
                # ==============================

                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)

                today = datetime.now().date()

                station_name = waqi_data["data"].get("city", {}).get("name", "Unknown")
                city_name = station_name  # WAQI usually gives city-level name

                # 1️⃣ Check / Insert City
                cursor.execute("SELECT city_id FROM cities WHERE city_name=%s", (city_name,))
                city = cursor.fetchone()

                if not city:
                    cursor.execute("INSERT INTO cities (city_name) VALUES (%s)", (city_name,))
                    conn.commit()
                    city_id = cursor.lastrowid
                else:
                    city_id = city["city_id"]

                # 2️⃣ Check / Insert Location
                cursor.execute("""
                    SELECT location_id FROM locations
                    WHERE name=%s AND city_id=%s
                """, (station_name, city_id))

                location = cursor.fetchone()

                if not location:
                    cursor.execute("""
                        INSERT INTO locations (name, latitude, longitude, city_id)
                        VALUES (%s, %s, %s, %s)
                    """, (station_name, lat, lng, city_id))
                    conn.commit()
                    location_id = cursor.lastrowid
                else:
                    location_id = location["location_id"]

                # 3️⃣ Insert AQI (Unique per day)
                cursor.execute("""
                    SELECT reading_id FROM aqi_readings
                    WHERE location_id=%s AND record_date=%s
                """, (location_id, today))

                existing = cursor.fetchone()

                if not existing:
                    cursor.execute("""
                        INSERT INTO aqi_readings
                        (location_id, pm25, aqi, record_date)
                        VALUES (%s, %s, %s, %s)
                    """, (location_id, None, aqi, today))
                    conn.commit()

                cursor.close()
                conn.close()

                # ==============================
                # 🔹 RETURN RESPONSE
                # ==============================

                return jsonify({
                    "aqi": aqi,
                    "category": category_data["category"],
                    "health_message": category_data["health_message"],
                    "source": "WAQI",
                    "station": station_name
                })

        # If both APIs fail
        return jsonify({
            "aqi": None,
            "category": "Data Unavailable",
            "health_message": "No nearby AQI station found. Try another location or check database records.",
            "source": "System",
            "suggestion": "Use /aqi endpoint with location_id for stored data"
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "aqi": None,
            "category": "Error",
            "health_message": "API request timed out",
            "source": "System"
        }), 504
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "aqi": None,
            "category": "Error",
            "health_message": "Failed to fetch AQI from external sources",
            "source": "System",
            "error": str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            "aqi": None,
            "category": "Error",
            "health_message": "Internal server error",
            "source": "System",
            "error": str(e)
        }), 500
        
        
# Important Notes:
# OpenAQ does not require API key ✓
# WAQI uses a "demo" token (limited to 1000 requests/day per IP)
# For production WAQI usage, get a free API key from: https://aqicn.org/api/
# Replace "demo" with your actual WAQI token for better reliability




@aqi_bp.route("/aqi/predict", methods=["GET"])
def predict_aqi():

    prediction = predict_next_day()

    if prediction is None:
        return jsonify({
            "message": "Not enough data to predict"
        }), 400

    category = get_aqi_category(prediction)

    return jsonify({
        "predicted_aqi": prediction,
        "category": category["category"],
        "health_message": category["health_message"]
    })
    

@aqi_bp.route("/aqi/trend", methods=["GET"])
def aqi_trend():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT record_date, AVG(aqi) as avg_aqi
    FROM aqi_readings ar
    JOIN locations l ON ar.location_id = l.location_id
    GROUP BY record_date
    ORDER BY record_date DESC
    LIMIT 7
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    rows.reverse()  # Oldest first

    return jsonify(rows)