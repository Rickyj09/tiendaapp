from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.blueprints.categorias import categorias_bp
from app.extensions import db
from app.models.categoria import Categoria


@categorias_bp.route("/")
@login_required
def index():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    return render_template("categorias/index.html", categorias=categorias)


@categorias_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        activo = True if request.form.get("activo") == "on" else False

        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "danger")
            return render_template("categorias/form.html", categoria=None)

        existe = Categoria.query.filter(db.func.lower(Categoria.nombre) == nombre.lower()).first()
        if existe:
            flash("Ya existe una categoría con ese nombre.", "warning")
            return render_template("categorias/form.html", categoria=None)

        categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion if descripcion else None,
            activo=activo
        )

        db.session.add(categoria)
        db.session.commit()

        flash("Categoría creada correctamente.", "success")
        return redirect(url_for("categorias.index"))

    return render_template("categorias/form.html", categoria=None)


@categorias_bp.route("/<int:categoria_id>/editar", methods=["GET", "POST"])
@login_required
def editar(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        activo = True if request.form.get("activo") == "on" else False

        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "danger")
            return render_template("categorias/form.html", categoria=categoria)

        existe = Categoria.query.filter(
            db.func.lower(Categoria.nombre) == nombre.lower(),
            Categoria.id != categoria.id
        ).first()

        if existe:
            flash("Ya existe otra categoría con ese nombre.", "warning")
            return render_template("categorias/form.html", categoria=categoria)

        categoria.nombre = nombre
        categoria.descripcion = descripcion if descripcion else None
        categoria.activo = activo

        db.session.commit()

        flash("Categoría actualizada correctamente.", "success")
        return redirect(url_for("categorias.index"))

    return render_template("categorias/form.html", categoria=categoria)


@categorias_bp.route("/<int:categoria_id>/toggle", methods=["POST"])
@login_required
def toggle_estado(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    categoria.activo = not categoria.activo
    db.session.commit()

    if categoria.activo:
        flash("Categoría activada correctamente.", "success")
    else:
        flash("Categoría inactivada correctamente.", "info")

    return redirect(url_for("categorias.index"))