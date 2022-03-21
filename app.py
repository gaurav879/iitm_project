from importlib.resources import Resource
from sqlite3 import Timestamp
from flask import Flask, render_template, request, redirect, session, make_response
from matplotlib import pyplot as plt
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
    tracker_type = db.Column(db.String)
    settings = db.Column(db.String)
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
        return make_response(render_template("login.html"))

    def post(self):
        _username = request.form["username"]
        pw = request.form["_password"]

        temp_user = User.query.all()

        for i in temp_user:
            if _username == i.username and pw == i.pw:
                id = i.user_id
                return redirect(f"/{id}/trackerlist")
        return make_response(render_template("login.html",msg="Either username or password wrong"))  


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
            if _username == i.username:
                return "user already exist"
        db.session.add(new_user)
        db.session.commit()
        return make_response(render_template('login.html',msg="Account created"))


class TrackerOperations(Resource):
    def get(self, user_id):
        temp_user = User.query.all()
        for i in temp_user:
            if i.user_id == user_id:
                temp = i
                break
        temp_trackers = Tracker.query.filter(
            Tracker.tracker_user_id == temp.user_id
        ).all()
        temp_logs=[]
        for i in temp_trackers:
            templogs=Logs.query.filter(Logs.tracker==i.tracker_id).order_by(Logs.timestamp).all()
            if(templogs):
                temp_logs.append(templogs[-1])
        print(temp_logs)
        return make_response(
            render_template(
                "tracker_display.html",
                logs=temp_logs,
                data=temp_trackers,
                user=temp,
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
            tracker_type=request.form["type"],
            settings=request.form["settings"],
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
        temp_tracker.tracker_name=request.form["tracker_name"]
        temp_tracker.tracker_description=request.form["tracker_description"]
        temp_tracker.settings=request.form["settings"]
        db.session.commit()
        return redirect(f"/{user_id}/trackerlist")


# class AddTracker(Resource):
#     def get(self, user_id, tracker_id):
#         temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
#         temp_logs = Logs.query.filter(Logs.tracker == tracker_id).all()
#         return make_response(
#             render_template("updatetracker.html", logs=temp_logs,tracker_name=temp_tracker.tracker_name, user_id=user_id)
#         )


class TrackerLogs(Resource):
    def get(self, user_id, tracker_id):
        temp_user=User.query.filter(User.user_id==user_id).first()
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        value_list=[]
        logs=Logs.query.filter(Logs.tracker==tracker_id).order_by(Logs.timestamp).all()
        for i in logs:
            value_list.append(i.value)
        if(temp_tracker.tracker_type=="numerical" or temp_tracker.tracker_type=="boolean"):
            print("000")
            plt.hist(value_list)
            plt.ylabel("Frequency")
            plt.xlabel("Marks")
            plt.savefig("./static/histo.png")
        return make_response(
            render_template("trackerlogs.html", tracker=temp_tracker, user=temp_user,logs=logs,)
        )


class AddLogs(Resource):
    def get(self,user_id,tracker_id):
        temp_user=User.query.filter(User.user_id == user_id).first()
        
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        return make_response(
            render_template("addlogs.html", tracker=temp_tracker, user=temp_user)
        )

    def post(self,user_id,tracker_id):
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
    def get(self, user_id, tracker_id,id):
        temp_tracker = Tracker.query.filter(Tracker.tracker_id == tracker_id).first()
        temp_logs = Logs.query.filter(Logs.id == id).first()
        return make_response(
            render_template("updatelogs.html", tracker=temp_tracker, user_id=user_id,logs=temp_logs,time=temp_logs.timestamp.split(" ")[1])
        )

    def post(self, user_id, tracker_id,id):
        temp_logs = Logs.query.filter(Logs.id == id).first()
        temp_logs.timestamp=str(request.form["date"]+" "+request.form["time"])
        temp_logs.value=request.form["value"]
        temp_logs.note=request.form["note"]
        db.session.commit()
        return redirect(f"/{user_id}/{tracker_id}/trackerlogs")


api.add_resource(TrackerOperations, "/<int:user_id>/trackerlist/")
api.add_resource(TrackerUpdate, "/<int:user_id>/<int:tracker_id>/updatetracker/")
api.add_resource(TrackerDeletion, "/<int:user_id>/<int:tracker_id>/deletetracker/")
api.add_resource(NewTracker, "/<int:user_id>/addtracker/")
api.add_resource(UserLogin, "/")
api.add_resource(UserOperations, "/signup")
api.add_resource(TrackerLogs, "/<int:user_id>/<int:tracker_id>/trackerlogs/")
api.add_resource(AddLogs, "/<int:user_id>/<int:tracker_id>/addlogs/")
api.add_resource(DeleteLogs, "/<int:user_id>/<int:tracker_id>/<int:id>/deletelogs/")
api.add_resource(UpdateLogs, "/<int:user_id>/<int:tracker_id>/<int:id>/updatelogs/")
if __name__ == "__main__":
    app.run(debug=True)
    db.init_app(app)
