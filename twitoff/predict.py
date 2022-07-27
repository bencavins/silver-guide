import numpy as np
from sklearn.linear_model import LogisticRegression
from twitoff.models import User
from twitoff.twitter import vectorize_tweet


def predict_user(username0, username1, hypo_tweet_text):
    # Grab both users from the DB
    user0 = User.query.filter(User.username == username0).one()
    user1 = User.query.filter(User.username == username1).one()

    # Grab tweet vectors and put into numpy array
    user0_vectors = np.array([tweet.vector for tweet in user0.tweets])
    user1_vectors = np.array([tweet.vector for tweet in user1.tweets])

    # Vertically stack tweet vectors into one np array
    vector_stack = np.vstack([user0_vectors, user1_vectors])
    labels = np.concatenate([
        np.zeros(len(user0.tweets)),
        np.ones(len(user1.tweets))
    ])

    # fit it all into our model
    log_reg = LogisticRegression().fit(vector_stack, labels)

    # vectorize the hypothetical tweet
    hypo_tweet_vector = vectorize_tweet(hypo_tweet_text)

    # do the prediction
    prediction = log_reg.predict(hypo_tweet_vector.reshape(1, -1))
    print(prediction)
    return prediction