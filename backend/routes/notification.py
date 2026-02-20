from flask import Blueprint, jsonify, request
from db import get_db_connection

notification_bp = Blueprint("notification", __name__)

@notification_bp.route("/notifications", methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT notification_id, message, is_read, created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        notifications = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(notifications), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
    
    
    
@notification_bp.route("/notifications/unread-count", methods=["GET"])
def unread_notification_count():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM notifications
            WHERE user_id = %s AND is_read = FALSE
            """,
            (user_id,)
        )

        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({"unread_count": count}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@notification_bp.route("/notification/<int:notification_id>/read", methods=["PUT"])
def mark_notification_read(notification_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE notifications
            SET is_read = TRUE
            WHERE notification_id = %s
            """,
            (notification_id,)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Notification marked as read"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notification_bp.route("/notifications/mark-all-read", methods=["PUT"])
def mark_all_notifications_read():
    user_id = request.json.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = %s AND is_read = FALSE
            """,
            (user_id,)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "All notifications marked as read"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
