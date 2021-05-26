import pandas as pd
import pickle
import requests
from tmdbv3api import TMDb
from tmdbv3api import Movie
import math
import numpy as np
import bs4 as bs
import urllib.request
from .secret import SECRET
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class UTILS:
    MOVIE_DATASET_PATH = SECRET.MOVIE_DATASET_PATH.value
    #COSINE_MODEL_PATH = SECRET.COSINE_MODEL_PATH.value
    NLP_MODEL_PATH = SECRET.NLP_MODEL_PATH.value
    TRANSFORM_MODEL_PATH = SECRET.TRANSFORM_MODEL_PATH.value
    DATA = pd.read_csv(MOVIE_DATASET_PATH)
    API_KEY = SECRET.API_KEY.value
    TMDB = TMDb()
    TMDB_MOVIE = Movie()
    TMDB.api_key = API_KEY
    POSTER_URL = 'https://image.tmdb.org/t/p/original'
    MOVIE_DETAIL_URL = 'https://api.themoviedb.org/3/movie/{}?api_key={}'
    MOVIE_CAST_URL = 'https://api.themoviedb.org/3/movie/{}/credits?api_key={}'
    INDIVIDUAL_CAST_URL = 'https://api.themoviedb.org/3/person/{}?api_key={}'
    REVIEW_URL = 'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'
    SEARCH_MOVIE_NAME = ""

    def __init__(self):
        self.TFIDF_TRANSFORM = pickle.load(open(self.TRANSFORM_MODEL_PATH, 'rb'))
        self.NLP_REVIEW_CLAFFSIFY_MODEL = pickle.load(open(self.NLP_MODEL_PATH, 'rb'))

    def get_suggestions(self):
        return list(self.DATA['movie_title'].str.capitalize())

    def _similarity(self):
        tfidf = TfidfVectorizer()
        count_matrix = tfidf.fit_transform(self.DATA['combination'])
        similarity = cosine_similarity(count_matrix)
        return similarity

    def recommend_movie(self):
        movie_name = self.SEARCH_MOVIE_NAME.lower()
        similarity = self._similarity()
        final_recommend_movie = []
        if movie_name not in self.DATA['movie_title'].unique():
            return ("Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies")
        if movie_name in self.DATA['movie_title'].unique():
            i = self.DATA.loc[self.DATA['movie_title'] == movie_name].index[0]
            l = []
            lst = list(enumerate(similarity[i]))
            lst = sorted(lst, key=lambda x: x[1], reverse=True)
            lst = lst[1:11]
            for i in range(len(lst)):
                a = lst[i][0]
                l.append(self.DATA['movie_title'][a])
        data = list(set(l))
        return data

    def cvt_runtime(self, runtime):
        if runtime % 60 == 0:
            return f"{math.floor(runtime /  60)} Hours"
        if runtime % 60 != 0:
            return f"{math.floor(runtime / 60)} Hour {runtime % 60} Min"

    def cvt_datetime(self, datetime):
        datetime = str(datetime).split("-")
        month_map = {"01":"January", "02":"February", "03":"March", "04":"April", "05":"May", "06":"June",
                     "07":"July", "08":"August", "09":"September", "10":"October", "11":"November", "12":"December",}
        year, month, date = datetime[0], month_map[datetime[1]], str(datetime[2])
        if date in '1':
            return f"{date}st {month} {year}"
        elif date in '2':
            return f"{date}nd {month} {year}"
        elif date in '3':
            return f"{date}rd {month} {year}"
        else:
            return f"{date}th {month} {year}"

    def get_individual_cast(self, cast_id):
        individual_cast = []
        res = requests.get(self.INDIVIDUAL_CAST_URL.format(cast_id, self.API_KEY))
        data = res.json()
        biography = data['biography']
        birthday = data['birthday']
        deathday = data['deathday']
        if biography == '':
            biography = None
        if birthday == '':
            birthday = None
        if deathday == '':
            deathday = None
        place_of_birth = data['place_of_birth']
        individual_cast.append([biography, birthday, place_of_birth, deathday, cast_id])
        return individual_cast

    def _scrap_review(self, imdb_id):
        sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        soup_result = soup.find_all("div", {"class": "text show-more__control"})
        return soup_result

    def _classify_review(self, review):
        review_lst = np.array([review])
        transform_data = self.TFIDF_TRANSFORM.transform(review_lst)
        pred = self.NLP_REVIEW_CLAFFSIFY_MODEL.predict(transform_data)
        return 'Positive' if pred else 'Negative'

    def get(self,
            get_poster = False,
            get_movie_details = False,
            get_cast = False,
            get_reviews = False):
        if get_cast:
            MAX_CAST = 15
            my_cast = []
            result = self.TMDB_MOVIE.search(self.SEARCH_MOVIE_NAME)
            try:
                movie_id = result[0].id
            except IndexError:
                return ""
            res = requests.get(self.MOVIE_CAST_URL.format(movie_id, self.API_KEY))
            data = res.json()
            cast = data['cast']
            for c in cast:
                if len(my_cast) <=  7:
                    if c['profile_path'] != None:
                        profile_path = f"{self.POSTER_URL}{c['profile_path']}"
                        original_name = c['original_name']
                        character_name = c['character']
                        cast_id = c['id']
                        individual_cast_details = self.get_individual_cast(cast_id = cast_id)
                        try:
                            character_name_1 = f"{str(character_name).split(' / ')[0]}"
                            character_name_2 = f"{str(character_name).split(' / ')[-1]}"
                            my_cast.append([profile_path, original_name, [character_name_1, character_name_2], individual_cast_details])
                        except:
                            my_cast.append([profile_path, original_name, character_name, individual_cast_details])
                    if c['profile_path'] == None:
                        continue
                if len(my_cast) > 7:
                    return my_cast
            return my_cast

        if get_movie_details:
            release_date = budget = overview = runtime = status = rating = title =''
            movie_genres = []
            final_genres = ""
            result = self.TMDB_MOVIE.search(self.SEARCH_MOVIE_NAME)
            try:
                movie_id = result[0].id
            except IndexError:
                return ""
            res = requests.get(self.MOVIE_DETAIL_URL.format(movie_id, self.API_KEY))
            data = res.json()
            release_date = self.cvt_datetime(datetime = data['release_date'])
            budget = data['budget']
            overview = data['overview']
            runtime = self.cvt_runtime(runtime = data['runtime'])
            status = data['status']
            title = data['original_title']
            try:
                genres = data['genres']
                for g in range(len(genres)):
                    grs = genres[g]['name']
                    movie_genres.append(grs)
                final_genres = ", ".join([genre for genre in movie_genres])
            except:
                final_genres = 'unknown'
            rating = data['vote_average']
            return [release_date, budget, overview, runtime, status, final_genres, rating, title]

        if get_poster:
            result = self.TMDB_MOVIE.search(self.SEARCH_MOVIE_NAME)
            try:
                movie_id = result[0].id
            except IndexError:
                return ""
            res = requests.get(self.MOVIE_DETAIL_URL.format(movie_id, self.API_KEY))
            data = res.json()
            poster_path = []
            poster = data['poster_path']
            if poster != None:
                poster_path = f"{self.POSTER_URL}{poster}"
            if poster == None:
                poster_path = f"{self.POSTER_URL}{data['belongs_to_collection']['poster_path']}"
            return poster_path

        if get_reviews:
            result = self.TMDB_MOVIE.search(self.SEARCH_MOVIE_NAME)
            try:
                movie_id = result[0].id
            except IndexError:
                return ""
            response = requests.get(self.MOVIE_DETAIL_URL.format(movie_id, self.API_KEY))
            response_data = response.json()
            imdb_id = response_data['imdb_id']
            soup_result = self._scrap_review(imdb_id = imdb_id)
            reviews_list = []
            reviews_status = []
            for reviews in soup_result:
                if reviews.string:
                    reviews_list.append(reviews.string)
                    pred = self._classify_review(review = reviews.string)
                    reviews_status.append(pred)
            data = [reviews_list, reviews_status]
            review_ = {reviews_list[i] : reviews_status[i] for i in range(len(reviews_list))}
            if review_ == {}:
                review_ = None
            return review_


    def get_movie_poster(self, movie_name):
        self.SEARCH_MOVIE_NAME = movie_name
        return self.get(get_poster = True)

    def get_movie_details(self, movie_name):
        self.SEARCH_MOVIE_NAME = movie_name
        return self.get(get_movie_details = True)

    def get_cast(self, movie_name):
        self.SEARCH_MOVIE_NAME = movie_name
        return self.get(get_cast = True)

    def get_reviews(self, movie_name):
        movie_reviews = []
        self.SEARCH_MOVIE_NAME = movie_name
        reviews = self.get(get_reviews = True)
        return reviews

    def get_recommend_movie_details(self, movie_name):
        self.SEARCH_MOVIE_NAME = movie_name
        recommend_movies = self.recommend_movie()
        recommend_movie_poster = []
        for rm in recommend_movies:
            try:
                poster = self.get_movie_poster(movie_name = str(rm))
                rating = self.get(get_movie_details = str(rm))[6]
                release_date = self.get(get_movie_details = str(rm))[0].split(" ")[-1]
                recommend_movie_poster.append([poster, str(rm), rating, release_date])
            except:
                return ""
        return recommend_movie_poster
