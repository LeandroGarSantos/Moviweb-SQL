from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from data_models import db, User, Movie, Review
import os

app = Flask(__name__)


# Define your routes for the API endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    """
        Get a list of all users.

        Returns:
            jsonify: A JSON response containing the list of users.
        """
    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify(users_data)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.sqlite'  # Use your desired database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/api/users/<user_id>/movies', methods=['GET'])
def get_user_movies_api(user_id):
    """
        Get the list of movies for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            jsonify: A JSON response containing the list of movies for the user.
        """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    movies = [{'id': movie.id, 'title': movie.title, 'year': movie.year} for movie in user.movies]
    return jsonify(movies)


@app.route('/api/users/<user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    """
        Add a movie to a user's list of movies.

        Args:
            user_id (int): The ID of the user.

        Returns:
            jsonify: A JSON response confirming the addition of the movie.
        """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    title = data.get('title')
    year = data.get('year')

    if not title or not year:
        return jsonify({'error': 'Title and year are required'}), 400

    movie = Movie(title=title, year=year)
    user.movies.append(movie)
    db.session.commit()

    return jsonify({'message': 'Movie added successfully'})


# Create the database tables
with app.app_context():
    db.create_all()


def fetch_movie_details(movie_title):
    """
        Fetches movie details from the OMDb API based on the provided movie title.

        Args:
            movie_title (str): The title of the movie.

        Returns:
            dict: A dictionary containing the movie details, or an empty dictionary if the API request fails.

        Raises:
            requests.RequestException: If an error occurs during the API request.
        """

    api_key = '7cee3b97'
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}'

    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 200:
            movie_data = response.json()
            return movie_data
        else:
            # Handle the case when the API request fails
            return {}
    except requests.RequestException as e:
        # Handle request exceptions
        print("An error occurred during the API request:", str(e))
        return {}


@app.route('/')
def home():
    """
       Renders the home page of the MovieWeb App.

       Returns:
           str: The rendered HTML template for the home page.
       """
    return render_template('index.html')


@app.route('/users')
def list_users():
    """
        Retrieves and renders a list of users.

        Returns:
            str: The rendered HTML template for the list of users.

        Raises:
            Exception: If an error occurs while retrieving user data.
        """
    try:
        users = User.query.all()
        return render_template('users.html', users=users)
    except Exception as e:
        # Handle exceptions related to getting users
        print("An error occurred while retrieving user data:", str(e))
        return render_template('error.html', error_message="An error occurred while retrieving user data")


@app.route('/users/<user_id>')
def get_user_movies(user_id):
    """
        Retrieves and renders the list of movies for a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The rendered HTML template for the list of movies.

        Raises:
            Exception: If an error occurs while retrieving user movies.
        """
    # try:
    #     user = User.query.get(user_id)
    #
    #     if not user:
    #         return render_template('error.html', error_message="User not found.")
    #
    #     movies = user.movies
    #     return render_template('movies.html', movies=movies, user_id=user_id)
    # except Exception as e:
    #     # Handle exceptions related to getting user movies
    #     print("An error occurred while retrieving user movies:", str(e))
    #     return render_template('error.html', error_message="An error occurred while retrieving user movies")
    try:
        user = User.query.get(user_id)

        if not user:
            return render_template('error.html', error_message="User not found.")

        movies = user.movies
        movies_with_details = []

        for movie in movies:
            movie_details = fetch_movie_details(movie.title)  # Fetch movie details from OMDb API
            combined_movie_data = {**movie.to_dict(), **movie_details}
            movies_with_details.append(combined_movie_data)

        return render_template('movies.html', movies=movies_with_details, user_id=user_id)
    except Exception as e:
        print("An error occurred while retrieving user movies:", str(e))
        return render_template('error.html', error_message="An error occurred while retrieving user movies")


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
        Adds a new user to the system.

        Returns:
            str: The rendered HTML template for adding a user.

        Raises:
            Exception: If an error occurs while adding a user.
        """
    if request.method == 'POST':
        try:
            username = request.form['username']
            User.add_user(username)  # Use the class method to add the user
            return redirect(url_for('list_users'))
        except Exception as e:
            # Handle exceptions related to adding a user
            print("An error occurred while adding a user:", str(e))
            return render_template('error.html', error_message="An error occurred while adding a user")
    return render_template('add_user.html')


