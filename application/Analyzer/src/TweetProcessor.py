import Polarity
import uuid
import json
from textblob import TextBlob
import string
import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk import sent_tokenize
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

class TweetProcessor:
    def __init__(self):
        self.keyword = ['Microsoft']

    # Placeholder Implementation: detects threat if tweet longer then 50 characters
    def process_tweet(self, tweet):
        #print(str(tweet))
        # Cast tweet bytestring to JSON object
        loc_index = str(tweet).find("LOC")
        temp_tweet  = str(tweet).split(" LOC ")
        tweets = tweet[0:20]
        #location = tweet[loc_index+1:]
        location = temp_tweet[1]
        location = location[:-1]
        print(location)
        polarity_coeff = self.get_tweet_polarity(str(tweet))
        wordMap = self.fetch_WordMap_words(str(tweet))
        wordMap_words = ''
        for words in wordMap:
            wordMap_words += words
            wordMap_words += ' '
        #print("*****************", wordMap_words, "*************")
        return Polarity.Polarity(int(str(uuid.uuid4().int)[:5]), polarity_coeff, location, wordMap_words)
    
    
    def fetch_WordMap_words(self, tweet):
        tweet = re.sub(r'[^\w\s]',' ',tweet)
        tokenizer = TweetTokenizer()
        stop_words = set(stopwords.words('english')) 
        lemmatizer = WordNetLemmatizer()

        tokens = tokenizer.tokenize(tweet)
        lemmas = []
        for word in tokens:
            if word.isalpha() and not word in stop_words:
                word = word.lower()
                word = lemmatizer.lemmatize(word, pos = 'v')
                if len(word)>=4:
                    lemmas.append(word)
        tokens = lemmas
        #print(tokens)
        while "" in tokens:
            tokens.remove("")
        while " " in tokens:
            tokens.remove(" ")
        while "\n" in tokens:
            tokens.remove("\n")
        while "\n\n" in tokens:
            tokens.remove("\n\n")
        return tokens

    def get_tweet_polarity(self, tweets):
        def percentage(part,whole):
            return 100*float(part)/float(whole)
        #TBD code to generate sentiment analysis for tweet 
        noofTerms = len(tweets)
        neutral,positive,negative = 0,0,0
        analysis=TextBlob(tweets)
        print(analysis.sentiment.polarity)
        if(analysis.sentiment.polarity==0.0):
            return 0
        elif(analysis.sentiment.polarity>0.00):
            return 1
        elif(analysis.sentiment.polarity<0.00):
            return -1
        '''

        for tweet in tweets:
            analysis=TextBlob(tweet)
            #polarity+=analysis.sentiment.polarity
            if(analysis.sentiment.polarity==0.0):
                neutral+=1
            elif(analysis.sentiment.polarity>0.00):
                positive+=1
            elif(analysis.sentiment.polarity<0.00):
                negative+=1

           
            if(analysis.sentiment.polarity==0.0):
                df['Sentiment'][i]=1
            elif(analysis.sentiment.polarity>0.0):
                df['Sentiment'][i]=2
            elif(analysis.sentiment.polarity<0.0):
                df['Sentiment'][i]=0
            

            positive=percentage(positive,noofTerms)
            negative=percentage(negative,noofTerms)
            neutral=percentage(neutral,noofTerms)
            print(positive,negative,neutral)
            '''
 

