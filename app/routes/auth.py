"""
Authentication Routes: Register, Login, Logout, Profile & History.
Demonstrates:
- Clean registration with password hashing
- Session management via Flask-Login
- Customer profile and booking history
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.base import db
from app.models.user import Customer, BaseUser

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if BaseUser.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return render_template("auth/register.html")

        try:
            customer = Customer(
                name=name,
                email=email,
                password=password,
                phone=phone
            )
            db.session.add(customer)
            db.session.commit()
            login_user(customer)
            flash("Welcome to CINEBOOK! Registration successful.", "success")
            return redirect(url_for("main.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error registering user: {str(e)}", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = BaseUser.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.name}!", "success")
            next_url = request.args.get("next")
            if user.is_admin():
                return redirect(next_url or url_for("admin.dashboard"))
            return redirect(next_url or url_for("main.index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    """Customer Profile with Upcoming Bookings and History."""
    bookings = current_user.bookings.order_by(BaseUser.bookings.entity.created_at.desc()).all()
    return render_template("auth/profile.html", user=current_user, bookings=bookings)
