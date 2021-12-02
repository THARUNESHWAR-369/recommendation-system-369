import pandas as pd
import numpy as np

import joblib
import urllib.request
import urllib.error
import bs4 as bs

# TMDB
from tmdbv3api import TMDb
from tmdbv3api import Movie

# From packages
from ._paths import PATHS
from ._movieDB import MOVIE_DB
from ._urls import URLS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from random import choices

class UTILS:

    """
    Modal Path
    """
    __MOVIE_DATASET_PATH = PATHS.MOVIE_DATASET_PATH

    __NLP_MODEL_PATH = PATHS.NLP_MODEL_PATH
    __TRANSFORM_MODEL_PATH = PATHS.TRANSFORM_MODEL_PATH

    # Api key
    __API_KEY = PATHS.API_KEY

    __MAX_MOVIE_RECOMMEND = 10

    __MAX_TOP_SEARCH = 5

    def __init__(self) -> None:
        # Load dataset
        self.__DATA = pd.read_csv(self.__MOVIE_DATASET_PATH)

        # Initialize Movie methods
        self.__TMDB = TMDb()
        self.__TMDB.api_key = self.__API_KEY
        self.__TMDB_MOVIE = Movie()

        # Load models
        self.__TFIDF_TRANSFORM = joblib.load(self.__TRANSFORM_MODEL_PATH)
        self.__REVIEW__MODEL = joblib.load(self.__NLP_MODEL_PATH)
    
    def getMovieNames(self) -> list:
        return list(self.__DATA['movie_title'].str.capitalize())
    
    def getMovieDetails(self, movie_name) -> list:
        return MOVIE_DB(movie_name=movie_name, tmdb_movie=self.__TMDB_MOVIE).getMovieDetails()
    
    def scrap_review(self, imdb_id) -> dict:
        soup_result = self.__scrapReview(imdb_id)
        if soup_result != None:
            reviews_list = []
            reviews_status = []
            review_dict = {}
            for reviews in soup_result:
                if reviews.string:
                    reviews_list.append(reviews.string)
                    rev_pred = self.__classify_review(review = reviews.string)
                    reviews_status.append(rev_pred)
                review_dict = {reviews_list[i] : reviews_status[i] for i in range(len(reviews_status))}
            if len(review_dict) != 0:
                return review_dict
        return None
    
    def recommendMovie(self, movie_name) -> list:
        moviename = movie_name.lower()
        similarity = self.__similarity()
        if moviename not in self.__DATA['movie_title'].unique():
            raise Exception#("Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies")
        
        movie_idx = self.__DATA.loc[self.__DATA['movie_title'] == moviename].index[0]
        movie_lst = []
        recom_lst = list(enumerate(similarity[movie_idx]))
        recom_lst = sorted(recom_lst, key=lambda x: x[1], reverse=True)
        recom_lst = recom_lst[1:self.__MAX_MOVIE_RECOMMEND + 1]
        
        for i in range(len(recom_lst)):
            movie_id = recom_lst[i][0]
            movie_lst.append(self.__DATA['movie_title'][movie_id])
        recom_movie_list = list(set(movie_lst))
        return self.__getRecomMovieDetails(recom_movie_list=recom_movie_list)
    
    def __getRecomMovieDetails(self, recom_movie_list) -> list:
        recomMovieDetailsList = []
        for movie_name in recom_movie_list:
            recomMovieDetailsList.append(MOVIE_DB(movie_name=movie_name, tmdb_movie=self.__TMDB_MOVIE).getMovieDetails(isRecomdMovie=True)[-1])
        return recomMovieDetailsList

    def __similarity(self) -> tuple:
        tfidf = TfidfVectorizer()
        count_matrix = tfidf.fit_transform(self.__DATA['combination'])
        similarity = cosine_similarity(count_matrix)
        return similarity

    def __classify_review(self, review) -> str:
        review_lst = np.array([review])
        transform_data = self.__TFIDF_TRANSFORM.transform(review_lst)
        pred = self.__REVIEW__MODEL.predict(transform_data)
        return 'Positive' if pred else 'Negative'
    
    def __scrapReview(self, imdb_id):
        try:
            sauce = urllib.request.urlopen(URLS.REVIEW_URL.format(imdb_id)).read()
            soup = bs.BeautifulSoup(sauce, 'lxml')
            soup_result = soup.find_all("div", {"class": "text show-more__control"})
            return soup_result
        except urllib.error.HTTPError:
            return None
   
    def getTopSearch(self):
        return choices(self.__DATA['movie_title'], k=self.__MAX_TOP_SEARCH)