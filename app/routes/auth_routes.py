from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app.extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({"message": "Already authenticated", "status": "success"}), 200
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'GET':
        return render_template('auth/register.html')

    # Handle POST
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        msg = "Missing required fields."
        if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
        flash(msg, "danger")
        return render_template('auth/register.html')

    user_exists = User.query.filter_by(username=username).first()
    email_exists = User.query.filter_by(email=email).first()
    
    if user_exists:
        msg = "Username is already taken."
        if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
        flash(msg, "danger")
        return render_template('auth/register.html')
    elif email_exists:
        msg = "Email is already registered."
        if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
        flash(msg, "danger")
        return render_template('auth/register.html')
    else:
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        msg = "Your account has been created! Please log in."
        if request.is_json:
            return jsonify({"message": msg, "status": "success"}), 201
            
        flash(msg, "success")
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({
                "message": "Already authenticated", 
                "status": "success",
                "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email, "is_premium": current_user.is_premium}
            }), 200
        return redirect(url_for('dashboard.index'))

    if request.method == 'GET':
        return render_template('auth/login.html')

    # Handle POST
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)
    if isinstance(remember, str): remember = remember.lower() == 'on'
    
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user, remember=remember)
        
        if request.is_json:
            return jsonify({
                "message": "Login Successful!", 
                "status": "success",
                "user": {"id": user.id, "username": user.username, "email": user.email, "is_premium": user.is_premium}
            }), 200
            
        flash("Login Successful!", "success")
        return redirect(url_for('dashboard.index'))
    else:
        msg = "Login Unsuccessful. Please check email and password"
        if request.is_json:
            return jsonify({"message": msg, "status": "danger"}), 401
            
        flash(msg, "danger")
        return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    if request.method == 'POST' and request.is_json:
        return jsonify({"message": "You have been logged out.", "status": "info"}), 200
        
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

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
