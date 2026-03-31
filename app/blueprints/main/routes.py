from flask import render_template, redirect, url_for
from flask_login import login_required

from app.blueprints.main import main_bp


@main_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard/index.html")