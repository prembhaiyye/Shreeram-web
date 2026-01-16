from flask import Blueprint, jsonify, request
from models import SensorData, ControlStatus, ControlLog
from firebase_config import db
from flask_login import login_required
import datetime
import random

api = Blueprint('api', __name__)

@api.route('/api/sensor-data', methods=['GET'])
@login_required
def get_sensor_data():
    # Simulate hardware pushing data to Firestore
    # In production, Pi would write to Firestore directly or via a specific API key
    
    new_data = {
        'temperature': random.uniform(20, 30),
        'humidity': random.uniform(40, 70),
        'ph': random.uniform(5.5, 6.5),
        'tds': random.uniform(800, 1200),
        'n_val': random.uniform(100, 200),
        'p_val': random.uniform(30, 50),
        'k_val': random.uniform(100, 300),
        'water_temp': random.uniform(18, 25),
        'water_level': random.uniform(80, 100),
        'light_intensity': random.uniform(1000, 5000),
        'cpu_temp': random.uniform(40, 60),
        'gas_status': 0
    }
    
    if db:
        # Create SensorData object
        record = SensorData(new_data)
        db.collection('sensor_data').add(record.to_dict())
        return jsonify(new_data)
        
    return jsonify(new_data) # Fallback if no DB

@api.route('/api/controls', methods=['GET', 'POST'])
@login_required
def update_control():
    if not db:
        return jsonify({'success': False, 'error': 'Database not connected'}), 500

    controls_ref = db.collection('control_status')
    
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        state = data.get('state') # True/False
        
        doc_ref = controls_ref.document(name)
        doc = doc_ref.get()
        
        if doc.exists:
            control_data = doc.to_dict()
            
            # --- Advanced Safety Logic ---
            
            # 1. Check Locks
            if control_data.get('locked', False) and state:
                return jsonify({
                    "success": False, 
                    "message": f"Action Blocked: {control_data.get('locked_reason', 'Safety Lock Active')}"
                }), 403

            # 2. Get Latest Sensor Data for Interlocks
            sensor_query = db.collection('sensor_data').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
            latest_sensor = next(sensor_query, None)
            sensor_val = latest_sensor.to_dict() if latest_sensor else {}

            # 3. Water Level Protection (Pumps)
            if 'pump' in name and sensor_val.get('water_level', 100) < 15.0:
                 return jsonify({
                    "success": False, 
                    "message": "Action Blocked: Low Water Level (Run Dry Protection)"
                }), 403

            # 4. pH Interlock (Simultaneous Dosing)
            if 'ph' in name:
                opposite = 'ph_down_pump' if 'up' in name else 'ph_up_pump'
                opp_doc = controls_ref.document(opposite).get()
                if opp_doc.exists and opp_doc.to_dict().get('is_on', False) and state:
                     return jsonify({
                        "success": False, 
                        "message": "Action Blocked: Cannot dose pH Up and Down simultaneously."
                    }), 403
            
            # --- Apply Change ---
            
            update_data = {'is_on': state}
            if state:
                update_data['last_active'] = datetime.datetime.utcnow()
            
            doc_ref.update(update_data)
            
            # --- Log Action ---
            log_entry = ControlLog(
                control_name=name,
                action="ON" if state else "OFF",
                trigger="manual",
                details="User toggled via UI"
            )
            db.collection('control_logs').add(log_entry.to_dict())
            
            return jsonify({'success': True, 'new_state': state})
            
        return jsonify({'success': False, 'error': 'Control not found'}), 404
        
    # GET - return all states
    docs = controls_ref.stream()
    # Return simple key-value for frontend compatibility or full objects? 
    # The frontend expects {name: state}.
    res = {}
    for doc in docs:
        d = doc.to_dict()
        res[d['name']] = d['is_on']
    return jsonify(res)

@api.route('/api/controls/mode', methods=['POST'])
@login_required
def update_control_mode():
    if not db: return jsonify({'success': False}), 500
    
    data = request.json
    mode = data.get('mode') # manual, auto, schedule
    
    # Update all controls to this mode
    # In a batch would be better, but loop is fine for < 20 docs
    batch = db.batch()
    docs = db.collection('control_status').stream()
    for doc in docs:
        batch.update(doc.reference, {'mode': mode})
    batch.commit()
    
    return jsonify({"success": True, "mode": mode})

@api.route('/api/controls/emergency-stop', methods=['POST'])
@login_required
def emergency_stop():
    if not db: return jsonify({'success': False}), 500
    
    # Find all active
    active_docs = db.collection('control_status').where('is_on', '==', True).stream()
    count = 0
    batch = db.batch()
    
    for doc in active_docs:
        batch.update(doc.reference, {'is_on': False})
        
        # Log
        log = ControlLog(
            control_name=doc.id,
            action="OFF",
            trigger="emergency",
            details="Emergency Stop Triggered"
        )
        db.collection('control_logs').add(log.to_dict())
        count += 1
        
    batch.commit()
    return jsonify({"success": True, "message": f"Stopped {count} active devices."})

@api.route('/api/upload-image', methods=['POST'])
@login_required
def upload_image():
    return jsonify({'success': True, 'message': 'Image uploaded successfully'}) # Mock

@api.route('/api/capture-system-camera', methods=['GET'])
@login_required
def capture_system_camera():
    return jsonify({
        'success': True, 
        'image_url': '/static/images/mock_pi_capture.jpg',
        'timestamp': datetime.datetime.now().isoformat()
    })

@api.route('/api/analyze-image', methods=['POST'])
@login_required
def analyze_image():
    # Simulate an AI analysis call
    issues = [
        {"health": "Healthy", "issue": "None", "confidence": 0.98, "cause": "Optimal conditions", "recommendation": "Maintain current nutrient levels"},
        {"health": "Unhealthy", "issue": "Nitrogen Deficiency", "confidence": 0.87, "cause": "Low nitrogen availability", "recommendation": "Increase nitrogen concentration"},
        {"health": "Unhealthy", "issue": "Powdery Mildew", "confidence": 0.76, "cause": "High humidity & poor airflow", "recommendation": "Improve ventilation and reduce humidity"},
        {"health": "Unhealthy", "issue": "pH Imbalance", "confidence": 0.92, "cause": "pH outside optimal range of 5.5-6.5", "recommendation": "Calibrate sensors and adjust pH using reagents"}
    ]
    result = random.choice(issues)
    result['sensor_validated'] = True # simplified
    return jsonify(result)

