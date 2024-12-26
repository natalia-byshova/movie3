import configparser
import mysql.connector
from colorama import init, Fore

# configure connection credentials
config = configparser.ConfigParser()
config.read('config.ini')

#create a connection
def connect():
    conn = None
    print("\n" + Fore.GREEN + "\u276F", end=' ')
    print("Connecting to the database...")
    try:
        conn = mysql.connector.connect(
            host=config['6000movies']['host'],
            username=config['6000movies']['username'],
            password=config['6000movies']['password'],
            database=config['6000movies']['database']
        )
    except mysql.connector.Error as err:
        print(f"Something went wrong while connecting to the database: {err}")
    return conn