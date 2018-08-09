
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

    # friend = db.relationship("Connections", backref=db.backref("users"))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User username= {} name = {} email = {}>".format(self.username, self.name, self.email)

# class Connections(db.Model):
#     """Connects users to each other"""

#     __tablename__="connections"

#     friendship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     user_id_1 = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#     user_id_2 = db.Column(db.Integer, db.ForeignKey('users.user_id'))

#     def __repr__(self):
#         """Provide helpful representation when printed"""

#         return "<User user_id_1= {} user_id_2 = {}>".format(self.user_id_1, self.user_id_2)

class Video(db.Model):
    """Users model"""

    __tablename__="videos"

    video_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # date = db.Column(db.DateTime, nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False)
    #file names will be stored as userid_video_id.file_ext
    filename = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", backref=db.backref("video"))


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Video video_id= {} user_id = {} date_uploaded = {}>".format(self.video_id, self.user_id, self.date_uploaded)

class Tag(db.Model):
    """The video tags available"""

    __tablename__="tags"

    tag_code = db.Column(db.String(5), primary_key=True)
    tag_name = db.Column(db.String(20), nullable=False)



    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Tags tag_code= {} tag_name = {}>".format(self.tag_code, self.tag_name)

class VideoTag(db.Model):
    """An instance of a video being given a tag"""

    __tablename__="videotags"

    video_tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'))
    tag_code = db.Column(db.String(5), db.ForeignKey('tags.tag_code'))

    video = db.relationship("Video", backref=db.backref("video_tag"))
    tag = db.relationship("Tag", backref=db.backref("video_tag"))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Video-Tags video_id = {} tag_code= {}>".format(self.video_id, self.tag_code)


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