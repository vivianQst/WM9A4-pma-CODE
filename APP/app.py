from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# for secure session management
app.secret_key = 'supersecretkey' 



# Database 
#Reference:https://www.freecodecamp.org/news/connect-python-with-sql/
# Configuring the database(use SQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  

# SQLite database path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialising SQLAlchemy objects
db = SQLAlchemy(app)

# Creating a user database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    school_id = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # password hash processing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialise the database (used when running the application for the first time)
with app.app_context():
    db.create_all()



#Web Page Design
# Home page routing 
@app.route('/')
def home():
    return render_template('home.html')



# Login page routing
# reference: https://www.makeuseof.com/python-login-page-simple-build/
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

          # Query users
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


# Registration page routing
# reference: https://www.javatpoint.com/simple-registration-form-using-tkinter-in-python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        school_id = request.form['school_id']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Form validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another one.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered. Please choose another one.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
        else:
           # Create new users
            new_user = User(username=username, school_id=school_id, email=email)
            new_user.set_password(password)  # Encrypted storage passwords
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


# Registration routes (login out)
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

from datetime import datetime





# Booking page routing
#reference:https://github.com/OneScreenfulOfPython/booking-system
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user' not in session:
        flash('You need to log in to make a booking.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        facility = request.form['facility']
        date = request.form['date']
        time = request.form['time']
        message = request.form['message']

        # Get the current logged in user
        user = User.query.filter_by(username=session['user']).first()

        # Create new bookings
        new_booking = booking(
            user_id=user.id,
            facility=facility,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            time=datetime.strptime(time, '%H:%M').time(),
            message=message
        )

        db.session.add(new_booking)
        db.session.commit()

        flash('Booking successful!', 'success')
        return redirect(url_for('home'))

    return render_template('booking.html')



if __name__ == '__main__':
    app.run(debug=True)


