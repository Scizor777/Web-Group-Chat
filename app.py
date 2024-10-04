from flask import Flask,render_template,request,redirect,url_for,session
from flask_socketio import join_room,leave_room,send,SocketIO
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
from string import ascii_uppercase


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SECRET_KEY"]="asddasdwdafwdafwfasdawg"
db_login = SQLAlchemy(app)
socketio = SocketIO(app)
class log_info(db_login.Model):
    sno = db_login.Column(db_login.Integer,primary_key=True)
    username =db_login.Column(db_login.String(200),nullable=False)
    password = db_login.Column(db_login.String(500),nullable=False)
    date_created = db_login.Column(db_login.DateTime,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.username}-{self.password}"
    def user(self) -> str:
        return f"{self.username}"
    def passw(self) -> str:
        return f"{self.password}"

rooms = {}
onlineUser = []

def unique_gen(data):
    while True:
        code = ""
        for _ in range(data):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

@app.route("/" , methods = ["POST", "GET"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form['username']
        password = str(request.form['password'])
        alluser = log_info.query.all()
        for user in alluser:
            if(username == user.user() and password == user.passw()):
                session['name'] = username 
                return redirect(url_for('room1'))
        else:
            return render_template('index.html',username=username,password=password,error="Invalid Credentials")
    return render_template('index.html')

@app.route("/room", methods=["POST","GET"])
def room1():
    name = session.get('name')
    print(name)
    if name is None :
        return render_template('index.html',error="Please enter Credentials")
    if request.method == "POST":
        code = request.form.get('code',False)
        create = request.form.get('create',False)
        join = request.form.get('sumbit',False)
        if join is not False:
            if code in rooms:
                session['room'] = code
                return redirect(url_for('chat'))
            else:
                return render_template('boiler.html',error="room is not present")
        elif create is not False:
            room = unique_gen(4)
            rooms[room] = {"members": 0, "messages": []}
            session['room'] = room
            return redirect(url_for('chat'))
    return render_template('boiler.html')

@app.route("/chat", methods=["POST","GET"])
def chat():
    room = session.get('room')
    name = session.get('name')
    if name in onlineUser:
        return render_template('index.html',error="user already online")
    if room is None or room not in rooms:
        return redirect(url_for('room1'))
    onlineUser.append(name)
    return render_template('chat.html',roomno=room,name=name)

@socketio.on('connect')
def connect(auth):
    name = session.get('name')
    room = session.get('room')
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    print(onlineUser)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    if name in onlineUser:
        onlineUser.remove(name)
    if name in onlineUser:
        onlineUser.remove(name)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

@socketio.on("message")
def message(data):
    room = session.get('room')
    content = {
        "name": session.get("name"),
        "message": data["msg"]
    }
    send(content,to=room)
    rooms[room]["messages"].append(content)
if __name__ == '__main__':
    socketio.run(app, debug=True)