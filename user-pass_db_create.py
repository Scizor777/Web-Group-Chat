from app import db_login,app,log_info
name = ""   # add new name and passwd and run the program to add new user
passw = ""

with app.app_context():
    newuser = log_info(username=name,password=passw)
    db_login.session.add(newuser)
    db_login.session.commit()
