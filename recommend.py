from db_connect import connect
from queries import get_plot, get_id_plot, get_movies_by_ids
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import re

# define a list of stopwords
stopwords = set(stopwords.words('english'))

# define a threshold for a movie to be recommended
threshold = 0.15

# helper functions
def preprocess(plot):
    plot = re.sub(r"[^\w\s]", "", plot)     # delete punctuation
    plot = plot.split()     # tokenize
    plot = [term for term in plot if term not in stopwords]     # remove stop words
    plot = [WordNetLemmatizer().lemmatize(term) for term in plot]   # lemmatize
    return set(plot)

def find_feature(word, bow):
    if word in bow:
        return True
    else:
        return False

def list_recommendations(similarity_matrix, core_bow):
    recommendations = []
    core_count = len(core_bow)
    for key in similarity_matrix:
        similarity_count = similarity_matrix[key].count(True)
        if similarity_count / core_count  >= threshold:
            recommendations.append(key)
    return recommendations

def check_genres(core_genres, candidate_genres):
    if not core_genres or not candidate_genres:
        return False
    for genre in candidate_genres:
        if genre in core_genres:
            return True
    return False

# main function
def recommend_movies(conn, core_id):
    core_plot, core_genres = get_plot(conn, core_id)     # get the core movie's plot and list of genres
    core_bow = preprocess(core_plot)

    # create a dict of candidates
    candidates = {}

    # populate candidates
    for stem in core_bow:
        similar_movies = get_id_plot(conn, stem, core_id)
        for movie in similar_movies:
            if movie[0] not in candidates.keys():
                candidates[movie[0]] = movie[1]

    # clean and tokenize each plot in the list of candidates
    for key in candidates:
        candidates[key] = preprocess(candidates[key])

    # make a matrix that will hold True/False values for tokens that were found/not found in the core plot
    similarity_matrix = {}

    # populate the matrix
    for key in candidates:
        similarity_matrix[key] = [find_feature(word, candidates[key]) for word in core_bow]

    # get a list of recommended ids
    recs = list_recommendations(similarity_matrix, core_bow)

    if len(recs) == 0:
        movies = []
        return movies

    # find recommendations by ids
    shortlist = get_movies_by_ids(conn, recs)

    # apply filter by genre: only movies that have at least one genre in common with the core movie remain
    movies = []
    for movie in shortlist:
        genre_filter = check_genres(core_genres, movie[3])
        if genre_filter == True:
            movies.append(movie)
    return movies