"""
Admin Dashboard Routes.
Demonstrates:
- Role-based Access Control (RBAC) via @admin_required decorator
- Managing Movies, Theatres, Screens, Shows, and Bookings
- Synchronizing TMDB metadata
- Revenue calculation and system diagnostics
"""

from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user

from app.models.base import db
from app.models.user import BaseUser, Customer, Admin
from app.models.movie import Movie
from app.models.theatre import Theatre, Screen, Seat
from app.models.show import Show, ShowSeat
from app.models.booking import Booking, Payment
from app.services.tmdb_service import TMDBService

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash("Administrator privilege required to access this resource.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/")
@admin_required
def dashboard():
    """Main Admin Dashboard Overview."""
    total_users = Customer.query.count()
    total_movies = Movie.query.count()
    total_theatres = Theatre.query.count()
    total_bookings = Booking.query.count()

    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status="SUCCESS").scalar() or 0.0

    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_movies=total_movies,
        total_theatres=total_theatres,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        recent_bookings=recent_bookings
    )


@admin_bp.route("/movies")
@admin_required
def movies_list():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    return render_template("admin/movies.html", movies=movies)


@admin_bp.route("/movies/sync-tmdb", methods=["POST"])
@admin_required
def sync_tmdb():
    tmdb_svc = TMDBService()
    count = tmdb_svc.sync_catalog(force_refresh=True)
    flash(f"Successfully synchronized {count} movies with TMDB!", "success")
    return redirect(url_for("admin.movies_list"))


@admin_bp.route("/theatres")
@admin_required
def theatres_list():
    theatres = Theatre.query.all()
    return render_template("admin/theatres.html", theatres=theatres)


@admin_bp.route("/shows")
@admin_required
def shows_list():
    shows = Show.query.order_by(Show.start_time.desc()).all()
    movies = Movie.query.filter_by(is_active=True).all()
    screens = Screen.query.filter_by(is_active=True).all()
    return render_template("admin/shows.html", shows=shows, movies=movies, screens=screens)


@admin_bp.route("/shows/create", methods=["POST"])
@admin_required
def create_show():
    movie_id = int(request.form.get("movie_id"))
    screen_id = int(request.form.get("screen_id"))
    start_time_str = request.form.get("start_time")
    base_price = float(request.form.get("base_price", 200.0))

    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
    movie = Movie.query.get_or_404(movie_id)
    end_time = start_time + timedelta(minutes=movie.runtime + 20)

    show = Show(
        movie_id=movie_id,
        screen_id=screen_id,
        start_time=start_time,
        end_time=end_time,
        base_price=base_price
    )
    db.session.add(show)
    db.session.flush()

    # Generate ShowSeat inventory
    screen = Screen.query.get_or_404(screen_id)
    for seat in screen.seats:
        multiplier = 2.0 if seat.tier == "RECLINER" else (1.4 if seat.tier == "PREMIUM" else 1.0)
        show_seat = ShowSeat(
            show_id=show.id,
            seat_id=seat.id,
            price=round(base_price * multiplier, 2),
            status="AVAILABLE"
        )
        db.session.add(show_seat)

    db.session.commit()
    flash("Show successfully scheduled!", "success")
    return redirect(url_for("admin.shows_list"))


@admin_bp.route("/bookings")
@admin_required
def bookings_list():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)
