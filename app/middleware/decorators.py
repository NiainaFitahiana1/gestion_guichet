from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                flash("Accès non autorisé", "danger")
                return redirect(url_for("dashboard.index"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
