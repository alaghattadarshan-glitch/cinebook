"""
Movie Detail Routes.
"""

from flask import Blueprint, render_template, abort, session
from app.models.movie import Movie
from app.models.theatre import Theatre
from app.models.show import Show

movies_bp = Blueprint("movies", __name__)


@movies_bp.route("/<int:movie_id>")
def detail(movie_id: int):
    """Movie Information Page."""
    movie = Movie.query.get_or_404(movie_id)
    city = session.get("selected_city", "Mumbai")

    # Find shows for this movie in the user's selected city
    theatres = Theatre.query.filter_by(city=city, is_active=True).all()
    theatre_ids = [t.id for t in theatres]

    available_shows = Show.query.filter(
        Show.movie_id == movie.id,
        Show.is_active.is_(True)
    ).all()

    # Group shows by theatre
    shows_by_theatre = {}
    for s in available_shows:
        t = s.theatre
        if t and (t.city == city or not city):
            if t not in shows_by_theatre:
                shows_by_theatre[t] = []
            shows_by_theatre[t].append(s)

    return render_template(
        "movies/detail.html",
        movie=movie,
        shows_by_theatre=shows_by_theatre,
        selected_city=city
    )
