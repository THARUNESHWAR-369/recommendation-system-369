import requests
from requests.api import request

import math

from ._urls import URLS
from ._paths import PATHS


class FORMATDATA:

    def __init__(self, movie_keys, map_data) -> None:
        self.__MOVIE_KEYS = movie_keys
        self.__MAP_MOVIE_DATA, self.__MAP_MONTH = map_data

    def startFromat(self) -> None:
        __fs = self.__formatStrings()
        __fd = self.__formatDate()
        __fb = self.__formatBudget()
        self.__formatRuntime()
        self.__formatMMD(dict(**__fs, **__fd, **__fb))

    def __formatStrings(self) -> list:
        __fs = {}
        for key in self.__MOVIE_KEYS[:-1]:
            __fs[key] = ", ".join([val for val in self.__MAP_MOVIE_DATA[key]])
        return __fs
    
    def __formatDate(self) -> dict:
        """
        yyyy-mm-dd
        """
        __year, __month, __date = str(self.__MAP_MOVIE_DATA['release_date']).split('-')
        return {'release_date':f"{__year}-{__month}-{__date} ({__date} {self.__MAP_MONTH[__month]} {__year})"}
    
    def __formatBudget(self) -> dict:
        try:
            __fb = {}
            for budget in ['budget', 'revenue']:
                __fb[budget] = f"{self.__MAP_MOVIE_DATA[budget] / 1000000} Million USD"
            return __fb
        except Exception:
            return {'budget':None, "revenue":None}
    
    def __formatRuntime(self) -> None:
        try:
            runtime = self.__MAP_MOVIE_DATA['runtime']
            if runtime % 60 == 0:
                self.__MAP_MOVIE_DATA['runtime'] = f"{math.floor(runtime /  60)} Hours"
            elif runtime % 60 != 0:
                self.__MAP_MOVIE_DATA['runtime'] =  f"{math.floor(runtime / 60)} Hour {runtime % 60} Min"
        except Exception:
            pass

    def __formatMMD(self, f_data) -> None:
        for key, val in f_data.items():self.__MAP_MOVIE_DATA[key] = val

