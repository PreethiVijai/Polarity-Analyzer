import argparse
from time import sleep
import json
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from RabbitSender import RabbitSender


class listener(StreamListener):
    def on_status(self, status):
        print(status.user.location)
        rabbit_sender = RabbitSender('tweet')
        rabbit_sender.prepare_connection("rabbitmq")
        rabbit_sender.send_message(status.text+" LOC "+str(status.user.location))

    def on_data(self, data):
        j = json.loads(data)
        try:
            print("test")
            if j['user']['location'] is not None and j['text'] is not None:
                rabbit_sender = RabbitSender('tweet')
                rabbit_sender.prepare_connection("rabbitmq")
                rabbit_sender.send_message(j['text']+" LOC "+j['user']['location'])       
        except KeyError:
            print("error")


    def on_error(self, status):
        print(status)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('rabbit_host', help='Hostname of RabbitMQ instance to connect to')
    parser.add_argument('keyword')
    return parser.parse_args()


def main(rabbit_host,keyword):
    ckey="4xXQLsSwFyELZeeBpbXNwZCZj"
    csecret="VyYZXqUErrnRjOBTBWxAb8SIDNri1EVT5OVEVEH7PLJbGtS9Td"
    atoken="2877104310-HNcYKKiTJ15SuOFiLicZwMiboW6gqA9INEyTX59"
    asecret="KYXiJPBKutnXErcrC5mEVxwGdUGfZ5Dp503yVn9CFTafI"
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    

    twitterStream = Stream(auth, listener())
    twitterStream.filter(track=[keyword])


if __name__ == '__main__':
    print("launching\n")
    args = parse_args()
    main(args.rabbit_host,args.keyword)

