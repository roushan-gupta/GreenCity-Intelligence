import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Flask application entry point
from flask import Flask
from flask_cors import CORS
from flask import send_from_directory
from flask_mail import Mail
import config


app = Flask(__name__)
CORS(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

mail = Mail(app)

# Make mail accessible to other modules
from routes import auth
auth.mail = mail

from routes.auth import auth_bp
from routes.location import location_bp
from routes.aqi import aqi_bp
from routes.incident import incident_bp
from routes.notification import notification_bp

app.register_blueprint(auth_bp)
app.register_blueprint(location_bp)
app.register_blueprint(aqi_bp)
app.register_blueprint(incident_bp)
app.register_blueprint(notification_bp)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

# @app.route("/frontend/<path:filename>")
# def serve_frontend(filename):
#     return send_from_directory("../frontend", filename)

@app.route("/")
def home():
    return "Pollution Management System Backend Running"

@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection successful"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
    
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False