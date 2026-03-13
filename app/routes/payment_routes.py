from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db, razorpay_client
from app.models.payment import Payment
from app.models.resume import Resume
from datetime import datetime, timedelta
import pytz
import json

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/create-order/<int:resume_id>", methods=["POST"])
@login_required
def create_order(resume_id):
    """Create Razorpay order for single download"""
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Create Razorpay order
        order_data = {
            "amount": 5000,  # ₹50 in paisa
            "currency": "INR",
            "receipt": f"download_{resume_id}_{current_user.id}",
            "notes": {
                "user_id": str(current_user.id),
                "resume_id": str(resume_id),
                "payment_type": "single_download"
            }
        }

        order = razorpay_client.order.create(order_data)

        # Save payment record
        payment = Payment(
            user_id=current_user.id,
            razorpay_order_id=order["id"],
            amount=5000,
            currency="INR",
            payment_type="single_download",
            resume_id=resume_id
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": razorpay_client.auth[0]  # Razorpay key ID
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/create-premium-order", methods=["POST"])
@login_required
def create_premium_order():
    """Create Razorpay order for premium subscription"""
    try:
        # Create Razorpay order for ₹1,00,000
        order_data = {
            "amount": 10000000,  # ₹1,00,000 in paisa
            "currency": "INR",
            "receipt": f"premium_{current_user.id}_{datetime.now().timestamp()}",
            "notes": {
                "user_id": str(current_user.id),
                "payment_type": "premium_subscription"
            }
        }

        order = razorpay_client.order.create(order_data)

        # Save payment record
        payment = Payment(
            user_id=current_user.id,
            razorpay_order_id=order["id"],
            amount=10000000,
            currency="INR",
            payment_type="premium_subscription"
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": razorpay_client.auth[0]  # Razorpay key ID
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/verify-payment", methods=["POST"])
@login_required
def verify_payment():
    """Verify Razorpay payment and update user status"""
    try:
        data = request.get_json()
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        # Verify signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Find and update payment record
        payment = Payment.query.filter_by(
            razorpay_order_id=razorpay_order_id,
            user_id=current_user.id
        ).first()

        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = "paid"

        if payment.payment_type == "single_download":
            # Single download payment - allow download
            db.session.commit()
            return jsonify({"success": True, "redirect": url_for("dashboard.download", resume_id=payment.resume_id)})

        elif payment.payment_type == "premium_subscription":
            # Premium subscription - activate for 45 days
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.now(ist)
            premium_expiry = now_ist + timedelta(days=45)

            current_user.is_premium = True
            current_user.premium_expiry = premium_expiry
            payment.premium_expiry = premium_expiry

            db.session.commit()

            return jsonify({"success": True, "redirect": url_for("dashboard.index")})

        return jsonify({"error": "Invalid payment type"}), 400

    except razorpay.errors.SignatureVerificationError:
        return jsonify({"error": "Payment verification failed"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/payment-success")
@login_required
def payment_success():
    """Payment success page"""
    return render_template("payment/success.html")

@payment_bp.route("/payment-failed")
@login_required
def payment_failed():
    """Payment failed page"""
    return render_template("payment/failed.html")