# GreenCity-Intelligence

GreenCity-Intelligence is a full-stack pollution monitoring and incident management system.
It enables citizens to report environmental issues and helps authorities monitor AQI and manage reported incidents.

## Features

- Citizen registration with OTP email verification
- Role-based login (`CITIZEN`, `ADMIN`)
- Pollution incident reporting with optional image upload
- AQI data and location-based monitoring
- Notification support for users
- ML folder for AQI prediction experimentation

## Tech Stack

- **Backend:** Flask, Flask-CORS, Flask-Mail, MySQL Connector
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **ML:** Python (model scripts/notebook)

## Project Structure

```text
backend/
	app.py                # Flask entry point
	db.py                 # MySQL connection
	routes/               # API route blueprints
	services/             # Service-layer utilities
	uploads/              # Uploaded incident images
database/
	schema.sql            # DB schema
frontend/
	*.html                # UI pages
	js/                   # Frontend logic
	css/                  # Styling
ml/
	predict.py            # Prediction script
	train_model.ipynb     # Model training notebook
```

## Prerequisites

- Python 3.10+
- MySQL 8+

## Setup

### 1) Clone and move into project

```bash
git clone <your-repo-url>
cd GreenCity-Intelligence
```

### 2) Configure environment variables

Create `backend/.env` from `backend/.env.example` and fill your local secrets.

### 3) Configure MySQL

1. Create/import schema using `database/schema.sql`.
2. Ensure database name is `pollution_db`.
3. Update DB credentials in `backend/.env`:
	 - `DB_HOST`
	 - `DB_USER`
	 - `DB_PASSWORD`
	 - `DB_NAME`

### 4) Configure email (OTP)

Update SMTP settings in `backend/.env`:

- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

For Gmail, use an App Password (recommended).

### 5) Install backend dependencies

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 6) Run backend

```bash
python app.py
```

Backend runs at: `http://127.0.0.1:5000`

### 7) Run frontend

Open `frontend/index.html` in a browser (or serve `frontend/` with a local static server).

Frontend scripts currently call backend at:

`http://127.0.0.1:5000`

## Main API Routes

- Auth: `/login`, `/register`, `/send-otp`, `/register-with-otp`
- User profile: `/users/<user_id>`
- Other modules are registered from:
	- `backend/routes/location.py`
	- `backend/routes/aqi.py`
	- `backend/routes/incident.py`
	- `backend/routes/notification.py`

## Notes

- `backend/uploads/` stores uploaded incident images.
- If you change backend host/port, update frontend API URLs in `frontend/js/` files.
- Keep credentials out of version control for production use.

## Health Check

After starting backend, verify service:

- `GET /` → `Pollution Management System Backend Running`
