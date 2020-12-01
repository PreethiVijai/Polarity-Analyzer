
from datetime import date
import mysql.connector
import json


add_threat = ("INSERT INTO POLARITY_TBL "
              "(id, polarity, location, tweets,date) "
              "VALUES (%(id)s, %(polarity)s, %(location)s, %(tweets)s, %(date)s)")


class DatabaseAccesser:
    def __init__(self, address, database):
        self.address = address
        self.database = database
        self.time_func = date.today

    def prepare_connection(self):
        self.connection = mysql.connector.connect(user="root", password="", host=self.address, database=self.database)

    def add_tweet(self, tweet_data):
        cursor = self.connection.cursor()
        data_tweet = {
            'id': tweet_data.ID,
            'polarity': tweet_data.polarity,
            'location': bytes(tweet_data.location, 'utf-8').decode('utf-8', 'ignore'),
            'tweets': bytes(json.dumps(tweet_data.tweets), 'utf-8').decode('utf-8', 'ignore'),
            'date': self.time_func()
        }
        cursor.execute(add_threat, data_tweet)
        self.connection.commit()
        cursor.close()

    def shutdown(self):
        self.connection.close()
