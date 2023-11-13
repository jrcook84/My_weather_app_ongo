#I want to make the scripts from week two and week 3
#idea is to take the users input store it in a database use a join on the weather db and make recomendations based off of that join
#need to reformat both scripts to work together

import time
from uszipcode import SearchEngine
from noaa_sdk import noaa
import sqlite3
import datetime

# Function to get zip code based on city name
def get_zipcode(city):
    search = SearchEngine(simple_zipcode=True)
    result = search.by_city(city)
    if result:
        return result[0].zipcode
    else:
        return None

# Timed print statement
print('My weather app ')
time.sleep(0.5)
print('App: Weather Advisor')
time.sleep(0.5)
print('Created by: Peter Cook')
time.sleep(0.5)

name = input('What do they call you: ')
city = input('Where are you from.... just the city... not at all for stalking purposes:  ')
age = int(input('How old are you? '))
#commenting out because i want the recomendations to come from the information in the weather db
# temperature = int(input('What is the temperature? check your phone or turn on the news its not that hard. '))

# Get zip code based on the user's input city
zipcode = get_zipcode(city)

if zipcode:
    print(f"The zip code for {city} is {zipcode}")
else:
    print(f"Zip code not found for {city}")

# Proceed with weather data retrieval only if zip code is available
if zipcode:
    # Weather data parameters
    country = "US"
    today = datetime.datetime.now()
    past = today - datetime.timedelta(days=14)
    start_date = past.strftime("%Y-%m-%dT00:00:00Z")
    end_date = today.strftime("%Y-%m-%dT23:59:59Z")

    # Connect to the weather database
    print("Preparing database...")
    db_file = "weather.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Drop previous version of the table if any
    drop_table_cmd = "DROP TABLE IF EXISTS observations;"
    cur.execute(drop_table_cmd)

    # Create a new table to store observations
    create_table_cmd = """CREATE TABLE IF NOT EXISTS observations ( 
                           timestamp TEXT NOT NULL PRIMARY KEY, 
                           city TEXT,
                           windSpeed REAL,
                           temperature REAL,
                           relativeHumidity REAL,
                           windDirection INTEGER,
                           barometricPressure INTEGER,
                           visibility INTEGER,
                           textDescription TEXT
                        );"""
    cur.execute(create_table_cmd)
    print("Database prepared")

    # Get hourly weather observations from NOAA Weather Service API
    print("Getting weather data...")
    n = noaa.NOAA()
    observations = n.get_observations(zipcode, country, start_date, end_date)

    # Populate the table with weather observations
    print("Inserting rows...")
    insert_cmd = """INSERT INTO observations 
                       (timestamp, city, windSpeed, temperature, relativeHumidity, 
                        windDirection, barometricPressure, visibility, textDescription)
                    VALUES
                       (?, ?, ?, ?, ?, ?, ?, ?, ?) """
    count = 0
    for obs in observations:
        insert_values = (obs["timestamp"],
                         city,
                         obs["windSpeed"]["value"],
                         obs["temperature"]["value"],
                         obs["relativeHumidity"]["value"],
                         obs["windDirection"]["value"],
                         obs["barometricPressure"]["value"],
                         obs["visibility"]["value"],
                         obs["textDescription"])
        cur.execute(insert_cmd, insert_values)
        count += 1
    if count > 0:
        cur.execute("COMMIT;")
    print(count, "rows inserted")
    print("Database load complete!")

    # Additional operations: Query and display data
    print("Querying and displaying data...")
    cur.execute("SELECT * FROM observations;")
    rows = cur.fetchall()

    # Display the results
    for row in rows:
        print(row)

    # Close the connection
    conn.close()
