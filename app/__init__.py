import os
from flask import Flask

from app.config import Config
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models.usuario import Usuario
    from app.models import Categoria, Producto, EntradaInventario, Venta, VentaDetalle
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.categorias import categorias_bp
    from app.blueprints.productos import productos_bp
    from app.blueprints.inventario import inventario_bp
    from app.blueprints.ventas import ventas_bp
    from app.blueprints.reportes import reportes_bp

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(reportes_bp)

    return app