
# RECOMMENDATION-SYSTEM-369

[![Maintenance](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/) 
[![Maintenance](https://img.shields.io/badge/framework-flask-red.svg)](https://flask.palletsprojects.com/en/2.0.x/) 
[![Maintenance](https://img.shields.io/badge/Frontend-HTML/CSS/JS-green.svg)](https://img.shields.io/badge/Frontend-HTML/CSS/JS-green.svg) 
[![Maintenance](https://img.shields.io/badge/API-TMDB-orange.svg)](https://developers.themoviedb.org/3) 
[![Maintenance](https://img.shields.io/badge/python-JUPETER/NOTEBOOK-yellow.svg)](https://img.shields.io/badge/python-JUPETER/NOTEBOOK-yellow.svg) 


This application provides all the details of the requested movie such as overview, genre, release date, rating, runtime, top cast, reviews, recommended movies, etc.

The details of the movies(title, genre, runtime, rating, poster, etc) are fetched using an API by TMDB,https://www.themoviedb.org/documentation/api, and using the IMDB id of the movie in the API, I did web scraping to get the reviews given by the user in the IMDB site using beautifulsoup4 and performed sentiment analysis on those reviews.

# Link to the application
Check out the live demo: https://recommendationsystem369.herokuapp.com/

# How to get the API key?
Create an account in https://www.themoviedb.org/       
Check out the API Documentaion in https://developers.themoviedb.org/3/getting-started/authentication

# How to run the project?
> 1.  Clone this repository in your local system.
> 2. Install all the libraries mentioned in the requirements.txt file.
> 3. Replace YOUR_API_KEY in utils/secret.py file.
> 4. Open your terminal/command prompt from your project directory and run the main.py file by executing the command python main.py.
> 5. Go to your browser and type http://127.0.0.1:5000/ in the address bar.
Hurray! That's it.

# Sources of the datasets
> 1. [IMDB 5000 Movie Dataset](https://www.kaggle.com/carolzhangdc/imdb-5000-movie-dataset)
> 2. [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset)
> 3. [List of movies in 2018](https://en.wikipedia.org/wiki/List_of_American_films_of_2018)
> 4. [List of movies in 2019](https://en.wikipedia.org/wiki/List_of_American_films_of_2019)
> 5. [List of movies in 2020](https://en.wikipedia.org/wiki/List_of_American_films_of_2020)
> 6. [List of movies in 2021](https://en.wikipedia.org/wiki/List_of_American_films_of_2021)
