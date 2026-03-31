from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from app.blueprints.auth import auth_bp
from app.models.usuario import Usuario


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        usuario = Usuario.query.filter_by(username=username, activo=True).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash("Inicio de sesión correcto.", "success")
            return redirect(url_for("main.dashboard"))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))