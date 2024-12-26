from db_connect import connect
from queries import get_movies, get_searches, record_search
from helpers import show_table, show_stats, get_keyword, get_genre, get_year, get_fav
from recommend import recommend_movies
from colorama import init, Fore
from InquirerPy import inquirer

def main():

    # introduce the app
    with open('README.txt','r') as readme:
        print(f"\n{readme.read()}")

    # set user options
    options = [
        "Find a movie",
        "Recommend a movie",
        "View search stats", 
        "Exit"
    ]
    choice = None

    # continue in a loop until the user chooses to exit
    while choice != options[len(options)-1]:

        # establish a connection
        conn = connect()

        ## exit if not connected
        if conn == None:
            print(Fore.RED + "\u2717", end=' ')
            print("Unable to connect. Exiting the appp\n")
            return 1

        # offer user options to choose from    
        print("")
        choice = inquirer.select(
            message="What would you like to do?",
            choices=options
            ).execute()

        # if exited
        if choice == options[len(options)-1]:
            conn.close()
            print(Fore.GREEN + "\u2713", end=' ')
            print("Exited\n")
            return 0

        try:
            if choice == options[0]:
                # prompt for a keyword
                keyword = get_keyword()
                # prompt for a genre
                genre = get_genre(conn)
                # prompt for a year
                year = get_year(conn, genre)
                # validate at least one search parameter is used
                if keyword or genre or year:
                    # proceed with search
                    movies = get_movies(conn, keyword, genre, year)  # fetch movies from the database
                    record_search(conn, keyword, genre, year, len(movies))  # record search in the database
                    show_table(movies)  # pretty-print the table
                else:
                    raise ValueError(f"Please use at least one of the search parameters (keyword, genre, year)")

            elif choice == options[1]:
                fav_id = get_fav(conn)
                if fav_id == None:
                    print("\u2205 Sorry, we don't have that movie in our database.")
                    return
                else:
                    print(Fore.GREEN + "\u276F", end=' ')
                    print("Looking for movies you might like...")
                    recommended = recommend_movies(conn, fav_id)
                    show_table(recommended)
            elif choice == options[2]:
                TOP_N = 10  # define N for Top N search queries
                searches = get_searches(conn)
                show_stats(searches, TOP_N)
        except Exception as err:
            print(Fore.RED + "\u2717", end=' ')
            print(f"{err}")
        finally:
            conn.close()

if __name__ == "__main__":
    # initialize colorama
    init(autoreset=True)
    main()