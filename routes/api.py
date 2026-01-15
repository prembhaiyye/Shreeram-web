from flask import Blueprint, jsonify, request
from models import db, SensorData, ControlStatus, Plant, TankLevel
from flask_login import login_required, current_user
import datetime
import random # For simulation

api = Blueprint('api', __name__)

@api.route('/api/sensor-data', methods=['GET'])
@login_required
def get_sensor_data():
    # In a real app, this would query the latest data from the DB
    # or the hardware interface. Here we simulate live data if DB is empty or old.
    
    # Simulate new reading
    new_data = SensorData(
        temperature=random.uniform(20, 30),
        humidity=random.uniform(40, 70),
        ph=random.uniform(5.5, 6.5),
        tds=random.uniform(800, 1200),
        n_val=random.uniform(100, 200),
        p_val=random.uniform(30, 50),
        k_val=random.uniform(100, 300),
        water_temp=random.uniform(18, 25),
        water_level=random.uniform(80, 100),
        light_intensity=random.uniform(1000, 5000),
        cpu_temp=random.uniform(40, 60),
        gas_status=0
    )
    db.session.add(new_data)
    db.session.commit()
    
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    
    return jsonify({
        'temperature': latest.temperature,
        'humidity': latest.humidity,
        'ph': latest.ph,
        'tds': latest.tds,
        'n': latest.n_val,
        'p': latest.p_val,
        'k': latest.k_val,
        'cpu_temp': latest.cpu_temp,
        'light': latest.light_intensity,
        'gas': latest.gas_status,
        'water_level': latest.water_level
    })

@api.route('/api/controls', methods=['GET', 'POST'])
@login_required
def controls():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        state = data.get('state') # True/False
        
        control = ControlStatus.query.filter_by(name=name).first()
        if control:
            control.is_on = state
            db.session.commit()
            return jsonify({'success': True, 'new_state': control.is_on})
        return jsonify({'success': False, 'error': 'Control not found'}), 404
        
    # GET - return all states
    controls = ControlStatus.query.all()
    return jsonify({c.name: c.is_on for c in controls})

@api.route('/api/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    # In a real app, save the file to a temporary location
    # For now, we'll just acknowledge receipt
    return jsonify({'success': True, 'message': 'Image uploaded successfully'})

@api.route('/api/capture-system-camera', methods=['GET'])
@login_required
def capture_system_camera():
    # Simulate a Raspberry Pi camera capture
    # In reality, you'd use picamera or libcamera here
    # Return a status and perhaps a mock image URL or base64
    return jsonify({
        'success': True, 
        'image_url': '/static/images/mock_pi_capture.jpg',
        'timestamp': datetime.datetime.now().isoformat()
    })

@api.route('/api/analyze-image', methods=['POST'])
@login_required
def analyze_image():
    # Simulate an AI analysis call
    # In a real app, you'd send the image to an online API (e.g., Plant.id)
    
    # Random issues for simulation
    issues = [
        {"health": "Healthy", "issue": "None", "confidence": 0.98, "cause": "Optimal conditions", "recommendation": "Maintain current nutrient levels"},
        {"health": "Unhealthy", "issue": "Nitrogen Deficiency", "confidence": 0.87, "cause": "Low nitrogen availability", "recommendation": "Increase nitrogen concentration"},
        {"health": "Unhealthy", "issue": "Powdery Mildew", "confidence": 0.76, "cause": "High humidity & poor airflow", "recommendation": "Improve ventilation and reduce humidity"},
        {"health": "Unhealthy", "issue": "pH Imbalance", "confidence": 0.92, "cause": "pH outside optimal range of 5.5-6.5", "recommendation": "Calibrate sensors and adjust pH using reagents"}
    ]
    
    result = random.choice(issues)
    
    # Sensor Validation Badge Logic (Simplified)
    latest_sensors = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    sensor_validated = False
    
    if latest_sensors:
        if result['issue'] == "Nitrogen Deficiency" and latest_sensors.n_val < 120:
            sensor_validated = True
        elif result['issue'] == "pH Imbalance" and (latest_sensors.ph < 5.5 or latest_sensors.ph > 6.5):
            sensor_validated = True
        elif result['health'] == "Healthy" and (5.8 <= latest_sensors.ph <= 6.2):
            sensor_validated = True

    result['sensor_validated'] = sensor_validated
    
    return jsonify(result)
