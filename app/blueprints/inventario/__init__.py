from flask import Blueprint

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")

from app.blueprints.inventario import routes