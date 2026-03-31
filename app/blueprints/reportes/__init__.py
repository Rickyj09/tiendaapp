from flask import Blueprint

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")

from app.blueprints.reportes import routes