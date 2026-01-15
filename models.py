from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Environmental ranges
    temp_min = db.Column(db.Float, default=20.0)
    temp_max = db.Column(db.Float, default=30.0)
    humidity_min = db.Column(db.Float, default=40.0)
    humidity_max = db.Column(db.Float, default=70.0)
    # Nutrient ranges
    ph_min = db.Column(db.Float, default=5.5)
    ph_max = db.Column(db.Float, default=6.5)
    tds_min = db.Column(db.Float, default=800.0)
    tds_max = db.Column(db.Float, default=1200.0)
    # Industrial & Safety Fields
    category = db.Column(db.String(50), default="Leafy") # Leafy / Fruiting / Herb
    auto_ph_correction = db.Column(db.Boolean, default=True)
    spectrum_pref = db.Column(db.String(50), default="Full") # Blue / Red / Full
    safety_max_temp = db.Column(db.Float, default=40.0)
    safety_min_water = db.Column(db.Float, default=15.0)
    # Nutrient ranges
    n_min = db.Column(db.Float, default=100.0)
    n_max = db.Column(db.Float, default=200.0)
    p_min = db.Column(db.Float, default=30.0)
    p_max = db.Column(db.Float, default=50.0)
    k_min = db.Column(db.Float, default=100.0)
    k_max = db.Column(db.Float, default=300.0)
    light_min = db.Column(db.Float, default=1000.0)
    light_max = db.Column(db.Float, default=20000.0)
    expected_days = db.Column(db.Integer, default=60)
    # Current progress
    start_date = db.Column(db.DateTime, default=datetime.utcnow)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    n_val = db.Column(db.Float)
    p_val = db.Column(db.Float)
    k_val = db.Column(db.Float)
    water_temp = db.Column(db.Float)
    water_level = db.Column(db.Float)
    light_intensity = db.Column(db.Float)
    cpu_temp = db.Column(db.Float)
    gas_status = db.Column(db.Float) # 0 for OK, 1 for Gas Detected

class ControlStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'n_pump', 'grow_light'
    is_on = db.Column(db.Boolean, default=False)
    settings = db.Column(db.JSON, nullable=True) # Store intensity, spectrum for lights

class TankLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'n_tank'
    level_percent = db.Column(db.Float, default=100.0)
