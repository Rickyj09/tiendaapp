from decimal import Decimal, InvalidOperation
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.ventas import ventas_bp
from app.extensions import db
from app.models.producto import Producto
from app.models.venta import Venta
from app.models.venta_detalle import VentaDetalle
from flask import render_template, request, redirect, url_for, flash, jsonify


def _to_int(valor):
    try:
        texto = (valor or "").strip()
        if texto == "":
            return None
        return int(texto)
    except (ValueError, AttributeError):
        return None


def generar_numero_venta():
    ultimo = Venta.query.order_by(Venta.id.desc()).first()
    siguiente = 1 if not ultimo else ultimo.id + 1
    return f"VTA-{siguiente:06d}"


@ventas_bp.route("/")
@login_required
def index():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template("ventas/index.html", ventas=ventas)


@ventas_bp.route("/buscar-producto")
@login_required
def buscar_producto():
    codigo = request.args.get("codigo", "").strip()

    if not codigo:
        return jsonify({"ok": False, "mensaje": "Código vacío."}), 400

    producto = Producto.query.filter_by(codigo_barras=codigo, activo=True).first()

    if not producto:
        return jsonify({"ok": False, "mensaje": "Producto no encontrado."}), 404

    if producto.stock_actual <= 0:
        return jsonify({
            "ok": False,
            "mensaje": f"El producto '{producto.nombre}' no tiene stock disponible."
        }), 400

    return jsonify({
        "ok": True,
        "producto": {
            "id": producto.id,
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "codigo_barras": producto.codigo_barras,
            "precio_venta": float(producto.precio_venta),
            "stock_actual": producto.stock_actual
        }
    })

@ventas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre.asc()).all()

    if not productos:
        flash("Primero debes crear al menos un producto activo.", "warning")
        return redirect(url_for("productos.index"))

    if request.method == "POST":
        metodo_pago = request.form.get("metodo_pago", "efectivo").strip().lower()
        observacion = request.form.get("observacion", "").strip()

        producto_ids = request.form.getlist("producto_id[]")
        cantidades = request.form.getlist("cantidad[]")

        if not producto_ids:
            flash("Debes agregar al menos un producto a la venta.", "danger")
            return render_template("ventas/nueva.html", productos=productos)

        metodos_validos = {"efectivo", "transferencia", "mixto"}
        if metodo_pago not in metodos_validos:
            flash("El método de pago no es válido.", "danger")
            return render_template("ventas/nueva.html", productos=productos)

        items = []
        errores = False

        for i in range(len(producto_ids)):
            producto_id = _to_int(producto_ids[i])
            cantidad = _to_int(cantidades[i]) if i < len(cantidades) else None

            if not producto_id and not cantidad:
                continue

            if not producto_id:
                flash(f"Fila {i + 1}: debes seleccionar un producto.", "danger")
                errores = True
                continue

            if cantidad is None or cantidad <= 0:
                flash(f"Fila {i + 1}: la cantidad debe ser mayor a cero.", "danger")
                errores = True
                continue

            producto = Producto.query.filter_by(id=producto_id, activo=True).first()
            if not producto:
                flash(f"Fila {i + 1}: el producto seleccionado no es válido.", "danger")
                errores = True
                continue

            if producto.stock_actual < cantidad:
                flash(
                    f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock_actual}.",
                    "danger"
                )
                errores = True
                continue

            items.append({
                "producto": producto,
                "cantidad": cantidad,
                "precio_unitario": Decimal(producto.precio_venta),
                "subtotal": Decimal(producto.precio_venta) * cantidad
            })

        if errores:
            return render_template("ventas/nueva.html", productos=productos)

        if not items:
            flash("Debes agregar al menos un producto válido a la venta.", "danger")
            return render_template("ventas/nueva.html", productos=productos)

        numero_venta = generar_numero_venta()
        total = sum(item["subtotal"] for item in items)

        venta = Venta(
            numero_venta=numero_venta,
            fecha=datetime.utcnow(),
            total=total,
            metodo_pago=metodo_pago,
            observacion=observacion if observacion else None,
            usuario_id=current_user.id
        )

        db.session.add(venta)
        db.session.flush()

        for item in items:
            detalle = VentaDetalle(
                venta_id=venta.id,
                producto_id=item["producto"].id,
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                subtotal=item["subtotal"]
            )
            db.session.add(detalle)

            item["producto"].stock_actual -= item["cantidad"]

        db.session.commit()

        flash("Venta registrada correctamente.", "success")
        return redirect(url_for("ventas.detalle", venta_id=venta.id))

    return render_template("ventas/nueva.html", productos=productos)


@ventas_bp.route("/<int:venta_id>")
@login_required
def detalle(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    return render_template("ventas/detalle.html", venta=venta)