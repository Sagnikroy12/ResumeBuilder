# from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
# from flask_login import login_user, logout_user, current_user, login_required
# from app.models.user import User
# from app.extensions import db, bcrypt

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         if request.is_json:
#             return jsonify({"message": "Already authenticated", "status": "success"}), 200
#         return redirect(url_for('dashboard.index'))
        
#     if request.method == 'GET':
#         return render_template('auth/register.html')

#     # Handle POST
#     if request.is_json:
#         data = request.get_json()
#     else:
#         data = request.form

#     email = data.get('email', '').strip().lower()
#     password = data.get('password')
#     # Use email as username to satisfy model constraint and ensure uniqueness
#     username = email if email else None
    
#     if not email or not password:
#         msg = "Missing required fields."
#         if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
#         flash(msg, "danger")
#         return render_template('auth/register.html')

#     if len(password) < 8:
#         msg = "Password must be at least 8 characters long."
#         if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
#         flash(msg, "danger")
#         return render_template('auth/register.html')

#     user_exists = User.query.filter_by(username=username).first()
#     email_exists = User.query.filter_by(email=email).first()
    
#     if user_exists:
#         msg = "Username is already taken."
#         if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
#         flash(msg, "danger")
#         return render_template('auth/register.html')
#     elif email_exists:
#         msg = "Email is already registered."
#         if request.is_json: return jsonify({"message": msg, "status": "danger"}), 400
#         flash(msg, "danger")
#         return render_template('auth/register.html')
#     else:
#         hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
#         new_user = User(username=username, email=email, password_hash=hashed_pw)
#         db.session.add(new_user)
#         db.session.commit()
        
#         msg = "Your account has been created! Please log in."
#         if request.is_json:
#             return jsonify({"message": msg, "status": "success"}), 201
            
#         flash(msg, "success")
#         return redirect(url_for('auth.login'))

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         if request.is_json:
#             return jsonify({
#                 "message": "Already authenticated", 
#                 "status": "success",
#                 "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email, "is_premium": current_user.is_premium}
#             }), 200
#         return redirect(url_for('dashboard.index'))

#     if request.method == 'GET':
#         return render_template('auth/login.html')

#     # Handle POST
#     if request.is_json:
#         data = request.get_json()
#     else:
#         data = request.form

#     email = data.get('email', '').strip().lower()
#     password = data.get('password')
#     remember = data.get('remember', False)
#     if isinstance(remember, str): remember = remember.lower() == 'on'
    
#     import logging
#     logger = logging.getLogger(__name__)
    
#     if not email or not password:
#         logger.warning(f"Login attempt with missing fields. Email present: {bool(email)}, Password present: {bool(password)}")
    
#     user = User.query.filter_by(email=email).first()
    
#     if user and bcrypt.check_password_hash(user.password_hash, password):
#         logger.info(f"Login successful for user '{email}'.")
#         login_user(user, remember=remember)
        
#         if request.is_json:
#             return jsonify({
#                 "message": "Login Successful!", 
#                 "status": "success",
#                 "user": {"id": user.id, "username": user.username, "email": user.email, "is_premium": user.is_premium}
#             }), 200
            
#         flash("Login Successful!", "success")
#         return redirect(url_for('dashboard.index'))
#     else:
#         if not user:
#             logger.warning(f"Login failed: User with email '{email}' not found.")
#         else:
#             logger.warning(f"Login failed: Password mismatch for user '{email}'.")
            
#         msg = "Login Unsuccessful. Please check email and password"
#         if request.is_json:
#             return jsonify({"message": msg, "status": "danger"}), 401
            
#         flash(msg, "danger")
#         return render_template('auth/login.html')

# @auth_bp.route('/logout', methods=['GET', 'POST'])
# @login_required
# def logout():
#     logout_user()
#     if request.method == 'POST' and request.is_json:
#         return jsonify({"message": "You have been logged out.", "status": "info"}), 200
        
