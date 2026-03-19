from flask import Blueprint, jsonify
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
import json

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/test-db", methods=["GET"])
def test_db():
    """Verify database connection by performing a simple CRUD operation."""
    try:
        # 1. Create a dummy user
        test_user = User(
            username="testuser_supabase",
            email="test_supabase@example.com",
            password_hash="dummy_hash"
        )
        db.session.add(test_user)
        db.session.commit()
        
        # 2. Create a dummy resume
        test_resume = Resume(
            user_id=test_user.id,
            title="Test Supabase Resume",
            data=json.dumps({"test": "data"}),
            template_id="template1"
        )
        db.session.add(test_resume)
        db.session.commit()
        
        # 3. Query back
        retrieved_user = User.query.filter_by(email="test_supabase@example.com").first()
        resume_count = Resume.query.filter_by(user_id=test_user.id).count()
        
        # 4. Cleanup
        db.session.delete(test_resume)
        db.session.delete(test_user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Database connection verified!",
            "details": {
                "user_retrieved": retrieved_user.username if retrieved_user else "Failed",
                "resumes_found": resume_count
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Database test failed: {str(e)}"
        }), 500
