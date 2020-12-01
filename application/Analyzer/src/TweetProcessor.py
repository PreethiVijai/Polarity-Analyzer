
import Polarity
import uuid
import json


class TweetProcessor:
    def __init__(self):
        self.keyword = ['Microsoft']

    # Placeholder Implementation: detects threat if tweet longer then 50 characters
    def process_tweet(self, tweet):
        print(tweet)
        # Cast tweet bytestring to JSON object
        tweet = json.loads(tweet)
        location = self.get_tweet_location(tweet)
        if location is None:
            return None
       
        polarity_coeff = self.get_tweet_polarity(tweet)
        if polarity_coeff is None:
            return None
        tweets = [tweet]
        
        return Threat.Threat(uuid.uuid4().int, polarity_coeff, location, tweets)

    def get_tweet_location(self, tweet):
        if 'data' not in tweet:
            return None
        data = tweet['data']
        if 'entities' not in data:
            return None
        entities = data['entities']
        if 'annotations' not in entities:
            return None
        annotations = entities['annotations']
        for annotation in annotations:
            if annotation['type'] == 'Place' and annotation['normalized_text'] is not None:
                return annotation['normalized_text']
        return None

    def get_tweet_polarity(self, tweet):
        #TBD code to generate sentiment analysis for tweet 
        if 'data' not in tweet:
            return None
        data = tweet['data']
        if 'text' not in data:
            return None
        text = data['text']
        for search in self.keyword:
            if search.lower() in text.lower():
                return search

