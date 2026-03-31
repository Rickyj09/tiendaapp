from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.blueprints.productos import productos_bp
from app.extensions import db
from app.models.categoria import Categoria
from app.models.producto import Producto


def _to_decimal(valor, default="0.00"):
    try:
        texto = (valor or "").strip().replace(",", ".")
        if texto == "":
            texto = default
        return Decimal(texto)
    except (InvalidOperation, AttributeError):
        return None


def _to_int(valor, default=0):
    try:
        texto = (valor or "").strip()
        if texto == "":
            return default
        return int(texto)
    except (ValueError, AttributeError):
        return None


@productos_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()

    query = Producto.query.join(Categoria).order_by(Producto.nombre.asc())

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(like),
                Producto.codigo.ilike(like),
                Producto.codigo_barras.ilike(like),
                Categoria.nombre.ilike(like)
            )
        )

    productos = query.all()
    return render_template("productos/index.html", productos=productos, q=q)


@productos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    categorias = Categoria.query.filter_by(activo=True).order_by(Categoria.nombre.asc()).all()

    if not categorias:
        flash("Primero debes crear al menos una categoría activa.", "warning")
        return redirect(url_for("categorias.index"))

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria_id = request.form.get("categoria_id", type=int)
        precio_venta = _to_decimal(request.form.get("precio_venta"))
        costo = _to_decimal(request.form.get("costo"), default="")
        stock_actual = _to_int(request.form.get("stock_actual"), default=0)
        stock_minimo = _to_int(request.form.get("stock_minimo"), default=0)
        unidad_medida = request.form.get("unidad_medida", "").strip()
        codigo_barras = request.form.get("codigo_barras", "").strip()
        activo = True if request.form.get("activo") == "on" else False

        if not codigo:
            flash("El código interno es obligatorio.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if not nombre:
            flash("El nombre del producto es obligatorio.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if not categoria_id:
            flash("Debes seleccionar una categoría.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        categoria = Categoria.query.filter_by(id=categoria_id, activo=True).first()
        if not categoria:
            flash("La categoría seleccionada no es válida.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if precio_venta is None or precio_venta < 0:
            flash("El precio de venta no es válido.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if costo is not None and costo < 0:
            flash("El costo no es válido.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if stock_actual is None or stock_actual < 0:
            flash("El stock actual no es válido.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if stock_minimo is None or stock_minimo < 0:
            flash("El stock mínimo no es válido.", "danger")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        existe_codigo = Producto.query.filter(db.func.lower(Producto.codigo) == codigo.lower()).first()
        if existe_codigo:
            flash("Ya existe un producto con ese código.", "warning")
            return render_template("productos/form.html", producto=None, categorias=categorias)

        if codigo_barras:
            existe_barras = Producto.query.filter(Producto.codigo_barras == codigo_barras).first()
            if existe_barras:
                flash("Ya existe un producto con ese código de barras.", "warning")
                return render_template("productos/form.html", producto=None, categorias=categorias)

        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion if descripcion else None,
            categoria_id=categoria_id,
            precio_venta=precio_venta,
            costo=costo,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo,
            unidad_medida=unidad_medida if unidad_medida else None,
            codigo_barras=codigo_barras if codigo_barras else None,
            activo=activo
        )

        db.session.add(producto)
        db.session.commit()

        flash("Producto creado correctamente.", "success")
        return redirect(url_for("productos.index"))

    return render_template("productos/form.html", producto=None, categorias=categorias)


@productos_bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
@login_required
def editar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    categorias = Categoria.query.filter_by(activo=True).order_by(Categoria.nombre.asc()).all()

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria_id = request.form.get("categoria_id", type=int)
        precio_venta = _to_decimal(request.form.get("precio_venta"))
        costo = _to_decimal(request.form.get("costo"), default="")
        stock_actual = _to_int(request.form.get("stock_actual"), default=0)
        stock_minimo = _to_int(request.form.get("stock_minimo"), default=0)
        unidad_medida = request.form.get("unidad_medida", "").strip()
        codigo_barras = request.form.get("codigo_barras", "").strip()
        activo = True if request.form.get("activo") == "on" else False

        if not codigo:
            flash("El código interno es obligatorio.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if not nombre:
            flash("El nombre del producto es obligatorio.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if not categoria_id:
            flash("Debes seleccionar una categoría.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        categoria = Categoria.query.filter_by(id=categoria_id, activo=True).first()
        if not categoria:
            flash("La categoría seleccionada no es válida.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if precio_venta is None or precio_venta < 0:
            flash("El precio de venta no es válido.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if costo is not None and costo < 0:
            flash("El costo no es válido.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if stock_actual is None or stock_actual < 0:
            flash("El stock actual no es válido.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if stock_minimo is None or stock_minimo < 0:
            flash("El stock mínimo no es válido.", "danger")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        existe_codigo = Producto.query.filter(
            db.func.lower(Producto.codigo) == codigo.lower(),
            Producto.id != producto.id
        ).first()
        if existe_codigo:
            flash("Ya existe otro producto con ese código.", "warning")
            return render_template("productos/form.html", producto=producto, categorias=categorias)

        if codigo_barras:
            existe_barras = Producto.query.filter(
                Producto.codigo_barras == codigo_barras,
                Producto.id != producto.id
            ).first()
            if existe_barras:
                flash("Ya existe otro producto con ese código de barras.", "warning")
                return render_template("productos/form.html", producto=producto, categorias=categorias)

        producto.codigo = codigo
        producto.nombre = nombre
        producto.descripcion = descripcion if descripcion else None
        producto.categoria_id = categoria_id
        producto.precio_venta = precio_venta
        producto.costo = costo
        producto.stock_actual = stock_actual
        producto.stock_minimo = stock_minimo
        producto.unidad_medida = unidad_medida if unidad_medida else None
        producto.codigo_barras = codigo_barras if codigo_barras else None
        producto.activo = activo

        db.session.commit()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos.index"))

    return render_template("productos/form.html", producto=producto, categorias=categorias)


@productos_bp.route("/<int:producto_id>/toggle", methods=["POST"])
@login_required
def toggle_estado(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.activo = not producto.activo
    db.session.commit()

    if producto.activo:
        flash("Producto activado correctamente.", "success")
    else:
        flash("Producto inactivado correctamente.", "info")

    return redirect(url_for("productos.index"))