from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import Plant, ControlStatus, TankLevel
from firebase_config import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.monitor'))
    return redirect(url_for('auth.login'))

@views.route('/monitor')
@login_required
def monitor():
    plant = None
    if db:
        plant_docs = db.collection('plants').limit(1).stream()
        p_doc = next(plant_docs, None)
        if p_doc:
            plant = Plant(**p_doc.to_dict(), id=p_doc.id)
            
    return render_template('monitor.html', user=current_user, plant=plant)

@views.route('/graph/<sensor_type>')
@login_required
def graph(sensor_type):
    plant = None
    controls = []
    
    if db:
        # Plant
        plant_docs = db.collection('plants').limit(1).stream()
        p_doc = next(plant_docs, None)
        if p_doc: plant = Plant(**p_doc.to_dict(), id=p_doc.id)

        # Fetched mapped controls
        control_map = {
            'temperature': ['environmental_fans', 'cpu_fans'],
            'humidity': ['environmental_fans'],
            'ph': ['ph_up_pump', 'ph_down_pump', 'circulation_pump', 'stirring_motor'],
            'tds': ['n_pump', 'p_pump', 'k_pump', 'circulation_pump', 'stirring_motor'],
            'n': ['n_pump', 'stirring_motor'],
            'light': ['grow_light']
        }
        
        target_names = control_map.get(sensor_type, [])
        if target_names:
            # Firestore 'in' query supports max 10
            docs = db.collection('control_status').where('name', 'in', target_names).stream()
            controls = [ControlStatus(**d.to_dict(), id=d.id) for d in docs]

    return render_template('graph.html', user=current_user, sensor_type=sensor_type, plant=plant, controls=controls)

@views.route('/controls')
@login_required
def controls():
    plant = None
    controls = []
    
    if db:
        # Plant
        plant_docs = db.collection('plants').limit(1).stream()
        p_doc = next(plant_docs, None)
        if p_doc: plant = Plant(**p_doc.to_dict(), id=p_doc.id)
        
        # Controls
        # Stream all to get advanced fields
        docs = db.collection('control_status').stream()
        controls = [ControlStatus(**d.to_dict(), id=d.id) for d in docs]
        
        # Sort by name or custom order if needed
        controls.sort(key=lambda x: x.name)

    return render_template('controls.html', user=current_user, controls=controls, plant=plant)

@views.route('/profile')
@login_required
def profile():
    plant = None
    if db:
        plant_docs = db.collection('plants').limit(1).stream()
        p_doc = next(plant_docs, None)
        if p_doc: plant = Plant(**p_doc.to_dict(), id=p_doc.id)
    return render_template('profile.html', user=current_user, plant=plant)

@views.route('/developer')
@views.route('/developer/<plant_id>')
@login_required
def developer(plant_id=None):
    plants = []
    active_plant = None
    
    if db:
        p_docs = db.collection('plants').stream()
        plants = [Plant(**d.to_dict(), id=d.id) for d in p_docs]
        
        if plant_id:
            # Find specific
            active_plant = next((p for p in plants if str(p.id) == plant_id), None)
        elif plants:
            active_plant = plants[0]

    return render_template('developer.html', user=current_user, plants=plants, plant=active_plant)

@views.route('/tanks')
@login_required
def tanks():
    plant = None
    tanks = []
    
    if db:
        # Plant
        p_doc = next(db.collection('plants').limit(1).stream(), None)
        if p_doc: plant = Plant(**p_doc.to_dict(), id=p_doc.id)
        
        # Tanks
        t_docs = db.collection('tanks').stream()
        tanks = [TankLevel(**d.to_dict()) for d in t_docs]

    return render_template('tanks.html', user=current_user, tanks=tanks, plant=plant)

@views.route('/ai-scan')
@login_required
def ai_scan():
    plant = None
    if db:
        p_doc = next(db.collection('plants').limit(1).stream(), None)
        if p_doc: plant = Plant(**p_doc.to_dict(), id=p_doc.id)
    return render_template('ai_scan.html', user=current_user, plant=plant)
