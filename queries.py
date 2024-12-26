from db_connect import connect
import re

def execute_select(conn, query, params=None):
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

def execute_insert(conn, query, params=None):
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()

def get_movies(conn, keyword, genre, year):
        # construct query and parameters based on user input
        select_movies = """SELECT title, plot, year, genres, runtime, `imdb.rating` FROM movies WHERE """
        filters = []
        params = []
        if keyword:
                filters.append("(title LIKE %s OR plot LIKE %s)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
        if genre:
                filters.append("(genres LIKE %s)")
                params.append(f"%{genre}%")
        if year:
                filters.append("(year = %s)")
                params.append(year)
        query = select_movies + " AND ".join(filters)
        params = tuple(params)
        result = execute_select(conn, query, params)
        return result

def get_plot(conn, id):
    query = """SELECT plot, genres FROM movies WHERE id = %s"""
    result = execute_select(conn, query, (id,))
    return result[0][0], result[0][1]

def get_id_plot(conn, stem, core_id):
    query = """SELECT id, plot FROM movies WHERE plot LIKE %s AND id != %s"""
    params = (
        f"%{stem}%",
        core_id
    )
    result = execute_select(conn, query, params)
    return result

def get_movies_by_ids(conn, ids):
        select_movies = """SELECT title, plot, year, genres, runtime, `imdb.rating` FROM movies WHERE """
        filters = ["(id = %s)" for id in ids]
        params = tuple(ids)
        query = select_movies + " OR ".join(filters)
        result = execute_select(conn, query, params)
        return result

def get_id_title(conn, title):
        query = """SELECT id, title FROM movies WHERE title LIKE %s"""
        param = f"%{title}%"
        result = execute_select(conn, query, (param,))
        result_dict = {}
        for row in result:
                result_dict[row[1]] = row[0]
        return result_dict

def record_search(conn, keyword, genre, year, count):
        query = """INSERT INTO search_history (search_term, genre_filter, year_filter, result_count)
                VALUES (%s, %s, %s, %s)"""
        params = (
                keyword if keyword else None,
                genre if genre else None,
                year if year else None,
                count
        )
        execute_insert(conn, query, params)

def get_searches(conn):
        query = """SELECT search_term, genre_filter, year_filter FROM search_history"""
        result = execute_select(conn, query)
        return result

def show_genres(conn):
        query = f"""DESCRIBE movies genres"""
        result = execute_select(conn, query)
        regex = r"'(\w[\w\s-]*)'"
        genres = re.findall(regex,result[0][1])
        genres.insert(0, "Any")
        return genres

def show_year_range(conn, genre):
        query = """SELECT MIN(year), MAX(year) FROM movies"""
        cursor = conn.cursor()
        if genre:
                query += " WHERE genres LIKE %s"
                param = f"%{genre}%"
                cursor.execute(query, (param,))
        else:
                cursor.execute(query)

        result = cursor.fetchone()
        cursor.close()
        min = result[0]
        max = result[1]
        return min, max