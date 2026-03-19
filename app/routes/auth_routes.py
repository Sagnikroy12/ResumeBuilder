from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app.extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    user_exists = User.query.filter_by(username=username).first()
    email_exists = User.query.filter_by(email=email).first()
    
    if user_exists:
        return jsonify({"message": "Username is already taken.", "status": "danger"}), 400
    elif email_exists:
        return jsonify({"message": "Email is already registered.", "status": "danger"}), 400
    else:
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Your account has been created!", "status": "success"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user, remember=data.get('remember', False))
        return jsonify({
            "message": "Login Successful!", 
            "status": "success",
            "user": {"id": user.id, "username": user.username, "email": user.email, "is_premium": user.is_premium}
        }), 200
    else:
        return jsonify({"message": "Login Unsuccessful. Please check email and password", "status": "danger"}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "You have been logged out.", "status": "info"}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email, "is_premium": current_user.is_premium}
        }), 200
    return jsonify({"user": None}), 200

@auth_bp.route('/toggle-premium', methods=['POST'])
@login_required
def toggle_premium():
    """Toggle Pro status for master user."""
    MASTER_EMAIL = "sagnikruproy11@gmail.com"
    if current_user.email != MASTER_EMAIL:
        return jsonify({"message": "Unauthorized"}), 403
    
    current_user.is_premium = not current_user.is_premium
    db.session.commit()
    
    status = "Pro" if current_user.is_premium else "Free"
    return jsonify({
        "message": f"Account toggled to {status}!", 
        "is_premium": current_user.is_premium
    }), 200
