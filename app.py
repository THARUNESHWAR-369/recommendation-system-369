from flask import Flask, render_template, request

import os

# import from packages
from packages._utils import UTILS

app = Flask(__name__)

utils = UTILS()



@app.route('/', methods=['POST', 'GET'])
def home():
    # get Movie names
    movieNamesList = utils.getMovieNames()

    status = False
    error = None
    topSearch = utils.getTopSearch()

    if request.method == "POST":
        print(request.form)
        searchMovieName = request.form.get('search-movie')
        
        try:
            movieDetails, castDetails, _ = utils.getMovieDetails(movie_name=searchMovieName)
            review_dict = utils.scrap_review(imdb_id = movieDetails['imdb_id'])
            recomMovieDetailsList = None if type(utils.recommendMovie(movie_name=searchMovieName)) == str else utils.recommendMovie(movie_name=searchMovieName)
            topSearch = None
            status = True
            return render_template('home.html', movieNamesList=movieNamesList,
                               status=status, 
                               error=error,
                               movieDetails=movieDetails, 
                               castDetails=None if len(castDetails) == 0 else castDetails, 
                               movieReviews=review_dict,
                               recomMovieDetailsList = recomMovieDetailsList,
                               topSearch=topSearch)
        except Exception as e:
            print("app.py (error): ",e)
            error = "sorry, this movie was not found in our database!"
            status=False
            return render_template('home.html', movieNamesList=movieNamesList,
                                status=status, 
                               error=error, topSearch=topSearch)
        
    if request.method == "GET":
        status = False
    return render_template('home.html',error=error, movieNamesList=movieNamesList, status=status, topSearch=topSearch)

if __name__ == '__main__':
    app.debug = True
    app.run()