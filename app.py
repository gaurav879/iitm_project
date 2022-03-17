from importlib.resources import Resource
from sqlite3 import Timestamp
from flask import Flask, render_template, request, redirect, session, make_response

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)

db = SQLAlchemy(app)


class User(db.Model):
    tablename = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    username = db.Column(db.String, nullable=False, unique=True)
    pw = db.Column(db.String, nullable=False)
    pass


class Tracker(db.Model):
    tablename = "tracker"
    tracker_id = db.Column(db.Integer, primary_key=True)
    tracker_name = db.Column(db.String, nullable=False)
    tracker_description = db.Column(db.String)
    tracker_user_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    Tracker_type = db.Column(db.String)
    # Settings = db.Column(db.String)
    pass


class Logs(db.Model):
    tablename = "log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    tracker = db.Column(
        db.Integer,
        db.ForeignKey("tracker.tracker_id", ondelete="CASCADE"),
        nullable=False,
    )
    value = db.Column(db.String)
    note = db.Column(db.String)
    pass


class UserLogin(Resource):
    def get(self):
        return make_response(render_template("temp.html"))

    def post(self):
        _username = request.form["username"]
        pw = request.form["_password"]

        temp_user = User.query.all()

        for i in temp_user:
            if _username == i.username and pw == i.pw:
                id = i.user_id
                return redirect(f"/{id}/trackerlist")
        return "Either username or password wrong"


class UserOperations(Resource):
    def get(self):
        return make_response(render_template("sign.html"))

    def post(self):
        new_user = User(
            first_name=request.form["first_name"],
            last_name=request.form["username"],
            username=request.form["username"],
            pw=request.form["_password"],
        )
        _username = request.form["username"]
        temp_user = User.query.all()
        for i in temp_user:
            if _username == i["username"]:
                return "user already exist"
        db.session.add(new_user)
        db.session.commit()
        return "user added"


class TrackerOperations(Resource):
    def get(self, user_id):
        temp_user = User.query.all()
        for i in temp_user:
            if i.user_id == user_id:
                temp = i
        temp_trackers = Tracker.query.filter(
            Tracker.tracker_user_id == temp.user_id
        ).all()

        data = {"data": temp_trackers}
        return make_response(
            render_template(
                "tracker_display.html",
                data=temp_trackers,
                id=temp.user_id,
                username=temp.username,
            )
        )


class NewTracker(Resource):
    def get(self, user_id):
        return make_response(render_template("addtrack.html", user_id=user_id))

    def post(self, user_id):
        new_tracker = Tracker(
            tracker_name=request.form["tracker_name"],
            tracker_description=request.form["tracker_description"],
            tracker_user_id=user_id,
            Tracker_type=request.form["type"],
        )
        db.session.add(new_tracker)
        db.session.commit()
        return redirect(f"/{user_id}/trackerlist")


class TrackerDeletion(Resource):
    def get(self, user_id, tracker_id):
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        db.session.delete(temp_tracker)
        db.session.commit()
        return redirect(f"/{user_id}/trackerlist")


class TrackerUpdate(Resource):
    def get(self, user_id, tracker_id):
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        return make_response(
            render_template("updatetracker.html", tracker=temp_tracker, user_id=user_id)
        )

    def post(self, user_id, tracker_id):
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        print(temp_tracker.tracker_name)
        print(request.form["tracker_name"])
        temp_tracker.tracker_name=request.form["tracker_name"]
        temp_tracker.tracker_description=request.form["tracker_description"]
        temp_tracker.Tracker_type=request.form["type"]
        print(temp_tracker.tracker_name)
        db.session.commit()
        return redirect(f"/{user_id}/trackerlist")


class AddTracker(Resource):
    def get(self, user_id, tracker_id):
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        temp_logs = Logs.query.filter(Logs.tracker == tracker_id).all()
        return make_response(
            render_template("updatetracker.html", logs=temp_logs,tracker_name=temp_tracker.tracker_name, user_id=user_id)
        )


class TrackerLogs(Resource):
    def get(self, user_id, tracker_id):
        temp_user=User.query.filter(User.user_id==user_id).first()
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        logs=Logs.query.filter(Logs.tracker==tracker_id).order_by(Logs.timestamp).all()

        return make_response(
            render_template("trackerlogs.html", tracker=temp_tracker, user=temp_user,logs=logs)
        )


class AddLogs(Resource):
    def get(self,user_id,tracker_id):
        temp_user=User.query.filter(User.user_id == user_id).first()
        
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        print(temp_tracker)
        return make_response(
            render_template("addlogs.html", tracker=temp_tracker, user=temp_user)
        )

    def post(self,user_id,tracker_id):
        print("00")
        new_log=Logs(timestamp=str(request.form["date"]+" "+request.form["time"]),tracker=tracker_id,value=request.form["value"],note=request.form["note"])
        db.session.add(new_log)
        db.session.commit()
        return redirect(f"/{user_id}/trackerlist")


class DeleteLogs(Resource):
    def get(self, user_id, tracker_id,id):
        temp_tracker = Logs.query.filter(Logs.id == id).first()
        db.session.delete(temp_tracker)
        db.session.commit()
        return redirect(f"/{user_id}/{tracker_id}/trackerlogs")


class UpdateLogs(Resource):
    def get(self, user_id, tracker_id):
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        return make_response(
            render_template("updatetracker.html", tracker=temp_tracker, user_id=user_id)
        )

    def post(self, user_id, tracker_id,id):
        temp_logs = Logs.query.filter(Logs.id == id).first()
        db.session.delete(temp_logs)
        new_log = Logs(
            On=str(request.form["date"]+" "+request.form["time"]), 
            tracker=tracker_id,
            value=request.form["note"],
            note=request.form["note"],
        )
        db.session.add(new_log)
        db.session.commit()
        return redirect(f"/{user_id}/{tracker_id}/trackerlogs")


api.add_resource(TrackerOperations, "/<int:user_id>/trackerlist/")
api.add_resource(TrackerUpdate, "/<int:user_id>/<int:tracker_id>/updatetracker/")
api.add_resource(TrackerDeletion, "/<int:user_id>/<int:tracker_id>/deletetracker/")
api.add_resource(NewTracker, "/<int:user_id>/addtracker/")
api.add_resource(UserLogin, "/")
api.add_resource(UserOperations, "/signup")
api.add_resource(AddTracker,"/<int:user_id>/<int:tracker_id>/addtracker/")
api.add_resource(TrackerLogs, "/<int:user_id>/<int:tracker_id>/trackerlogs/")
api.add_resource(AddLogs, "/<int:user_id>/<int:tracker_id>/addlogs/")
api.add_resource(DeleteLogs, "/<int:user_id>/<int:tracker_id>/<int:id>/deletelogs/")
api.add_resource(UpdateLogs, "/<int:user_id>/<int:tracker_id>/<int:id>/updatelogs/")
if __name__ == "__main__":
    app.run(debug=True)
    db.init_app(app)
