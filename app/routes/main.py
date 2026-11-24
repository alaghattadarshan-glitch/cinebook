"""
Main Routes: Home, Location selector, Discovery.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models.movie import Movie
from app.models.theatre import Theatre

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Cinematic Homepage inspired by BookMyShow."""
    now_showing = Movie.query.filter_by(category="NOW_SHOWING", is_active=True).all()
    trending = Movie.query.filter_by(category="TRENDING", is_active=True).all()
    coming_soon = Movie.query.filter_by(category="COMING_SOON", is_active=True).all()
    top_rated = Movie.query.filter_by(category="TOP_RATED", is_active=True).all()
    theatres = Theatre.query.filter_by(is_active=True).limit(6).all()

    # Featured banner movie
    featured_movie = now_showing[0] if now_showing else (trending[0] if trending else None)

    return render_template(
        "main/index.html",
        now_showing=now_showing,
        trending=trending,
        coming_soon=coming_soon,
        top_rated=top_rated,
        theatres=theatres,
        featured_movie=featured_movie
    )


@main_bp.route("/set-city", methods=["POST"])
def set_city():
    """Updates user's selected city in session."""
    city = request.form.get("city", "Mumbai")
    session["selected_city"] = city
    referrer = request.referrer or url_for("main.index")
    return redirect(referrer)


@main_bp.route("/explore")
def explore():
    """Movie Discovery Page with full filtering by title, genre, language and rating."""
    query = request.args.get("q", "")
    genre = request.args.get("genre", "All")
    language = request.args.get("language", "All")
    min_rating = float(request.args.get("rating", 0.0))

    movies_query = Movie.query.filter_by(is_active=True)

    if query:
        movies_query = movies_query.filter(Movie.title.ilike(f"%{query}%"))
    if genre and genre != "All":
        movies_query = movies_query.filter(Movie.genre.ilike(f"%{genre}%"))
    if language and language != "All":
        movies_query = movies_query.filter(Movie.language.ilike(f"%{language}%"))
    if min_rating > 0:
        movies_query = movies_query.filter(Movie.rating >= min_rating)

    movies = movies_query.order_by(Movie.rating.desc()).all()

    return render_template(
        "main/discovery.html",
        movies=movies,
        search_query=query,
        selected_genre=genre,
        selected_language=language,
        selected_rating=min_rating
    )
