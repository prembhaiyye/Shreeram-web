from datetime import datetime

class User:
    def __init__(self, email, password_hash, name, id=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name

    def to_dict(self):
        return {
            'email': self.email,
            'password_hash': self.password_hash,
            'name': self.name
        }
    
    # Flask-Login Mixin compat
    @property
    def is_active(self): return True
    @property
    def is_authenticated(self): return True
    @property
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

class Plant:
    def __init__(self, name, category="Leafy", control_pref=None, env_ranges=None, nutrient_ranges=None, id=None):
        self.id = id
        self.name = name
        self.category = category
        
        # Ranges & Preferences - Flattened or Nested (Nested is better for NoSQL)
        self.env_ranges = env_ranges or {
            'temp_min': 20.0, 'temp_max': 30.0,
            'humidity_min': 40.0, 'humidity_max': 70.0
        }
        self.nutrient_ranges = nutrient_ranges or {
            'ph_min': 5.5, 'ph_max': 6.5,
            'tds_min': 800.0, 'tds_max': 1200.0,
            'n_min': 100.0, 'n_max': 200.0,
            'p_min': 30.0, 'p_max': 50.0,
            'k_min': 100.0, 'k_max': 300.0
        }
        self.control_pref = control_pref or {
            'auto_ph_correction': True,
            'spectrum_pref': 'Full',
            'safety_max_temp': 40.0,
            'safety_min_water': 15.0
        }
        self.start_date = datetime.utcnow()
        self.expected_days = 60

    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'env_ranges': self.env_ranges,
            'nutrient_ranges': self.nutrient_ranges,
            'control_pref': self.control_pref,
            'start_date': self.start_date,
            'expected_days': self.expected_days
        }

class SensorData:
    def __init__(self, data_dict):
        self.timestamp = datetime.utcnow()
        self.data = data_dict # Includes temp, ph, etc.

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            **self.data
        }

class ControlStatus:
    def __init__(self, name, id=None, is_on=False, settings=None, mode='manual', locked=False, locked_reason=None, last_active=None):
        self.id = id or name # Use name as ID for controls usually
        self.name = name
        self.is_on = is_on
        self.settings = settings or {}
        
        # Advanced Features
        self.mode = mode
        self.locked = locked
        self.locked_reason = locked_reason
        self.last_active = last_active

    def to_dict(self):
        return {
            'name': self.name,
            'is_on': self.is_on,
            'settings': self.settings,
            'mode': self.mode,
            'locked': self.locked,
            'locked_reason': self.locked_reason,
            'last_active': self.last_active
        }

class ControlLog:
    def __init__(self, control_name, action, trigger='manual', details=None):
        self.timestamp = datetime.utcnow()
        self.control_name = control_name
        self.action = action
        self.trigger = trigger
        self.details = details

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'control_name': self.control_name,
            'action': self.action,
            'trigger': self.trigger,
            'details': self.details
        }

class TankLevel:
    def __init__(self, name, level_percent=100.0):
        self.name = name
        self.level_percent = level_percent

    def to_dict(self):
        return {
            'name': self.name,
            'level_percent': self.level_percent
        }


