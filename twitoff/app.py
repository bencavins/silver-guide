from flask import Flask, render_template, request
from twitoff.models import User, Tweet, DB
from twitoff.twitter import add_or_update_user
from twitoff.predict import predict_user


app = Flask(__name__)
app_title = 'Twitoff DS40'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

DB.init_app(app)


def create_app():

    @app.route('/')
    def hello_world():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)


    @app.route('/test')
    def test():
        return f'<p>Hello from {app_title}</p>'
    
    @app.route('/update')
    def update():
        users = User.query.all()
        for user in users:
            add_or_update_user(user.username)
        return """Updated user
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return """Created some users/tweets
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """
    
    @app.route('/populate')
    def populate():
        user1 = User(id=1, username='joe')
        tweet1 = Tweet(id=1, text='this is a tweet', user=user1)
        DB.session.add(user1)
        DB.session.add(tweet1)
        DB.session.commit()
        return """Created some users/tweets
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """
    
    @app.route('/user', methods=['POST'])
    def add_user():
        username = request.values['user_name']
        add_or_update_user(username)
        db_user = User.query.filter(User.username == username).one()
        return render_template(
            'user.html', 
            title=username, 
            message='',
            tweets=db_user.tweets
        )

    @app.route('/user/<username>')
    def user(username=None):
        db_user = User.query.filter(User.username == username).one()
        return render_template(
            'user.html', 
            title=username, 
            message='',
            tweets=db_user.tweets
        )

    @app.route('/compare', methods=['POST'])
    def compare():
        username0 = request.values['user0']
        username1 = request.values['user1']
        hypo_tweet_text = request.values['tweet_text']

        if username0 == username1:
            message = 'Cannot compare users to themselves!'
        else:
            prediction = predict_user(username0, username1, hypo_tweet_text)
            if prediction:
                predicted_user = username1
            else:
                predicted_user = username0
            message = f'This tweet was more likely written by {predicted_user}'
        
        return render_template(
            'prediction.html', 
            title='Prediction', 
            message=message
        )

    
    return app