from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import Plant, SensorData, ControlStatus, TankLevel

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.monitor'))
    return redirect(url_for('auth.login'))

@views.route('/monitor')
@login_required
def monitor():
    plant = Plant.query.first()
    return render_template('monitor.html', user=current_user, plant=plant)

@views.route('/graph/<sensor_type>')
@login_required
def graph(sensor_type):
    plant = Plant.query.first()
    return render_template('graph.html', user=current_user, sensor_type=sensor_type, plant=plant)

@views.route('/controls')
@login_required
def controls():
    plant = Plant.query.first()
    controls = ControlStatus.query.all()
    # Convert list to dict for easier access in template if needed, or pass as list
    return render_template('controls.html', user=current_user, controls=controls, plant=plant)

@views.route('/profile')
@login_required
def profile():
    plant = Plant.query.first()
    return render_template('profile.html', user=current_user, plant=plant)

@views.route('/developer')
@login_required
def developer():
    plant = Plant.query.first()
    return render_template('developer.html', user=current_user, plant=plant)

@views.route('/tanks')
@login_required
def tanks():
    plant = Plant.query.first()
    tanks = TankLevel.query.all()
    return render_template('tanks.html', user=current_user, tanks=tanks, plant=plant)
