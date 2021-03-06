
import os

from werkzeug.utils import secure_filename

from jinja2 import StrictUndefined

from flask import (g, Flask, render_template, redirect, request, flash, session, url_for, send_from_directory, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from functools import wraps

from model import *

from datetime import datetime, timedelta

import pytz

from queries import *

from helper_functions import *

from sqlalchemy import func

import bcrypt

from random import randint


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
    ok_urls = ['/login', '/login-check', '/add-user-form', '/add-user', '/about',] # '/static/css/style.css', '/static/photos/bright-3324408_1920.jpg']
    if (user_id is None) and (current_url not in ok_urls) and not current_url.startswith('/static'):
        return redirect('/login')


@app.route('/')
def homepage():
    """render homepage"""
    
    user_id = session['user_id']

    # videos = videos_by_date().all()
    videos = videos_by_date().limit(5)
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
        print(flash_messages)
    
        for message in flash_messages:
            if message[0]=='point':
                print('found a point')
                flash(message[1], "point")
            if message[0]=='level':
                print('found a level')
                flash(message[1], 'level')

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
    # hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    #query database to see if username entered exists
    user = User.query.filter(User.username==username).first()

    if user is None:
        #Suggest create profile or check username

        flash("Ooops. The username that username doesn't exist. Try again.", "alert")
        return redirect('/login')

    else:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):

            flash("You're logged in!", "alert")
            session['user_id'] = user.user_id

            return redirect('/')

        else:
            #suggest they check their password
            flash("Ooops. Looks like you entered your password incorrectly.", "alert")
            return redirect('/login')

@app.route('/logout')
def logout_user():
    """render logout template"""

    return render_template('logout.html')


@app.route('/logout-check')
def logout_check():
    """delete user_id from session if they want to logout"""

    del session['user_id']

    flash("You're logged out. See you next time.", "alert")
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

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    #check if the username is already taken
    user_check = user_by_username(username).first()

    if user_check == None:

        #add info to database and redirect to homepage if username is available
        flash('Welcome!', "alert")

        user = User(name=name, username=username, email=email, password=hashed.decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        #add entries to the UserLevelCategory for all the point categories
        categories = PointCategory.query.all()
        for category in categories:
            user_points = UserLevelCategory(user_id=user.user_id, point_category=category.point_category, user_total_points=0, level_number=1, last_updated=datetime.now())
            db.session.add(user_points)
        db.session.commit()
        session['user_id'] = user.user_id

        return redirect('/about')
    
    else:
        #suggest trying a different username if it's already being used
        flash('Sorry, that username is taken. Try another', "alert")
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

    return render_template('profile.html', videos=videos, category_levels = category_levels)


@app.route('/challenge')
def show_challenges(): #pragma no cover
    """Show all the available challenges"""

    user_id = session['user_id']

    challenges = Challenge.query.all()

    completed_videos = Video.query.filter(Video.user_id==user_id).all()
    completed = {}
    for video in completed_videos:
        for thing in video.video_challenge:
            completed[thing.challenge_name] = video.filename

    return render_template('challenges.html', challenges=challenges, completed=completed)


@app.route('/challenge/<challenge_name>')
def show_challenge_videos(challenge_name): #pragma no cover
    """Show a specific challenge and all the videos of that challenge"""

    challenge = challenges_by_name(challenge_name).first()

    videos = videos_by_video_challenge(challenge_name).all()

    user_id = session['user_id']

    points_given = social_points(user_id).all()

    given_tups = cat_vid_id_tups(points_given)

    completed = video_by_challenge_name_user_id(challenge_name, user_id).first()

    return render_template('challenge_details.html', challenge=challenge, videos=videos, completed=completed, user_id=user_id, given_tups=given_tups)

@app.route('/tags')
def show_all_tags():

    tags = Tag.query.all()

    return render_template('tags.html', tags=tags)

@app.route('/tags/<tag_name>')
def show_tag(tag_name): #pragma no cover


    videos = db.session.query(Video).join(VideoTag).filter(VideoTag.tag_name==tag_name).order_by(Video.date_uploaded.desc()).all()

    user_id = session['user_id']

    points_given = social_points(user_id).all()

    given_tups = cat_vid_id_tups(points_given)


    return render_template('tag_details.html', videos=videos, user_id=user_id, given_tups=given_tups)

@app.route('/about')
def show_about():

    user_id = session['user_id']

    user = User.query.filter(User.user_id==user_id).first()

    return render_template('about.html', user=user)

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

@app.route('/video-upload/challenge/<challenge_name>')
# @app.route('/video-upload/')
def upload_file_form(challenge_name):
    """Show form to upload a video"""

    user_id = session['user_id']
    tags = Tag.query.all()
    challenge = Challenge.query.filter(Challenge.challenge_name==challenge_name).first()

    return render_template('video_upload_form.html', challenge=challenge, tags=tags)


@app.route('/video-upload-submit', methods=['GET', 'POST']) #pragma no cover
def upload_file(): 
    """Upload video and save file to uploads folder
    ##It's not possible to effectively test this route. Most people seem to just make a mock route and test that the folder works  
    """

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', "alert")
            return redirect('/video-upload')

        file = request.files['file']
        print('file is', file)

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', "alert")
            return redirect('/video-upload')

        if file and allowed_file(file.filename):
            print('got into the if statement on line 336')
            #find file extension
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            print('file ext is', file_ext)

            #create new file name using user_id, file_ext, and date_uploaded
            new_name = name_file()
            print('named file', new_name)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            print('i tried to save it in the uploads folder')

            #add video to database
            user_id = session.get('user_id')
            # date_uploaded = datetime.now(tz=pytz.timezone('US/Pacific'))
            now = datetime.now(tz=pytz.timezone('US/Pacific'))
            # delta = timedelta(days=(-randint(0, 21)))
            # time = now+delta
            # print('im recording it as ', time)
            filename = name_file()
            # video = Video(user_id=user_id, date_uploaded=now, filename=new_name)

            delta = timedelta(days=(randint(0, 20)))
            time = now+delta
            video = Video(user_id=user_id, date_uploaded=time, filename=new_name)


            db.session.add(video)
            print('added the video')
            db.session.commit()
            print(' i added the video with the name ', new_name)

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

            return redirect('/video-upload/{}'.format(new_name))
            # return redirect('/')


    else:
        flash("oops. Something went wrong. Check the file extension on your file", "alert")
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

######################################################################################################################################
##AJAX routes

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
def make_point_chart(): #pragma no cover
    """ generates the data for a chart on profile showing completed and in-progress levels"""

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
def make_progress_chart(): #pragma no cover

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
if __name__ == "__main__": #pragma no cover
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, 'postgres:///project')

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')