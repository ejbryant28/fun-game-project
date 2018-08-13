
import os

from werkzeug.utils import secure_filename

from jinja2 import StrictUndefined

from flask import (g, Flask, render_template, redirect, request, flash, session, url_for, send_from_directory)
from flask_debugtoolbar import DebugToolbarExtension
from functools import wraps

from model import *

from datetime import datetime

import pytz

from queries import *

from helper_functions import *


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

#Make sure jinja tells you if you're using an undifined variable
app.jinja_env.undefined = StrictUndefined

######################################################################################################################################

@app.before_request
def before_request():
    """redirect user if they aren't logged in"""
    current_url = request.path
    user_id = session.get('user_id')
    ok_urls = ['/login', '/login-check', '/add-user-form', '/add-user']
    if (user_id is None) and (current_url not in ok_urls):
        return redirect('/login')
        # return redirect(url_for('/login'))

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         user_id = session['user_id']
#         if user_id is None:
#             return redirect('/login')
            
#         return f(*args, **kwargs)

#     return decorated_function


@app.route('/')
# @login_required
def homepage():
    """render homepage"""

    user_id = session['user_id']

    videos = videos_by_date().all()
    challenges = Challenge.query.all()

    return render_template('homepage.html', videos=videos, challenges=challenges)


@app.route('/login')
def login_form():
    """render login form"""

    return render_template('login_form.html')


@app.route('/login-check', methods=["POST"])
def check_login_info():
    """check login info from login form"""

    username = request.form.get('username')
    username = username.lower()
    password = request.form.get('password')

    #query database to see if username entered exists
    # user_info = user_by_username().first()
    user_info = User.query.filter(User.username==username).first()

    if user_info is None:
        #Suggest create profile or check username

        flash("""Ooops. The username you entered isn't in our database. 
                    Are you sure you entered it correctly? Do you want to
                    create a profile?""")
        return redirect('/login')

    elif user_info.password == password:
        #add user's info to session and redirect to homepage

        flash("You're logged in!")
        session['user_id'] = user_info.user_id
        return redirect('/')

    else:
        #suggest they check their password
        flash("Ooops. Looks like you entered your password incorrectly.")
        return redirect('/login')

@app.route('/logout')
# @login_required
def logout_user():
    """render logout template"""

    return render_template('logout.html')


@app.route('/logout-check')
def logout_check():
    """delete username from session if they want to logout"""
    del session['user_id']
    # session['user_id'] = None
    # print(session['user_id'])

    flash("You're logged out. See you next time.")
    return redirect('/login')


@app.route('/add-user-form')
def add_user_form():
    """show form to add new user"""

    return render_template('add_user.html')


@app.route('/add-user', methods=['POST'])
def add_user():
    """add new user to database"""

    #get info entered from form
    name = request.form.get('name')
    name = name.lower()

    username = request.form.get('username')
    username = username.lower()

    email = request.form.get('email')
    email = email.lower()
    
    password = request.form.get('password')

    #check if the username is already taken
    user_check = user_by_username(username).first()
    # user_check = User.query.filter(User.username==username).first()
    print(user_check)

    if user_check == None:

        #add info to database and redirect to homepage if username is available
        flash('Welcome!')

        user = User(name=name, username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.user_id

        return redirect('/')
    
    else:
        #suggest trying a different username if it's already being used
        flash('Sorry, that username is taken. Try another')
        return redirect('/add-user-form')

@app.route('/profile')
# @login_required
def user_profile():
    """Show users videos on profile page"""
    user_id = session.get('user_id')

    user = user_by_user_id(user_id).first()

    # user = User.query.filter(User.user_id==user_id).first()
    username = user.name.capitalize()

    # videos = videos_by_user_id(user_id).first()
    videos = videos_by_user_id(user_id).all()

    points_dict = make_points_dictionary(user_id)

    return render_template('profile.html', videos=videos, username=username, points_dict=points_dict)

######################################################################################################################################
#video-upload functions

UPLOAD_FOLDER = './static/uploads'

ALLOWED_EXTENSIONS = set(['webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif', 'gifv', 'mng', 'avi',
                         'mov', 'qt', 'wmv', 'yuv', 'rm', 'amv', 'mp4', 'm4p', 'm4v', 'f4v', 'f4p', 'f4a', 'f4b'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/video-upload')
# @login_required
def upload_file_form():
    """Show form to upload a video"""

    tags = Tag.query.all()
    # tags = tags().all()
    print("TAGS ARE", tags)

    # challenges = challenges().all()
    challenges = Challenge.query.all()

    return render_template('video_upload_form.html', challenges=challenges, tags=tags)


@app.route('/video-upload-submit', methods=['GET', 'POST'])
def upload_file():
    """Upload video and save file to uploads folder"""

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/video-upload')

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/video-upload')

        if file and allowed_file(file.filename):
            #find file extension
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()

            #create new file name using user_id, file_ext, and date_uploaded
            filename = name_file(file_ext)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #add video to database
            user_id = session.get('user_id')
            date_uploaded = datetime.now(tz=pytz.timezone('US/Pacific'))
            video = Video(user_id=user_id, date_uploaded=date_uploaded , filename=filename)

            db.session.add(video)
            db.session.commit()

            #get tags selected and add them to video_tags table
            tags = request.form.getlist('tag')
            for tag in tags:
                videotag = VideoTag(video_id=video.video_id, tag_name=tag)
                db.session.add(videotag)

            #get challenge and add that to video_challenge table
            challenge_name = request.form.get('challenge')
            video_challenge = VideoChallenge(video_id=video.video_id, challenge_name=challenge_name)
            db.session.add(video_challenge)

            db.session.commit()

            return redirect('/video-upload/{}'.format(filename))

    else:
        flash("oops. Something went wrong. Check the file extension on your file")
        return redirect('/video-upload')


    #this was the original else return:
    # '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''

@app.route('/video-upload/<filename>')
# @login_required
def show_video_details(filename):
    """Show details for a given video"""

    video = videos_by_filename(filename).first()

    return render_template('video_details.html', video=video)

@app.route('/challenge')
def show_challenges():
    """Show all the available challenges"""

    challenges = Challenge.query.all()
    # challenges = challenges().all()

    return render_template('challenges.html', challenges=challenges)


@app.route('/challenge/<challenge_name>')
def show_challenge_videos(challenge_name):
    """Show a specific challenge and all the videos of that challenge"""

    # challenge = Challenge.query.filter(Challenge.challenge_name==challenge_name).first()
    challenge = challenges_by_name(challenge_name).first()

    videos = db.session.query(Video).join(VideoChallenge).filter(VideoChallenge.challenge_name == challenge_name).order_by(Video.date_uploaded.desc()).all()

    return render_template('challenge_details.html', challenge=challenge, videos=videos)


######################################################################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, 'postgres:///project')

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')