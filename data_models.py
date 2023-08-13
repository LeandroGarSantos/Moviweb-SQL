from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define the UserMovie association table
user_movie_association = db.Table('user_movie_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)


class User(db.Model):
    """
        Model class representing a user.

        Attributes:
            id (int): The primary key for the user.
            username (str): The username of the user.
            movies (relationship): A relationship to the Movie model.

        Methods:
            __repr__: Returns a string representation of the user.
            add_user: Adds a new user to the database.
            delete_user: Deletes a user from the database.

        """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    movies = db.relationship('Movie', backref='user', lazy=True)

    def __repr__(self):
        return f"{self.id}, username='{self.username}"

    @classmethod
    def add_user(cls, username):
        new_user = cls(username=username)
        db.session.add(new_user)
        db.session.commit()

    @classmethod
    def delete_user(cls, user_id):
        user = cls.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()


class Movie(db.Model):
    """
    Model class representing a movie.

    Attributes:
        id (int): The primary key for the movie.
        title (str): The title of the movie.
        year (str): The year of release of the movie.
        genre (str): The genre of the movie.
        rating (str): The rating of the movie.
        director (str): The director of the movie.
        user_id (int): The ID of the user who added the movie.
        imdbid (str): The IMDb ID of the movie.
        reviews (relationship): A relationship to the Review model.

    Methods:
        __repr__: Returns a string representation of the movie.
        delete_movie: Deletes a movie from the database.
        update_movie: Updates movie information in the database.
        to_dict: Converts the movie attributes to a dictionary.
        get_reviews: Returns a list of reviews associated with the movie.

    """
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    director = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    imdbid = db.Column(db.String(10), unique=True)  # Define imdbid column
    reviews = db.relationship('Review', backref='movie', lazy=True)

    def __repr__(self):
        return f"ID={self.id}, title='{self.title}', rating='{self.rating}'"

    @classmethod
    def delete_movie(cls, movie_id):
        movie = cls.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()

    @classmethod
    def update_movie(cls, movie_id, user_id):
        movie = cls.query.get(movie_id)
        if movie:
            movie.title = movie_id.get('title', movie.title)
            movie.year = movie_id.get('year', movie.year)
            movie.genre = movie_id.get('genre', movie.genre)
            movie.rating = movie_id.get('rating', movie.rating)
            movie.director = movie_id.get('director', movie.director)
            movie.imdbid = movie_id.get('imdbid', movie.imdbid)
            # Update more attributes as needed

            db.session.commit()
            return True  # Return True to indicate successful update
        else:
            return False  # Return False if movie doesn't exist

    @classmethod
    def update_movie_info(cls, movie_id, new_title, new_rating):
        movie = cls.query.get(movie_id)
        if movie:
            movie.title = new_title
            movie.rating = new_rating
            db.session.commit()

    def to_dict(self):
        return {
            'Id': self.id,
            'Title': self.title,
            'Year': self.year,
            'Genre': self.genre,
            'Director': self.director,
            'Rating': self.rating,
            # Add more attributes as needed
        }

    def get_reviews(self):
        return Review.query.filter_by(movie_id=self.id).all()


class Review(db.Model):
    """
        Model class representing a review for a movie.

        Attributes:
            id (int): The primary key for the review.
            user_id (int): The ID of the user who wrote the review.
            movie_id (int): The ID of the movie being reviewed.
            review_text (str): The text of the review.
            rating (int): The rating given in the review.

        Methods:
            __repr__: Returns a string representation of the review.
            add_review: Adds a new review to the database.
            delete_review: Deletes a review from the database.
            update_review: Updates a review in the database.
            get_reviews_for_movie: Returns a list of reviews for a specific movie.

        """
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    review_text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Review(id={self.id}, movie_id={self.movie_id}, user_id={self.user_id}, rating={self.rating})"

    @classmethod
    def add_review(cls, user_id, movie_id, review_text, rating):
        new_review = cls(user_id=user_id, movie_id=movie_id, review_text=review_text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

    @classmethod
    def delete_review(cls, review_id):
        review = cls.query.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()

    @classmethod
    def update_review(cls, review_id, new_review_text, new_rating):
        review = cls.query.get(review_id)
        if review:
            review.review_text = new_review_text
            review.rating = new_rating
            db.session.commit()

    @classmethod
    def get_reviews_for_movie(cls, movie_id):
        return cls.query.filter_by(movie_id=movie_id).all()

