from flask import Flask
from models import db, User, Plant, ControlStatus, TankLevel
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-this' # Change for production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hydroponics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from routes.views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    with app.app_context():
        db.create_all()
        # Initialize default controls if not exist
        if not ControlStatus.query.first():
            controls = ['n_pump', 'p_pump', 'k_pump', 'ph_up_pump', 'ph_down_pump', 
                        'circulation_pump', 'stirring_motor', 'oxygen_motor',
                        'environmental_fans', 'cpu_fans', 'grow_light']
            for name in controls:
                db.session.add(ControlStatus(name=name))
            db.session.commit()
            
        # Initialize default tanks if not exist
        if not TankLevel.query.first():
            tanks = ['n_tank', 'p_tank', 'k_tank', 'ph_up_tank', 'ph_down_tank', 'main_tank']
            for name in tanks:
                db.session.add(TankLevel(name=name))
            db.session.commit()

        # Initialize default plant if not exist
        if not Plant.query.first():
            default_plant = Plant(name="Lettuce")
            db.session.add(default_plant)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
