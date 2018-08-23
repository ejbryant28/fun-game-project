
import os

from werkzeug.utils import secure_filename

from jinja2 import StrictUndefined

from flask import (g, Flask, render_template, redirect, request, flash, session, url_for, send_from_directory, jsonify)
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


@app.route('/')
def homepage():
    """render homepage"""

    user_id = session['user_id']

    videos = videos_by_date().all()
    challenges = Challenge.query.all()

    categories = PointCategory.query.filter(PointCategory.point_category != 'completion').all()

    points_given = points_by_user_id(user_id).all()

    given_tups = cat_vid_id_tups(points_given)

    return render_template('homepage.html', videos=videos, challenges=challenges, given_tups=given_tups, user_id=user_id)


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
def logout_user():
    """render logout template"""

    return render_template('logout.html')


@app.route('/logout-check')
def logout_check():
    """delete user_id from session if they want to logout"""

    del session['user_id']

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
def user_profile():
    """Show users videos on profile page"""
    user_id = session.get('user_id')

    user = user_by_user_id(user_id).first()

    videos = videos_by_user_id(user_id).all()

    category_levels = UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id).all()

    return render_template('profile.html', videos=videos, category_levels = category_levels)

@app.route('/challenge')
def show_challenges():
    """Show all the available challenges"""

    challenges = Challenge.query.all()

    return render_template('challenges.html', challenges=challenges)


@app.route('/challenge/<challenge_name>')
def show_challenge_videos(challenge_name):
    """Show a specific challenge and all the videos of that challenge"""

    challenge = challenges_by_name(challenge_name).first()

    videos = videos_by_video_challenge(challenge_name).all()

    user_id = session['user_id']

    # points_given = PointGiven.query.filter(PointGiven.user_id == user_id).all()
    points_given = points_by_user_id(user_id).all()

    given_tups = cat_vid_id_tups(points_given)

    completed = video_by_challenge_name_user_id(challenge_name, user_id).first()

    return render_template('challenge_details.html', challenge=challenge, videos=videos, completed=completed, user_id=user_id, given_tups=given_tups)

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

@app.route('/video-upload/')
def upload_file_form():
    """Show form to upload a video"""

    user_id = session['user_id']
    # using request.args, figure out what challenges
    # pass that to jinja to tell them which chanllenge

    tags = Tag.query.all()

    challenges = Challenge.query.all()
    # challenge = request.args.get('challenge_name')


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

            #add a completion point to PointGiven table for the user

            new_point = PointGiven(video_id=video.video_id, point_category='completion', time_given=video.date_uploaded, user_id=user_id)
            db.session.add(new_point)

            #enter video into VideoPointTotals table with initial values at 0 (excluding social and completion points)
            categories = PointCategory.query.filter(PointCategory.point_category != 'completion').all()

            for category in categories:
                new_point = VideoPointTotals(video_id = video.video_id, point_category=category.point_category, total_points = 0)
                db.session.add(new_point)

            db.session.commit()

            return redirect('/video-upload/{}'.format(filename))

    else:
        flash("oops. Something went wrong. Check the file extension on your file")
        return redirect('/video-upload')


@app.route('/video-upload/<filename>')
def show_video_details(filename):
    """Show details for a given video"""

    video = videos_by_filename(filename).first()

    points = video_points_by_video_id(video.video_id).all()

    user_id = session['user_id']
    points_given = points_by_user_id(user_id).all()

    given_tups = cat_vid_id_tups(points_given)

    return render_template('video_details.html', video=video, points=points, given_tups=given_tups, user_id=user_id)

@app.route('/add_point', methods=["POST"])
def add_point():
    """"""

    category_video_id = request.form.get('cat_vid_id')
    cv_list = category_video_id.split('_')
    category = cv_list[0]
    video_id = cv_list[1]

    now = datetime.now()

    user_id = session['user_id']

    #add a point to point_given table:
    new_point = PointGiven(video_id=video_id, point_category= category, time_given=now, user_id=user_id)
    db.session.add(new_point)

    
    #change point totals table to add new point
    video_points = video_point_totals_by_video_id_point_category(video_id, category).first()
    video_points.total_points += 1

    #change user level table and check to see if leveled up
    user_point = UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id, UserLevelCategory.point_category == 'social').first()
    user_point.user_total_points += 1

    level = CategoryLevelPoints.query.filter(CategoryLevelPoints.point_category == 'social', CategoryLevelPoints.points_required < user_point.user_total_points).order_by(CategoryLevelPoints.level_number.desc()).first()
    print("FIRST LEVEL IS", level.level_number)
            
    if level.level_number > user_point.level_number:
        user_point.level_number = level.level_number
        print("NEW LEVEL IS", level.level_number)
    else:
        print("IT STAYED THE SAME")

    db.session.commit()

    point_value = {'value' :video_points.total_points, 'cat_vid_id': category_video_id}
    return jsonify(point_value)


######################################################################################################################################
if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, 'postgres:///project')

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')