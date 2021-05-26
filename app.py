from flask import Flask, render_template, request
from utils.utils import UTILS
from utils.secret import SECRET

app = Flask(__name__)
utils = UTILS()
app.secret_key = SECRET.API_KEY.value

@app.route('/', methods=["POST", "GET"])
def hello_world():
    suggestions = utils.get_suggestions()
    error = ''
    if request.method == 'GET':
        return render_template('home.html', suggestions=suggestions, error=error)

    if request.method == "POST":
        movie_name = request.form.get('search-field')

        if movie_name == None:
            error = "Sorry, the movie is not found at our database! Try with another movie :)"
            return render_template('home.html', suggestions=suggestions, error=error)
        if movie_name != None:
            movie_poster = utils.get_movie_poster(movie_name = movie_name)
            movie_casts = utils.get_cast(movie_name = movie_name)
            movie_details = utils.get_movie_details(movie_name =movie_name)
            movie_review = utils.get_reviews(movie_name = movie_name)
            recommend_movies = utils.get_recommend_movie_details(movie_name = movie_name)
            if len(movie_poster) == 0:
                error = "Sorry, the movie is not found at our database! Try with another movie :)"
            return render_template(
                                    'recommended_movie.html',
                                    suggestions=suggestions,
                                    movie_name=movie_name,
                                    movie_poster=movie_poster,
                                    movie_details=movie_details,
                                    movie_casts=movie_casts,
                                    movie_review=movie_review,
                                    recommneded_movies=recommend_movies,
                                    error=error
                                )
if __name__ == '__main__':
    app.debug = True
    app.run(threaded=True, port=5555)
