from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from firebase_config import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not db:
            flash("Database not connected. Please check configuration.", category='error')
            return render_template("login.html", user=current_user)

        # Firestore Query
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).stream()
        user_doc = next(query, None) # Get first match

        if user_doc:
            user_data = user_doc.to_dict()
            if check_password_hash(user_data['password_hash'], password):
                flash('Logged in successfully!', category='success')
                # Create User object for Flask-Login
                user_obj = User(
                    email=user_data['email'], 
                    password_hash=user_data['password_hash'], 
                    name=user_data['name'], 
                    id=user_doc.id # Use doc ID
                )
                login_user(user_obj, remember=True)
                return redirect(url_for('views.monitor'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        if not db:
             flash("Database key missing.", category='error')
             return render_template("register.html", user=current_user)

        users_ref = db.collection('users')
        if next(users_ref.where('email', '==', email).limit(1).stream(), None):
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Create new user
            new_user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password) # Default method sha256
            )
            
            # Add to Firestore
            users_ref.add(new_user.to_dict())
            
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))

    return render_template("register.html", user=current_user)