@app.route('/users/<user_id>/delete_user', methods=['GET', 'POST'])
def delete_user(user_id):
    """
        Deletes a user from the system.

        Args:
            user_id (str): The ID of the user to be deleted.

        Returns:
            str: The rendered HTML template for deleting a user.

        Raises:
            Exception: If an error occurs while deleting a user.
        """
    if request.method == 'POST':
        try:
            user = User.query.get(user_id)

            if not user:
                return render_template('error.html', error_message="User not found.")

            # Delete user's movies first
            for movie in user.movies:
                db.session.delete(movie)

            db.session.delete(user)
            db.session.commit()

            return redirect(url_for('list_users'))
        except Exception as e:
            # Handle exceptions related to deleting a user
            print("An error occurred while deleting a user:", str(e))
            return render_template('error.html', error_message="An error occurred while deleting a user")

    return render_template('delete_user.html', user_id=user_id)


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
        Adds a new movie to a user's movie list.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The rendered HTML template for adding a movie.

        Raises:
            Exception: If an error occurs while adding a movie.
        """
    if request.method == 'POST':
        try:
            movie_title = request.form['movie_title']
            movie_rating = request.form['movie_rating']

            movie_details = fetch_movie_details(movie_title)

            if not movie_details:
                return render_template('error.html', error_message="Movie details not found.")

            movie_year = movie_details.get('Year', '')
            movie_genre = movie_details.get('Genre', '')
            movie_director = movie_details.get('Director', '')
            movie_imdbid = movie_details.get('imdbID', '')

            movie = Movie(title=movie_title, rating=movie_rating, user_id=user_id, year=movie_year, genre=movie_genre, director=movie_director, imdbid=movie_imdbid)
            db.session.add(movie)
            db.session.commit()

            return redirect(url_for('get_user_movies', user_id=user_id))
        except Exception as e:
            # Handle exceptions related to adding a movie
            print("An error occurred while adding a movie:", str(e))
            return render_template('error.html', error_message="An error occurred while adding a movie")

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
        Update movie information or details.

        This route allows users to update the information or details of a movie.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID or identifier of the movie to be updated.

        Returns:
            str: If the request method is GET, it renders a page where users can update the movie details.
                 If the request method is POST, it updates the movie information and redirects to the user's movie list page.

        Raises:
            Exception: If an error occurs during the movie update process.
        """
    if request.method == 'POST':
        try:
            new_title = request.form['new_title']
            new_rating = request.form['new_rating']

            movie = Movie.query.filter_by(imdbid=movie_id).first()

            if not movie:
                return render_template('error.html', error_message="Movie not found.")

            # Fetch movie details using new title
            new_movie_details = fetch_movie_details(new_title)

            if not new_movie_details:
                return render_template('error.html', error_message="New movie details not found.")

            # Update movie information with new details
            movie.title = new_movie_details.get('Title', movie.title)
            movie.year = new_movie_details.get('Year', movie.year)
            movie.genre = new_movie_details.get('Genre', movie.genre)
            movie.director = new_movie_details.get('Director', movie.director)
            movie.imdbid = new_movie_details.get('imdbID', movie.imdbid)
            movie.rating = new_rating

            db.session.commit()

            return redirect(url_for('get_user_movies', user_id=user_id))
        except Exception as e:
            # Handle exceptions related to updating a movie
            print("An error occurred while updating a movie:", str(e))
            return render_template('error.html', error_message="An error occurred while updating a movie")

    try:
        user_movies = User.query.get(user_id).movies  # Fetch user's movies
        movie = next((movie for movie in user_movies if movie.imdbid == movie_id), None)
        if movie:
            return render_template('update_movie.html', user_id=user_id, movie=movie)
        else:
            return render_template('error.html', error_message="Movie not found.")
    except Exception as e:
        # Handle exceptions related to getting a movie for update
        print("An error occurred while retrieving a movie for update:", str(e))
        return render_template('error.html', error_message="An error occurred while retrieving a movie for update")


@app.route('/users/<user_id>/delete_movie', methods=['GET', 'POST'])
def delete_movie(user_id):
    """
    Deletes a movie from a user's movie list.

    Args:
        user_id (str): The ID of the user.

        Returns:
            str: The rendered HTML template for deleting a movie.

        Raises:
            Exception: If an error occurs while deleting a movie.
    """
    # user = db.session.get(User, user_id)
    user = User.query.get(user_id)

    if not user:
        return render_template('error.html', error_message="User not found.")

    if request.method == 'POST':
        try:
            movie_id = request.args.get('movie_id')
            movie_to_delete = next((movie for movie in user.movies if movie.imdbid == movie_id), None)

            if movie_to_delete:
                db.session.delete(movie_to_delete)
                db.session.commit()
                return redirect(url_for('get_user_movies', user_id=user_id))
            else:
                return render_template('error.html', error_message="Movie not found.")
        except Exception as e:
            # Handle exceptions related to deleting a movie
            print("An error occurred while deleting a movie:", str(e))
            return render_template('error.html', error_message="An error occurred while deleting a movie")

    return render_template('delete_movie.html', user=user)


