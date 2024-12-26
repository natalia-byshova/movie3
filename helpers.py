from collections import Counter
from tabulate import tabulate
from InquirerPy import inquirer
import textwrap
from colorama import init, Fore
from queries import show_genres, show_year_range, get_id_title

def prettify(headers, table):
    return tabulate(
            table, 
            headers=headers, 
            tablefmt='fancy_grid' # style of formatting
            )

def show_table(movies):
    # count rows
    rows = len(movies)
    if rows > 0:
        # define headers for the table
        headers = (
            "Title",
            "Plot",
            "Year",
            "Genre",
            "Runtime (min)",
            "IMDB Rating"
        )

        # wrap lines that are too long
        max_length = [30, 80, 4, 30, 15, 15]
        wrapped_movies = []
        for row in movies:
            wrapped_row = []
            for i, cell in enumerate(row):
                if i == 3: # handle multiple genres per row
                    cell = list(cell)
                    cell = "\n".join(cell)

                if len(str(cell)) > max_length[i]:
                    wrapped_cell = textwrap.fill(cell, width=max_length[i])
                else:
                    wrapped_cell = cell
                wrapped_row.append(wrapped_cell)
            wrapped_movies.append(wrapped_row)

        # configure the table to be displayed
        table = prettify(headers, wrapped_movies)
        
        print(Fore.GREEN + "\u2713", end=' ')
        print(f"Found {rows} movies:")
        print(table)
    else:
        print("\u2205 Nothing found.")

def show_stats(searches, n):
    # make search queries from params
    search_queries = []
    for row in searches:
        search_terms = [str(term).lower() for term in row if term]
        search_query = " ".join(search_terms)
        search_queries.append(search_query)
    often_searched = Counter(search_queries).most_common(n)
    
    # configure the table to be displayed
    headers = [
        "Search query",
        "Times searched"
    ]
    table = prettify(headers, often_searched)

    print(Fore.GREEN + "\u2713", end=' ')
    print(f"Top {n} most popular search queries:")
    print(table)

def prompt_text(message):
    response = inquirer.text(
        message=message
    ).execute().strip()
    return response

def prompt_select(message, options):
    response = inquirer.select(
        message=message,
        choices=options
    ).execute()
    return response

def get_keyword():
    keyword = prompt_text("Enter keyword(s), or leave blank:")
    if len(keyword) > 128:
        raise ValueError("Keyword cannot be longer than 128 characters")
    return keyword

def get_year(conn, genre):
    min_year, max_year = show_year_range(conn, genre)    # fetch available years for the selected genre
    year = prompt_text(f"Choose a release year ({min_year} - {max_year}), or leave blank:")
    if year:
        try:
            year = int(year)
            if not min_year <= year <= max_year:
                raise ValueError             
        except ValueError:
            raise ValueError(f"Please enter a 4-digit year between {min_year} and {max_year}")
    return year

def get_genre(conn):
    genres = show_genres(conn)  # fetch available genres
    genre = prompt_select("Choose a genre:", genres)
    if genre == "Any":
        genre = ""
    return genre

def get_fav(conn):
    fav_title = prompt_text("What's your favorite movie?")
    candidate_titles = get_id_title(conn, fav_title)    # retrieve movies with that title
    if not candidate_titles:
        return None
    else:
        fav_movie = prompt_select("Choose the one you mean:", candidate_titles)
        fav_id = candidate_titles.get(fav_movie)
    return fav_id