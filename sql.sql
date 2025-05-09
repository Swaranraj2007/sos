-- Emergency Response App Database Schema

CREATE DATABASE emergency_response_app;
USE emergency_response_app;

-- 1. User Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Emergency Contacts Table
CREATE TABLE emergency_contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    contact_name VARCHAR(50) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    relationship VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Health Information Table
CREATE TABLE health_info (
    health_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    blood_group VARCHAR(3),
    medical_conditions TEXT,
    allergies TEXT,
    medications TEXT,
    emergency_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Incident Records Table
CREATE TABLE incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    incident_type VARCHAR(100),
    description TEXT,
    incident_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. Location History Table
CREATE TABLE location_history (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 6. SOS Requests Table
CREATE TABLE sos_requests (
    sos_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    location VARCHAR(100),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
