from flask import Blueprint

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

from app.blueprints.productos import routes