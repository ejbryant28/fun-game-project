
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    """Users model"""

    __tablename__="users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    #add username uniqueness constraint

    # friend = db.relationship("Connections", backref=db.backref("users"))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User username= {} name = {} email = {}>".format(self.username, self.name, self.email)


class Video(db.Model):
    """Users model"""

    __tablename__="videos"

    video_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False)
    filename = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", backref=db.backref("video"))


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Video video_id= {} user_id = {} date_uploaded = {}>".format(self.video_id, self.user_id, self.date_uploaded)

class Tag(db.Model):
    """The video tags available"""

    __tablename__="tags"

    # tag_code = db.Column(db.String(5), primary_key=True)
    tag_name = db.Column(db.String(20), primary_key=True)



    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Tags tag_name = {}>".format(self.tag_name)

class VideoTag(db.Model):
    """An instance of a video being given a tag"""

    __tablename__="videotags"

    video_tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), nullable=False)
    tag_name = db.Column(db.String(20), db.ForeignKey('tags.tag_name'), nullable=False)

    video = db.relationship("Video", backref=db.backref("video_tag"))
    tag = db.relationship("Tag", backref=db.backref("video_tag"))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Video-Tags video_id = {} tag_name= {}>".format(self.video_id, self.tag_name)

class PointCategory(db.Model):
    """All the possible categories of points"""

    __tablename__="pointcategories"

    point_category = db.Column(db.String(20), primary_key=True)


class PointGiven(db.Model):
    """An instance giving a video a point"""

    __tablename__="point_given"

    point_giving_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), nullable=False)
    point_category = db.Column(db.String(20), db.ForeignKey('pointcategories.point_category'), nullable=False)
    time_given = db.Column(db.DateTime, nullable=False)
    #user_id of who GAVE the point
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    user = db.relationship("User", backref=db.backref("point_given")) #this is for who GAVE the point
    video = db.relationship("Video", backref=db.backref("point_given"))
    point_categories = db.relationship("PointCategory")


class Challenge(db.Model):
    """Different instructions for users to complete"""

    __tablename__="challenges"

    challenge_name = db.Column(db.String(20), primary_key=True)
    description = db.Column(db.String(200), nullable=False)

class VideoChallenge(db.Model):
    """Associate video with a challeng"""

    __tablename__="video_challenge"

    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), primary_key=True)
    challenge_name = db.Column(db.String(20), db.ForeignKey('challenges.challenge_name'), nullable=False)

    video = db.relationship("Video", backref=db.backref("video_challenge"))
    challenge = db.relationship("Challenge", backref=db.backref("video_challenge"))
    

class VideoPointTotals(db.Model):
    """tying the user to their total points"""

    __tablename__="video_point_totals"

    point_total_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), nullable=False)
    point_category = db.Column(db.String(20), db.ForeignKey('pointcategories.point_category'), nullable=False)
    total_points=db.Column(db.Integer, nullable=False)

    # point_level = db.relationship("PointLevel", backref=db.backref("user_point_totals"))
    point_categories = db.relationship("PointCategory")
    video = db.relationship("Video", backref=db.backref("video_point_totals"), order_by="VideoPointTotals.point_category")

class CategoryLevelPoints(db.Model):
    """The required number of points required to reach a level in any given point_category"""

    __tablename__="category_level_points"

    point_level_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    point_category = db.Column(db.String(20), db.ForeignKey('pointcategories.point_category'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)
    points_required = db.Column(db.Integer, nullable=False)

    pointcategories = db.relationship("PointCategory")


class UserLevelCategory(db.Model):
    """Find which level a user is at per category"""

    __tablename__ = 'user_level_category'

    user_level_category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    point_category = db.Column(db.String(20), db.ForeignKey('pointcategories.point_category'))
    user_total_points = db.Column(db.Integer, nullable=False)
    level_number = db.Column(db.Integer, db.ForeignKey("category_level_points.point_level_id"), nullable=False)

    user = db.relationship("User", backref=db.backref("user_level"))
    pointcategories = db.relationship("PointCategory")
    level = db.relationship("CategoryLevelPoints", backref=db.backref("user_level"))


def connect_to_db(app, database):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    print("Connected to DB")


if __name__ == "__main__":

    from server import app 
    connect_to_db(app, 'postgres:///project')
    db.create_all()