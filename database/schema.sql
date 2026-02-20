-- Database schema
CREATE DATABASE IF NOT EXISTS pollution_db;
USE pollution_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contact_number VARCHAR(20),
    address_house VARCHAR(100),
    address_street VARCHAR(100),
    address_city VARCHAR(100),
    address_state VARCHAR(100),
    address_pincode VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    role ENUM('CITIZEN', 'ADMIN') DEFAULT 'CITIZEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations Table
CREATE TABLE IF NOT EXISTS locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AQI Readings Table
CREATE TABLE IF NOT EXISTS aqi_readings (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    pm25 DECIMAL(10, 2),
    pm10 DECIMAL(10, 2),
    aqi INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
);

-- Incidents Table
CREATE TABLE IF NOT EXISTS incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    location_id INT,
    incident_type VARCHAR(100) NOT NULL,
    description TEXT,
    image_path VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    place_name VARCHAR(255),
    status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED') DEFAULT 'OPEN',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Insert sample locations
INSERT INTO locations (name, latitude, longitude) VALUES 
('Delhi Central', 28.6139, 77.2090),
('Mumbai Downtown', 19.0760, 72.8777),
('Bangalore Tech Park', 12.9716, 77.5946),
('Chennai Marina', 13.0827, 80.2707),
('Kolkata Park Street', 22.5726, 88.3639)
ON DUPLICATE KEY UPDATE name=name;


-- ML prediction table
CREATE TABLE cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL UNIQUE,
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India'
);

CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT,
    location_name VARCHAR(150),
    latitude DOUBLE,
    longitude DOUBLE,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE aqi_readings (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT,
    location_id INT,
    pm25 DOUBLE,
    aqi INT,
    record_date DATE,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    UNIQUE (location_id, record_date)
);