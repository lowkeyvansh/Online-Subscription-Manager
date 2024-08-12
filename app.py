from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    subscriptions = db.relationship('Subscription', backref='owner', lazy=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    renewal_date = db.Column(db.DateTime, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        subscriptions = Subscription.query.filter_by(owner_id=current_user.id).all()
        return render_template('index.html', subscriptions=subscriptions)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/subscription/new', methods=['GET', 'POST'])
@login_required
def new_subscription():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        cost = request.form['cost']
        renewal_date = datetime.strptime(request.form['renewal_date'], '%Y-%m-%d')
        new_subscription = Subscription(name=name, category=category, cost=cost, renewal_date=renewal_date, owner_id=current_user.id)
        db.session.add(new_subscription)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_subscription.html')

@app.route('/subscription/<int:subscription_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    if request.method == 'POST':
        subscription.name = request.form['name']
        subscription.category = request.form['category']
        subscription.cost = request.form['cost']
        subscription.renewal_date = datetime.strptime(request.form['renewal_date'], '%Y-%m-%d')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_subscription.html', subscription=subscription)

@app.route('/subscription/<int:subscription_id>/delete', methods=['POST'])
@login_required
def delete_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    db.session.delete(subscription)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
