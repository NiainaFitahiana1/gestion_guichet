from flask import Blueprint,render_template


guichet_bp = Blueprint('guichet_bp', __name__)

@guichet_bp.route("/", methods=["GET"])
def index():
    return render_template("guichetier/index.html")