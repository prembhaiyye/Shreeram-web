from flask import Flask
from models import User, Plant, ControlStatus, TankLevel
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-this' # Change for production
    
    # Firebase Init
    from firebase_config import db
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if not db: return None
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            return User(email=data['email'], password_hash=data['password_hash'], name=data['name'], id=user_id)
        return None

    # Register Blueprints
    from routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from routes.views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    # Seed Default Data (Firestore)
    if db:
        # 1. Plants
        plants_ref = db.collection('plants')
        if not next(plants_ref.limit(1).stream(), None):
            print("🌱 Seeding Default Plant...")
            default_plant = Plant(name="Lettuce")
            plants_ref.add(default_plant.to_dict())

        # 2. Controls
        controls_ref = db.collection('control_status')
        if not next(controls_ref.limit(1).stream(), None):
            print("🔌 Seeding Default Controls...")
            controls = ['n_pump', 'p_pump', 'k_pump', 'ph_up_pump', 'ph_down_pump', 
                        'circulation_pump', 'stirring_motor', 'oxygen_motor',
                        'environmental_fans', 'cpu_fans', 'grow_light']
            for name in controls:
                # Use name as doc ID
                controls_ref.document(name).set(ControlStatus(name=name).to_dict())
        
        # 3. Tanks
        tanks_ref = db.collection('tanks')
        if not next(tanks_ref.limit(1).stream(), None):
             print("🛢️ Seeding Default Tanks...")
             tanks = ['n_tank', 'p_tank', 'k_tank', 'ph_up_tank', 'ph_down_tank', 'main_tank']
             for name in tanks:
                 tanks_ref.document(name).set(TankLevel(name=name).to_dict())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
