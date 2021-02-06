# spotify-played-tracks
Sort previouse day's played tracks into SQL database using Spotify API

# Modules used:
Pandas
Request
sqlite3
selenium
datetme
json
time
sqlalchemy

# Program runthrough
Using the Spotify API the program retrieves previously played tracks and sorts them into SQL database with the goal of long term data analysis
The API uses a QAUTH token that expires every hour, it was decided to use selenium to retrieve the token every time the script was run.
The program checks if all the data is valid via a series of validation checks (checking for empty lists, null values, correct timestamps, unique identifiers)
It then sorts all the retrieved data into sorted lists (song_names, artist_names, played_at, timestamps) 
These listed items are then turned into dictionary items so they can be turned into a DataFrame to be transferred to SQL.
