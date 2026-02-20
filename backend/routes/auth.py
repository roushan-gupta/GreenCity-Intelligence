from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify
from flask_mail import Message
from db import get_db_connection
import random
import string
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

# In-memory OTP storage (use Redis or database in production)
otp_storage = {}

# Mail instance will be set by app.py
mail = None

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP via email"""
    try:
        msg = Message(
            subject="Pollution Management System - OTP Verification",
            recipients=[email],
            body=f"Your OTP for registration is: {otp}\n\nThis OTP will expire in 10 minutes.\n\nIf you didn't request this, please ignore this email."
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    """Send OTP to user's email for registration"""
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        # Check if email already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing_user:
            return jsonify({"message": "Email already registered"}), 400

        # Generate OTP
        otp = generate_otp()
        
        # Store OTP with expiration time (10 minutes)
        otp_storage[email] = {
            "otp": otp,
            "expires_at": datetime.now() + timedelta(minutes=10)
        }

        # Send OTP via email
        if send_otp_email(email, otp):
            return jsonify({"message": "OTP sent to your email"}), 200
        else:
            return jsonify({"message": "Failed to send OTP. Please check email configuration."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/register-with-otp", methods=["POST"])
def register_with_otp():
    """Register user after OTP verification"""
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    name = data.get("name")
    contact_number = data.get("contact_number")
    address_house = data.get("address_house")
    address_street = data.get("address_street")
    address_city = data.get("address_city")
    address_state = data.get("address_state")
    address_pincode = data.get("address_pincode")
    password = data.get("password")

    if not email or not otp or not password:
        return jsonify({"message": "Email, OTP, and password are required"}), 400

    if not name or not contact_number or not address_house or not address_street or not address_city or not address_state or not address_pincode:
        return jsonify({"message": "All profile and address fields are required"}), 400

    try:
        # Verify OTP
        if email not in otp_storage:
            return jsonify({"message": "No OTP found. Please request a new one."}), 400

        stored_data = otp_storage[email]
        
        # Check if OTP expired
        if datetime.now() > stored_data["expires_at"]:
            del otp_storage[email]
            return jsonify({"message": "OTP expired. Please request a new one."}), 400

        # Check if OTP matches
        if stored_data["otp"] != otp:
            return jsonify({"message": "Invalid OTP"}), 400

        # OTP is valid, create user
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users (name, email, contact_number, address_house, address_street, address_city, address_state, address_pincode, password, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'CITIZEN')
        """
        cursor.execute(
            query,
            (
                name,
                email,
                contact_number,
                address_house,
                address_street,
                address_city,
                address_state,
                address_pincode,
                hashed_password,
            )
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Remove OTP from storage after successful registration
        del otp_storage[email]

        return jsonify({"message": "Registration successful! Please login."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    raw_password = data.get("password")
    hashed_password = generate_password_hash(raw_password)

    if not name or not email or not raw_password:
        return jsonify({"message": "All fields are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (name, email, hashed_password))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({"message": "User not found"}), 404

        if not check_password_hash(user["password"], password):
                return jsonify({"message": "Invalid password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user["user_id"],
            "name": user["name"],
            "role": user["role"],
            "email": user["email"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, name, email, contact_number, address_house, address_street,
                   address_city, address_state, address_pincode, role, created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user_profile(user_id):
    data = request.json
    name = data.get("name")
    contact_number = data.get("contact_number")
    address_house = data.get("address_house")
    address_street = data.get("address_street")
    address_city = data.get("address_city")
    address_state = data.get("address_state")
    address_pincode = data.get("address_pincode")

    if not name or not contact_number or not address_house or not address_street or not address_city or not address_state or not address_pincode:
        return jsonify({"message": "All profile and address fields are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET name = %s,
                contact_number = %s,
                address_house = %s,
                address_street = %s,
                address_city = %s,
                address_state = %s,
                address_pincode = %s
            WHERE user_id = %s
            """,
            (
                name,
                contact_number,
                address_house,
                address_street,
                address_city,
                address_state,
                address_pincode,
                user_id,
            )
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
