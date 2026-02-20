from flask import Blueprint, request, jsonify
from db import get_db_connection
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

incident_bp = Blueprint("incident", __name__)

# @incident_bp.route("/report-incident", methods=["POST"])
# def report_incident():
#     data = request.json

#     user_id = data.get("user_id")
#     location_id = data.get("location_id")
#     incident_type = data.get("incident_type")
#     description = data.get("description")

#     if not user_id or not location_id or not incident_type:
#         return jsonify({"message": "user_id, location_id and incident_type are required"}), 400

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = """
#         INSERT INTO incidents (user_id, location_id, incident_type, description)
#         VALUES (%s, %s, %s, %s)
#         """
#         cursor.execute(query, (user_id, location_id, incident_type, description))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"message": "Incident reported successfully"}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500





# FORCE INSERT EXAMPLE (UNCOMMENT TO TEST)

# @incident_bp.route("/report-incident", methods=["POST"])
# def report_incident():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # FORCE INSERT (NO CONDITIONS, NO LOOP)
#         cursor.execute(
#             "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
#             (4, "FORCE notification from report_incident")
#         )

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"message": "FORCE INSERT DONE"}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500









@incident_bp.route("/report-incident", methods=["POST"])
def report_incident():
    user_id = request.form.get("user_id")
    location_id = request.form.get("location_id")
    incident_type = request.form.get("incident_type")
    description = request.form.get("description")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    place_name = request.form.get("place_name")


    file = request.files.get("image")
    image_path = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)


        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not user_id or not incident_type or not latitude or not longitude:
            return jsonify({"message": "Missing required fields"}), 400

        query = """
        INSERT INTO incidents (user_id, location_id, incident_type, description, image_path, latitude, longitude, place_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, location_id, incident_type, description, image_path, latitude, longitude, place_name))

        conn.commit()
        # Create notification for admin users
        cursor.execute("SELECT user_id FROM users WHERE role = 'ADMIN'")
        admins = cursor.fetchall()

        notification_message = f"New pollution incident reported at location {place_name} for {incident_type}."

        for admin in admins:
            cursor.execute(
                "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
                (admin[0], notification_message)
            )

        conn.commit()
        
        cursor.close()
        conn.close()

        return jsonify({"message": "Incident reported with image successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    

@incident_bp.route("/incidents", methods=["GET"])
def get_all_incidents():
    status = request.args.get("status")  # optional filter

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if status:
            query = """
            SELECT i.incident_id, i.incident_type, i.description, i.status, i.reported_at,
                     i.user_id,
                   u.name AS citizen_name,
                   l.name AS location_name,
                   i.latitude,
                   i.longitude,
                   i.place_name,
                   i.image_path
            FROM incidents i
            JOIN users u ON i.user_id = u.user_id
            LEFT JOIN locations l ON i.location_id = l.location_id
            WHERE i.status = %s
            ORDER BY i.reported_at DESC
            """
            cursor.execute(query, (status,))
        else:
            query = """
            SELECT i.incident_id, i.incident_type, i.description, i.status, i.reported_at,
                     i.user_id,
                   u.name AS citizen_name,
                   l.name AS location_name,
                   i.image_path,
                   i.latitude,
                   i.longitude,
                   i.place_name
            FROM incidents i
            JOIN users u ON i.user_id = u.user_id
            LEFT JOIN locations l ON i.location_id = l.location_id
            ORDER BY i.reported_at DESC
            """
            cursor.execute(query)

        incidents = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(incidents), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
@incident_bp.route("/incident/<int:incident_id>/status", methods=["PUT"])
def update_incident_status(incident_id):
    new_status = request.json.get("status")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get current status
        cursor.execute(
            "SELECT status, user_id FROM incidents WHERE incident_id = %s",
            (incident_id,)
        )
        incident = cursor.fetchone()

        if not incident:
            return jsonify({"message": "Incident not found"}), 404

        current_status = incident["status"]

        # Allowed transitions
        allowed = {
            "OPEN": ["IN_PROGRESS"],
            "IN_PROGRESS": ["RESOLVED"],
            "RESOLVED": []
        }

        if new_status not in allowed[current_status]:
            return jsonify({"message": "Invalid status transition"}), 400

        # Update status
        cursor.execute(
            "UPDATE incidents SET status = %s WHERE incident_id = %s",
            (new_status, incident_id)
        )

        # Notify citizen ONCE per valid change
        cursor.execute(
            "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
            (incident["user_id"], f"Your incident #{incident_id} is now {new_status}")
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Status updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# @incident_bp.route("/debug-notification", methods=["GET"])
# def debug_notification():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         cursor.execute(
#             "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
#             (4, "Debug notification from Flask")
#         )

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return "DEBUG NOTIFICATION INSERTED"

#     except Exception as e:
#         return str(e)
