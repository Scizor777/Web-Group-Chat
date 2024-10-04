from app import db_login,app,log_info
name = "diyansh"
passw = "80800"

with app.app_context():
    newuser = log_info(username=name,password=passw)
    db_login.session.add(newuser)
    db_login.session.commit()
