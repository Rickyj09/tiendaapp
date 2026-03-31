from datetime import datetime, timedelta

from flask import render_template, request
from flask_login import login_required

from app.blueprints.reportes import reportes_bp
from app.models.venta import Venta
from app.models.producto import Producto
from app.models.venta_detalle import VentaDetalle
from app.extensions import db


@reportes_bp.route("/")
@login_required
def dashboard():

    # 🔹 Ventas de hoy
    hoy = datetime.utcnow().date()
    inicio_hoy = datetime.combine(hoy, datetime.min.time())
    fin_hoy = datetime.combine(hoy, datetime.max.time())

    ventas_hoy = Venta.query.filter(
        Venta.fecha >= inicio_hoy,
        Venta.fecha <= fin_hoy
    ).all()

    total_hoy = sum(v.total for v in ventas_hoy)

    # 🔹 Últimos 7 días
    hace_7 = datetime.utcnow() - timedelta(days=7)

    ventas_7 = Venta.query.filter(
        Venta.fecha >= hace_7
    ).all()

    total_7 = sum(v.total for v in ventas_7)

    # 🔹 Productos con stock bajo
    productos_bajo = Producto.query.filter(
        Producto.stock_actual <= Producto.stock_minimo
    ).all()

    # 🔹 Top productos vendidos
    top_productos = db.session.query(
        Producto.nombre,
        db.func.sum(VentaDetalle.cantidad).label("total_vendido")
    ).join(VentaDetalle).group_by(Producto.id).order_by(
        db.desc("total_vendido")
    ).limit(5).all()

    return render_template(
        "reportes/dashboard.html",
        total_hoy=total_hoy,
        total_7=total_7,
        productos_bajo=productos_bajo,
        top_productos=top_productos
    )