class MOVIE_DB:

    __MOVIE_NAME, __TMDB_MOVIE = None, None
    
    __MOVIE_KEYS = ['genres', 'production_companies', 'production_countries', 'spoken_languages', 'poster_path']

    __MAP_MONTH = {"01":'JAN', "02":"FEB", "03":'MAR', "04":"APR", "05":'MAY', "06":"JUN", 
                   "07":'JUL', "08":"AUG", "09":"SEP", "10":'OCT', '11':'NOV', '12':"DEC"}

    __MAX_CAST = 7

    def __init__(self, movie_name, tmdb_movie) -> None:
        self.__MOVIE_NAME = movie_name
        self.__TMDB_MOVIE = tmdb_movie 

        self.__MAP_MOVIE_DATA = {
            "adult": "False",
            "budget":"",
            "imdb_id":"",
            "genres": list(),
            'original_title': "", 
            'overview': "", 
            'poster_path': "", 
            'production_companies': list(),
            'production_countries': list(),
            'release_date': "",
            'revenue': '', 
            'runtime': "",
            'spoken_languages': list(),
            'status':"",
            'tagline': '',
            'vote_average': "",
        }

        self.__MAP_RECOM_MOVIE_DATA = {
            "vote_average":"",
            "original_title":"",
            "poster_path":"",
            "release_date":""
        }

        self.__CAST_KEYS= [
            "biography",
            "birthday",
            "deathday",
            'name',
            "place_of_birth",
            "profile_path"
        ]

        self.__CAST_DETAILS = []
    
    def __FetchMovieDetails(self, id) -> None:
        movie_result = requests.get(URLS.MOVIE_DETAIL_URL.format(id, PATHS.API_KEY))
        if movie_result:
            result_movie_details = movie_result.json()

            for movie_data_keykey in list(self.__MAP_MOVIE_DATA.keys()):
                if result_movie_details[movie_data_keykey]:
                    if movie_data_keykey in self.__MOVIE_KEYS:
                        if movie_data_keykey == "poster_path":
                            self.__MAP_MOVIE_DATA[movie_data_keykey] = f"{URLS.POSTER_URL}{result_movie_details[movie_data_keykey]}"
                        else:
                            for details in result_movie_details[movie_data_keykey]:
                                for k,v in details.items():
                                    if k == "name":
                                        self.__MAP_MOVIE_DATA[movie_data_keykey].append(v)
                    else:
                        self.__MAP_MOVIE_DATA[movie_data_keykey] = result_movie_details[movie_data_keykey]

    def __FetchCastDetails(self, id) -> None:
        count = 0
        movie_cast_result = requests.get(URLS.MOVIE_CAST_URL.format(id, PATHS.API_KEY))
        if movie_cast_result:
            result_movie_cast = movie_cast_result.json()['cast'][:self.__MAX_CAST]
            for cast in result_movie_cast:
                try:
                    result_movie_cast = movie_cast_result.json()['cast'][:self.__MAX_CAST + count]
                    character_cast_dict = {"character":cast['character']}
                    cast_details = requests.get(URLS.INDIVIDUAL_CAST_URL.format(cast['id'], PATHS.API_KEY))
                    individual_cast_details = cast_details.json()

                    if individual_cast_details['profile_path'] != None:
                        cast_details = {} 
                        cast_details['profile_path'] = f"{URLS.POSTER_URL}{individual_cast_details['profile_path']}"
                        for cast_key in self.__CAST_KEYS[:-1]:
                            cast_details[cast_key] = individual_cast_details[cast_key]
                    else:
                        count+=1
                except Exception as e:
                    print("CASET (ERROR): ",e)
                
                """print('individual_cast_details: ',len(individual_cast_details))
                for cast_key in self.__CAST_KEYS:
                    cast_details = {} 
                    if individual_cast_details[cast_key] != None and individual_cast_details["deathday"] == None:
                        print("cast_key: ",cast_key,"-->",individual_cast_details[cast_key])
                        if cast_key == "profile_path":
                            cast_details[cast_key] = f"{URLS.POSTER_URL}{individual_cast_details[cast_key]}"
                        else:
                            cast_details[cast_key] = individual_cast_details[cast_key]
                    cast_details["deathday"] = individual_cast_details["deathday"]"""
                    
                self.__CAST_DETAILS.append(dict(**character_cast_dict, **cast_details))
          
    def __FetchRecomMovieDetails(self, id) -> None:
        recom_movie_result = requests.get(URLS.MOVIE_DETAIL_URL.format(id, PATHS.API_KEY))
        if recom_movie_result:
            result_recom_movie_details = recom_movie_result.json()

            for recom_movie_keys in list(self.__MAP_RECOM_MOVIE_DATA.keys()):
                if result_recom_movie_details[recom_movie_keys]:
                    if recom_movie_keys == "poster_path":
                        self.__MAP_RECOM_MOVIE_DATA[recom_movie_keys] = f"{URLS.POSTER_URL}{result_recom_movie_details[recom_movie_keys]}"
                    else:
                        self.__MAP_RECOM_MOVIE_DATA[recom_movie_keys] = result_recom_movie_details[recom_movie_keys]

    def getMovieDetails(self, isRecomdMovie=False) -> list:
        result = self.__TMDB_MOVIE.search(self.__MOVIE_NAME)
        if result:
            result_details = result[0]
            if result_details:
                if isRecomdMovie==True:
                    self.__FetchRecomMovieDetails(id=result_details.id)
                    return None, None, self.__MAP_RECOM_MOVIE_DATA

                if isRecomdMovie == False:
                    self.__FetchMovieDetails(id=result_details.id)
                    self.__FetchCastDetails(id=result_details.id)
                    self.__do_format()
                    return self.__MAP_MOVIE_DATA, self.__CAST_DETAILS, None
            isRecomdMovie = False
               
    def __do_format(self) -> None:
        formatData = FORMATDATA(movie_keys=self.__MOVIE_KEYS, map_data=[self.__MAP_MOVIE_DATA, self.__MAP_MONTH])
        formatData.startFromat()
