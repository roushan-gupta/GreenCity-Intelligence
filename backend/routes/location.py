from flask import Blueprint, jsonify
from db import get_db_connection

location_bp = Blueprint("location", __name__)

@location_bp.route("/locations", methods=["GET"])
def get_locations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM locations")
        locations = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(locations), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500