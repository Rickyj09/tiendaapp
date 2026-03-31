from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.inventario import inventario_bp
from app.extensions import db
from app.models.entrada_inventario import EntradaInventario
from app.models.producto import Producto


def _to_decimal(valor, default=""):
    try:
        texto = (valor or "").strip().replace(",", ".")
        if texto == "":
            texto = default
        if texto == "":
            return None
        return Decimal(texto)
    except (InvalidOperation, AttributeError):
        return None


def _to_int(valor):
    try:
        texto = (valor or "").strip()
        if texto == "":
            return None
        return int(texto)
    except (ValueError, AttributeError):
        return None


@inventario_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()

    query = EntradaInventario.query.join(Producto).order_by(EntradaInventario.fecha.desc())

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(like),
                Producto.codigo.ilike(like),
                Producto.codigo_barras.ilike(like)
            )
        )

    entradas = query.all()
    return render_template("inventario/index.html", entradas=entradas, q=q)


@inventario_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre.asc()).all()

    if not productos:
        flash("Primero debes crear al menos un producto activo.", "warning")
        return redirect(url_for("productos.index"))

    if request.method == "POST":
        producto_id = request.form.get("producto_id", type=int)
        cantidad = _to_int(request.form.get("cantidad"))
        costo_unitario = _to_decimal(request.form.get("costo_unitario"))
        observacion = request.form.get("observacion", "").strip()

        if not producto_id:
            flash("Debes seleccionar un producto.", "danger")
            return render_template("inventario/form.html", productos=productos)

        producto = Producto.query.filter_by(id=producto_id, activo=True).first()
        if not producto:
            flash("El producto seleccionado no es válido.", "danger")
            return render_template("inventario/form.html", productos=productos)

        if cantidad is None or cantidad <= 0:
            flash("La cantidad debe ser un entero mayor a cero.", "danger")
            return render_template("inventario/form.html", productos=productos)

        if costo_unitario is not None and costo_unitario < 0:
            flash("El costo unitario no es válido.", "danger")
            return render_template("inventario/form.html", productos=productos)

        entrada = EntradaInventario(
            producto_id=producto.id,
            usuario_id=current_user.id,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            observacion=observacion if observacion else None
        )

        producto.stock_actual += cantidad

        if costo_unitario is not None:
            producto.costo = costo_unitario

        db.session.add(entrada)
        db.session.commit()

        flash("Entrada de inventario registrada correctamente.", "success")
        return redirect(url_for("inventario.index"))

    return render_template("inventario/form.html", productos=productos)