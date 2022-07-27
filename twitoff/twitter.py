import os
import tweepy
import spacy
from .models import DB, Tweet, User


key = os.getenv('TWITTER_API_KEY')
secret = os.getenv('TWITTER_API_KEY_SECRET')


twitter_auth = tweepy.OAuthHandler(key, secret)
twitter = tweepy.API(twitter_auth)


# Load our pretrained spacy word embeddings model
nlp = spacy.load('my_model')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


def add_or_update_user(username):
    # Look up user using twitter API
    twitter_user = twitter.get_user(screen_name=username)

    # Check if user exists in DB already
    db_user = User.query.get(twitter_user.id)
    if db_user is None:
        db_user = User(id=twitter_user.id, username=username)
        # Add user to DB
        DB.session.add(db_user)

    # Get user's tweets
    tweets = twitter_user.timeline(
        count=200,
        exclude_replies=True,
        include_rts=False,
        tweet_mode='extended'
    )

    # Add each tweet to the DB
    for tweet in tweets:
        db_tweet = Tweet(
            id=tweet.id, 
            text=tweet.full_text,
            vector=vectorize_tweet(tweet.full_text)
        )
        if Tweet.query.get(db_tweet.id) is None:
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    
    DB.session.commit()