@app.route('/users/<user_id>/add_review/<movie_id>', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    """
    Adds a review to a movie in a user's movie list.

    Args:
        user_id (str): The ID of the user.
        movie_id (str): The ID of the movie.

        Returns:
            str: The rendered HTML template for adding a review.

        Raises:
            Exception: If an error occurs while adding a review.
    """
    if request.method == 'POST':
        try:
            review_text = request.form['review_text']
            rating = request.form['rating']

            user = User.query.get(user_id)

            if not user:
                return render_template('error.html', error_message="User not found.")

            movie = Movie.query.filter_by(imdbid=movie_id).first()
            if not movie:
                return render_template('error.html', error_message="Movie not found.")

            review = Review(user_id=user_id, movie_id=movie_id, review_text=review_text, rating=rating)
            db.session.add(review)
            db.session.commit()

            return redirect(url_for('get_user_movies', user_id=user_id))
        except Exception as e:
            # Handle exceptions related to adding a review
            print("An error occurred while adding a review:", str(e))
            return render_template('error.html', error_message="An error occurred while adding a review")

    try:
        user_movies = User.query.get(user_id).movies
        movie = next((movie for movie in user_movies if movie.imdbid == movie_id), None)
        if movie:
            # Add the following lines to get the reviews associated with the movie
            reviews = movie.get_reviews()
            return render_template('add_review.html', user_id=user_id, movie=movie, reviews=reviews)
        else:
            return render_template('error.html', error_message="Movie not found.")
    except Exception as e:
        # Handle exceptions related to getting a movie for review
        print("An error occurred while retrieving a movie for review:", str(e))
        return render_template('error.html', error_message="An error occurred while retrieving a movie for review")


@app.route('/users/<user_id>/movies/<movie_id>/update_review/<review_id>', methods=['GET', 'POST'])
def update_review(user_id, movie_id, review_id):
    """
        Update a review for a movie.

        This route allows users to update a review for a specific movie.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID or identifier of the movie.
            review_id (str): The ID or identifier of the review to be updated.

        Returns:
            str: If the request method is GET, it renders a page where users can update the review.
                 If the request method is POST, it updates the review and redirects to the movie details page.

        Raises:
            Exception: If an error occurs during the review update process.
        """
    if request.method == 'POST':
        try:
            new_review_text = request.form['new_review_text']
            new_rating = int(request.form['new_rating'])

            Review.update_review(review_id, new_review_text, new_rating)

            return redirect(url_for('movie_details', user_id=user_id, movie_id=movie_id))
        except Exception as e:
            # Handle exceptions related to updating a review
            print("An error occurred while updating a review:", str(e))
            return render_template('error.html', error_message="An error occurred while updating a review")

    review = Review.query.get(review_id)
    return render_template('update_review.html', user_id=user_id, movie_id=movie_id, review=review)


@app.route('/users/<user_id>/delete_review/<movie_id>/<review_id>', methods=['POST'])
def delete_review(user_id, movie_id, review_id):
    """
        Delete a review for a movie.

        This route allows users to delete a review for a specific movie.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID or identifier of the movie.
            review_id (str): The ID or identifier of the review to be deleted.

        Returns:
            str: Redirects to the user's list of movies after successfully deleting the review.

        Raises:
            Exception: If an error occurs during the review deletion process.
        """
    try:
        user = User.query.get(user_id)
        if not user:
            return render_template('error.html', error_message="User not found.")

        movie = Movie.query.filter_by(imdbid=movie_id).first()
        if not movie:
            return render_template('error.html', error_message="Movie not found.")

        review = Review.query.get(review_id)
        if not review:
            return render_template('error.html', error_message="Review not found.")

        db.session.delete(review)
        db.session.commit()

        return redirect(url_for('get_user_movies', user_id=user_id))
    except Exception as e:
        # Handle exceptions related to deleting a review
        print("An error occurred while deleting a review:", str(e))
        return render_template('error.html', error_message="An error occurred while deleting a review")


@app.errorhandler(404)
def page_not_found(e):
    """
        Renders a custom 404 page when a page is not found.

        Args:
            e: The exception raised for the page not found error.

        Returns:
            str: The rendered HTML template for the 404 page.
        """
    return render_template('404.html'), 404


if __name__ == '__main__':
    """
        Run the Flask application.

        This block of code creates the necessary database tables within a Flask application context
        and then starts the Flask development server.

        Note:
            Make sure to set the `debug` parameter to `False` in a production environment.

        """
    with app.app_context():
        db.create_all()
    app.run(debug=True)