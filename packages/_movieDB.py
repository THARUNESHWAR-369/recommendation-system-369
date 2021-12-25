import requests
from requests.api import request

import math

from ._urls import URLS
from ._paths import PATHS


class FORMATDATA:

    def __init__(self, movie_keys, map_data) -> None:

        self.__MOVIE_KEYS = movie_keys
        self.__MAP_MOVIE_DATA, self.__CAST_DETAILS ,self.__MAP_MONTH = map_data

    def startFromat(self) -> None:
        __fs = self.__formatStrings()
        __fd = self.__formatDate()
        __fb = self.__formatBudget()
        self.__formatPicUrl()
        self.__formatRuntime()
        self.__formatMMD(dict(**__fs, **__fd, **__fb))

    def __formatPicUrl(self):
        for cast_dict_idx in range(len(self.__CAST_DETAILS)):
            self.__CAST_DETAILS[cast_dict_idx]['profile_path'] = f"{URLS.POSTER_URL}{self.__CAST_DETAILS[cast_dict_idx]['profile_path']}"
        self.__MAP_MOVIE_DATA['poster_path'] = f"{URLS.POSTER_URL}{self.__MAP_MOVIE_DATA['poster_path']}"

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

    __CAST_KEYS= [
            "biography",
            "birthday",
            "deathday",
            'name',
            "place_of_birth",
            "profile_path"
        ]

    __MAP_MONTH = {"01":'JAN', "02":"FEB", "03":'MAR', "04":"APR", "05":'MAY', "06":"JUN", 
                   "07":'JUL', "08":"AUG", "09":"SEP", "10":'OCT', '11':'NOV', '12':"DEC"}

    __MAX_CAST = 7

    def __init__(self, movie_name, tmdb_movie) -> None:

        self.__MOVIE_NAME = movie_name
        self.__TMDB_MOVIE = tmdb_movie 

        self.__MAP_RECOM_MOVIE_DATA = {
            "vote_average":"",
            "original_title":"",
            "poster_path":"",
            "release_date":""
        }

        self.__CAST_DETAILS = []

        self.__GET_MOVIE_DETAILS = {
            "id":"",
            'overview':'',
            'poster_path':'',
            'release_date':'',
            'title':'',
            'vote_average':''
        }

        self.__MOVIE_DETAILS = {
            'budget':'',
            'genres':list(),
            'imdb_id':'',
            'production_companies':list(),
            'production_countries':list(),
            'release_date':'',
            'revenue':'',
            'runtime':'',
            'spoken_languages':list(),
            'status':'',
            'tagline':''
        }
    
    def __FetchMovieDetails(self, id) -> None:
                
        movie_result = requests.get(URLS.MOVIE_DETAIL_URL.format(id, PATHS.API_KEY))

        if movie_result:
            result_movie_details = movie_result.json()
            #print("result_movie_details: ",result_movie_details)

            for md_keys, md_values in self.__MOVIE_DETAILS.items():

                if md_values == list():
                    for md_details_dict in result_movie_details[md_keys]:
                        self.__MOVIE_DETAILS[md_keys].append(md_details_dict['name'])
                        self.__GET_MOVIE_DETAILS[md_keys] = self.__MOVIE_DETAILS[md_keys]
                else:
                    self.__GET_MOVIE_DETAILS[md_keys] = result_movie_details[md_keys]

    def __FetchCastDetails(self, id) -> None:
        __CAST_COUNT = 0
        movie_cast_result = requests.get(URLS.MOVIE_CAST_URL.format(id, PATHS.API_KEY))
        if movie_cast_result:
            result_movie_cast = movie_cast_result.json()['cast'][:self.__MAX_CAST + __CAST_COUNT]
            for cast_details in result_movie_cast:
                character_cast_dict = {"character":cast_details['character']}
                cast_details = requests.get(URLS.INDIVIDUAL_CAST_URL.format(cast_details['id'], PATHS.API_KEY))
                individual_cast_details = cast_details.json()

                #print("\n\nindividual_cast_details: ",individual_cast_details)

                if individual_cast_details['profile_path'] != None:
                    cast_details = {cast_keys:individual_cast_details[cast_keys] for cast_keys in self.__CAST_KEYS}
                    self.__CAST_DETAILS.append(dict(**character_cast_dict, **cast_details))
                
                else:
                    #print("\n\n\t\tProfile Path None\a")
                    __CAST_COUNT += 1
                    continue
                
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
            #print(result_details)
            if result_details:
                if isRecomdMovie==True:
                    self.__FetchRecomMovieDetails(id=result_details.id)
                    return None, None, self.__MAP_RECOM_MOVIE_DATA

                else:
                    for gmd_keys, _ in self.__GET_MOVIE_DETAILS.items():
                        self.__GET_MOVIE_DETAILS[gmd_keys] = result_details[gmd_keys]
                    self.__FetchMovieDetails(id=result_details.id)
                    self.__FetchCastDetails(id=result_details.id)  
                    self.__do_format()
                    #print('__GET_MOVIE_DETAILS: ',self.__GET_MOVIE_DETAILS)
                    return self.__GET_MOVIE_DETAILS, self.__CAST_DETAILS, None    
    
            isRecomdMovie = False
               
    def __do_format(self) -> None:
        formatData = FORMATDATA(movie_keys=self.__MOVIE_KEYS, map_data=[self.__GET_MOVIE_DETAILS, self.__CAST_DETAILS, self.__MAP_MONTH])
        formatData.startFromat()
