from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_user(self, user):
        pass

    @abstractmethod
    def delete_user(self, user_id):
        pass

    @abstractmethod
    def add_movie_to_user(self, user_id, movie):
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        pass

    @abstractmethod
    def update_movie(self, user_id, movie_id, new_title, new_rating):
        pass

    # Add more methods as needed