#     flash("You have been logged out.", "info")
#     return redirect(url_for('auth.login'))

# @auth_bp.route('/me', methods=['GET'])
# def get_current_user():
#     if current_user.is_authenticated:
#         return jsonify({
#             "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email, "is_premium": current_user.is_premium}
#         }), 200
#     return jsonify({"user": None}), 200

# @auth_bp.route('/toggle-premium', methods=['POST'])
# @login_required
# def toggle_premium():
#     """Toggle Pro status for master user."""
#     MASTER_EMAIL = "sagnikruproy11@gmail.com"
#     if current_user.email != MASTER_EMAIL:
#         return jsonify({"message": "Unauthorized"}), 403
    
#     current_user.is_premium = not current_user.is_premium
#     db.session.commit()
    
#     status = "Pro" if current_user.is_premium else "Free"
#     return jsonify({
#         "message": f"Account toggled to {status}!", 
#         "is_premium": current_user.is_premium
#     }), 200


from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

def _extract_data():
    """Robustly extract data from JSON or form-encoded request."""
    if request.is_json:
        return request.get_json() or {}
    # Accept JSON without header, try to parse form fields
    try:
        return request.get_json(force=True) or {}
    except Exception:
        return request.form or {}

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({"message": "Already authenticated", "status": "success"}), 200
        return redirect(url_for('dashboard.index'))

    if request.method == 'GET':
        return render_template('auth/register.html')

    data = _extract_data()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')

    if not email or not password:
        msg = "Missing required fields."
        current_app.logger.warning("Register attempt missing fields: email present=%s", bool(email))
        if request.is_json:
            return jsonify({"message": msg, "status": "danger"}), 400
        flash(msg, "danger")
        return render_template('auth/register.html')

    if len(password) < 8:
        msg = "Password must be at least 8 characters long."
        if request.is_json:
            return jsonify({"message": msg, "status": "danger"}), 400
        flash(msg, "danger")
        return render_template('auth/register.html')

    username = email  # use email as username to satisfy model constraints

    # Race conditions still possible; handle IntegrityError on commit
    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.warning("Register IntegrityError for email=%s: %s", email, str(e))
        msg = "A user with that email or username already exists."
        if request.is_json:
            return jsonify({"message": msg, "status": "danger"}), 409
        flash(msg, "danger")
        return render_template('auth/register.html')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Unexpected error during registration for email=%s", email)
        msg = "Registration failed due to server error."
        if request.is_json:
            return jsonify({"message": msg, "status": "danger"}), 500
        flash(msg, "danger")
        return render_template('auth/register.html')

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

    data = _extract_data()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    remember = data.get('remember', False)
    if isinstance(remember, str):
        remember = remember.lower() in ('on', 'true', '1')

    logger = current_app.logger

    if not email or not password:
        logger.warning("Login attempt missing fields. email present=%s", bool(email))
        if request.is_json:
            return jsonify({"message": "Email and password required", "status": "danger"}), 400
        flash("Email and password required", "danger")
        return render_template('auth/login.html')

    try:
        user = User.query.filter_by(email=email).first()
    except Exception:
        logger.exception("Database query error during login for email=%s", email)
        if request.is_json:
            return jsonify({"message": "Login failed", "status": "danger"}), 500
        flash("Login failed", "danger")
        return render_template('auth/login.html')

    if user and user.check_password(password):
        logger.info("Login successful for user %s", email)
        login_user(user, remember=remember)
        if request.is_json:
            return jsonify({
                "message": "Login Successful!",
                "status": "success",
                "user": {"id": user.id, "username": user.username, "email": user.email, "is_premium": user.is_premium}
            }), 200

        flash("Login Successful!", "success")
        return redirect(url_for('dashboard.index'))

    if not user:
        logger.warning("Login failed: user not found: %s", email)
    else:
        logger.warning("Login failed: password mismatch for: %s", email)

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