"""
Movie Entity & TMDB Integration Mapping.
Demonstrates:
- Encapsulation: Poster URL generation with guaranteed safe fallbacks
- Association: Movies are scheduled into Shows
"""

from app.models.base import db, BaseModel


class Movie(BaseModel):
    """
    Movie Model.
    Stores metadata synchronized from TMDB or created via Admin dashboard.
    """
    __tablename__ = "movies"

    tmdb_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    poster_path = db.Column(db.String(255), nullable=True)
    backdrop_path = db.Column(db.String(255), nullable=True)
    release_date = db.Column(db.String(50), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    genre = db.Column(db.String(150), nullable=True)
    language = db.Column(db.String(50), default="English")
    runtime = db.Column(db.Integer, default=120)  # minutes
    trailer_url = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), default="NOW_SHOWING", index=True)  # NOW_SHOWING, COMING_SOON, TRENDING, TOP_RATED, POPULAR
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    shows = db.relationship("Show", back_populates="movie", cascade="all, delete-orphan", lazy="dynamic")

    # Safe Fallback constants (Encapsulation)
    FALLBACK_POSTER = "/static/images/poster-fallback.svg"
    FALLBACK_BACKDROP = "/static/images/banner-fallback.svg"
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
    TMDB_ORIGINAL_BASE = "https://image.tmdb.org/t/p/original"

    @property
    def poster_url(self) -> str:
        """
        Encapsulation: Computes the absolute, valid poster image URL.
        Falls back to a clean local SVG placeholder if TMDB poster is absent.
        """
        if self.poster_path:
            if self.poster_path.startswith("http"):
                return self.poster_path
            return f"{self.TMDB_IMAGE_BASE}{self.poster_path}"
        return self.FALLBACK_POSTER

    @property
    def backdrop_url(self) -> str:
        """Encapsulation: Backdrop URL with guaranteed fallback."""
        if self.backdrop_path:
            if self.backdrop_path.startswith("http"):
                return self.backdrop_path
            return f"{self.TMDB_ORIGINAL_BASE}{self.backdrop_path}"
        return self.FALLBACK_BACKDROP

    def __repr__(self) -> str:
        return f"<Movie id={self.id} title='{self.title}' rating={self.rating}>"
