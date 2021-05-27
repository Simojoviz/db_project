from flask import Flask
from flask import *

from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from sqlalchemy import create_engine

from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from model import *


app = Flask ( __name__ )

#engine = create_engine('sqlite:///database.db', echo=True)
# engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)
engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)


app.config ['SECRET_KEY'] = 'ubersecret'

Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users
Prenotation = Base.classes.prenotations
Shift = Base.classes.shifts

Session = sessionmaker(bind=engine)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    # costruttore di classe
    def __init__(self, id, email, psw, active=True):
        self.id = id
        self.email = email
        self.psw = psw
        self.active = active

def get_user_by_email(session, email):
    user = get_user(session, email = email)
    if user is not None:
        return User(user.id, user.email, user.pwd)

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = get_user(session, id = user_id)
    session.close()
    if user is not None:
        return User(user.id, user.email, user.pwd)

@app.route('/')
def home():
    session = Session()
    try:
        if current_user.is_authenticated:
            return redirect(url_for('private'))
        users = get_all_emails(session)

        session.commit()
        return render_template("home.html", users=users)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session = Session()
        try:
            userReq = request.form['user']
            passReq = request.form['pass']
            userIn = get_user(session, email = userReq)
            if(userIn is not None):
                if (passReq == userIn.pwd):
                    user = get_user_by_email(session, userReq)
                    login_user(user)
                    session.commit()
                    return redirect(url_for('private'))
                else:
                    session.commit()
                    return redirect(url_for('home'))
            else:
                session.commit()
                return redirect(url_for('home'))
        except:
            session.rollback()
            raise
        finally:
            session.close()


@app.route('/private')
@login_required
def private():
    session = Session()
    try:
        email = current_user.email
        user = get_user(session, email=email)
        prenotations = get_prenotation(session, user=user)
        s = []
        for p in prenotations:
            sh = get_shift(session, prenotation=p)
            s.append(to_string(shift=sh))
        resp = make_response(render_template("private.html", us = user.fullname, prenotations=s))
        
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))