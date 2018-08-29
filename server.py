
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

from sqlalchemy import func

import bcrypt


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

    points_given = social_points(user_id).all()

    given_tups = cat_vid_id_tups(points_given)

    #query find most recent entry in in UserLevel
    date_table_updated = UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id).order_by(UserLevelCategory.last_updated.desc()).first()

    #find most recent entry in points_given table
    new_point = None
    if date_table_updated:
        new_point = newest_points(user_id, date_table_updated.last_updated).first()


    #check if they're different
    if new_point:
        flash_messages = []

        #if different, find all the points that are more recent than date updated
        new_points = newest_points(user_id, date_table_updated.last_updated).all()

        #call function that updates all the tables and returns flash messages
        flash_messages = update_tables(new_points, user_id)
    
        for message in flash_messages:
            flash(message)

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
    bpass = b'password'
    hashed = bcrypt.hashpw(bpass, bcrypt.gensalt())

    #query database to see if username entered exists
    user_info = User.query.filter(User.username==username).first()

    if user_info is None:
        #Suggest create profile or check username

        flash("""Ooops. The username you entered isn't in our database. 
                    Are you sure you entered it correctly? Do you want to
                    create a profile?""")
        return redirect('/login')

    elif bcrypt.checkpw(bpass, hashed):
        print("BCRYPT PASSWORD MATCH")

        flash("You're logged in!")
        session['user_id'] = user_info.user_id

        return redirect('/')

    # elif user_info.password == password:
    #     #add user's info to session and redirect to homepage

    #     flash("You're logged in!")
    #     session['user_id'] = user_info.user_id

    #     return redirect('/')

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
    password = b'password'
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    #check if the username is already taken
    user_check = user_by_username(username).first()

    if user_check == None:

        #add info to database and redirect to homepage if username is available
        flash('Welcome!')

        user = User(name=name, username=username, email=email, password=hashed)
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

    test_vid = videos_by_user_id(user_id).first()

    if test_vid:
        videos = videos_by_user_id(user_id).all()
    else:
        videos = []

    category_levels = UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id).all()
    # print("CATEGORY LEVELS ARE", category_levels)
    # for entry in category_levels:
    #     print(entry.point_category, entry.level_number)

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
    points_given = social_points(user_id).all()

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

# @app.route('/video-upload/<challenge-name>')

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

            #query to find users current point numbers for competion and add one
            user_point = UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id, UserLevelCategory.point_category =='completion').first()
            user_point.user_total_points +=1

            #find current level
            current_level = UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id, UserLevelCategory.point_category=='completion').first()
        
            #check to see if user leveled up in completion
            max_level = level_category_current_point('completion', user_point.user_total_points).first()
            
            if max_level.level_number > current_level.level_number:
                current_level.level_number = max_level.level_number

            #enter video into VideoPointTotals table with initial values at 0 (excluding social and completion points)
            categories = PointCategory.query.filter(PointCategory.point_category != 'completion', PointCategory.point_category != 'social').all()

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
    points_given = social_points(user_id).all()

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

    #change social points for user in user level table and check to see if leveled up
    user_point = points_by_user_id_category(user_id, 'social').first()
    user_point.user_total_points += 1

    level = level_category_current_point('social', user_point.user_total_points).first()
            
    if level.level_number >= user_point.level_number:
        user_point.level_number = level.level_number

    db.session.commit()

    point_value = {'value' :video_points.total_points, 'cat_vid_id': category_video_id}
    return jsonify(point_value)


@app.route('/point-chart')
def make_point_chart():

    user_id = session['user_id']

    level_points = UserLevelCategory.query.filter(UserLevelCategory.user_id==user_id).all()

    level_dict = {}

    for entry in level_points:
        curr_level_num = entry.level_number

        #find the next level up 
        curr_level =CategoryLevelPoints.query.filter(CategoryLevelPoints.point_category==entry.point_category, CategoryLevelPoints.level_number ==curr_level_num).first()
        nex_level = CategoryLevelPoints.query.filter(CategoryLevelPoints.point_category==entry.point_category, CategoryLevelPoints.level_number ==curr_level_num+1).first()
    
        #find the difference in point requirements between current level requirements and next level
        difference = nex_level.points_required - curr_level.points_required

        #find the surplus of points that the user has
        excess = entry.user_total_points - curr_level.points_required

        #find the percentace of the difference that the user has finished
        fraction_complete = excess/difference
        
        level_dict[entry.point_category] = [curr_level_num, fraction_complete]

    return jsonify(level_dict)

@app.route('/progress-chart')
def make_progress_chart():

    user_id = session['user_id']

    #find all the points a user has been given 

    points_dict = {}

    points_dict['originality'] = make_chart_core_lst('originality', user_id)

    points_dict['silliness'] = make_chart_core_lst('silliness', user_id)

    points_dict['enthusiasm'] = make_chart_core_lst('enthusiasm', user_id)

    points_dict['artistry'] = make_chart_core_lst('artistry', user_id)

    points_dict['social'] = make_chart_soc(user_id)

    points_dict['completion'] = make_chart_comp(user_id)

    return jsonify(points_dict)


######################################################################################################################################
if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, 'postgres:///project')

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')