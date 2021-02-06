import pandas as pd
import os
import requests
import sqlite3
import json
from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("https://developer.spotify.com/console/get-recently-played/")
DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USERNAME = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')


def get_token():
    try:
        driver.find_element(By.ID, 'fill-sample-data').click()
        btn = WebDriverWait(driver, 10).until(
             EC.presence_of_element_located((By.XPATH, "//*[@id=\"console-form\"]/div[3]/div/span/button"))
        )
        btn.send_keys(Keys.RETURN)
        time.sleep(0.5)
        driver.find_element(By.ID, 'scope-user-read-recently-played').send_keys(Keys.RETURN)
        time.sleep(0.5)
        # choose to login with facebook.
        driver.find_element(By.XPATH, '//*[@id="app"]/body/div[1]/div[2]/div/div[2]/div/a').send_keys(Keys.RETURN)
        driver.find_element(By.ID, 'email').send_keys(USERNAME)
        driver.find_element(By.ID, 'pass').send_keys(PASSWORD)
        driver.find_element(By.ID, 'loginbutton').click()
        token_text = driver.find_element(By.ID, 'oauth-input')
        token = token_text.get_attribute('value')
    except:
        driver.quit()
    return token


def check_data_valid(df: pd.DataFrame) -> bool:
    # check for empty DataFrame
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    # Primary key check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check is Violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null value found")

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    # If the timestamps do not equal yesterdays time stamps they were not played yesterday.
    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("A song in the data was not from the last 24 hours")
    return True


# These are the perams  that Spotify needs to send you data
if __name__ == '__main__':
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=get_token())
    }

    driver.close()
    # Creates a unix timestamp in milliseconds for yesterdays date. So *1000
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers=headers)
    data = r.json()

    # We create empty lists that we are going to fill and make into a dictionary and then create a DataFrame.
    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # loop through every song that in the json file (from yesterday) and append info into our empty lists.
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    # Take those lists we just created and put them into a DICT, this is so that our data frame will be neat.
    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps
    }

    # Uses our Dict that Uses our List and puts it all in a nice DataDrame.
    song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])

    # Validate
    if check_data_valid(song_df):
        print("Data valid")

    # Load
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect('my_played_tracks.sqlite')
    cursor = conn.cursor()

    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)

    try:
        song_df.to_sql("my_played_tracks", engine, index=False, if_exists='append')
        print("Process Successful")
    except:
        print("Data already exists in the database")



