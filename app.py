from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# Config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bjj_gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Admin model
class Admin(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Member model
class Member(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    first_name   = db.Column(db.String(100), nullable=False)
    last_name    = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

# Create tables if they dont exist
with app.app_context():
    db.create_all()

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        admin = Admin.query.filter_by(username=data['username']).first()

        if admin and check_password_hash(admin.password, data['password']):
            login_user(admin)
            return redirect(url_for('read_members'))
        else:
            flash('invalid credentials')
            return redirect(url_for('login'))
    
    return render_template('login.html')


# Create member route
@app.route('/create_member', methods=['POST'])
@login_required
def create_member():
    data = request.json
    new_member = Member(
        first_name   = data['first_name'],
        last_name    = data['last_name'],
        email        = data['email'],
        phone_number = data['phone_number']
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'new member added!'}), 201

# Read members route
@app.route('/read_members', methods=['GET'])
@login_required
def read_members():
    members = Member.query.all()
    result = [
        {
            'id': member.id,
            'first_name'  : member.first_name,
            'last_name'   : member.last_name,
            'email'       : member.email,
            'phone_number': member.phone_number
        } for member in members
    ]
    return jsonify(result), 200

# Update member route
@app.route('/update_member/<int:id>', methods=["PUT"])
@login_required
def update_member(id):
    member = Member.query.get(id) # Fetch member by ID
    if not member:
        return jsonify({'message': 'Member not found'}), 404
    
    data = request.json
    member.first_name   = data.get('first_name', member.first_name)
    member.last_name    = data.get('last_name', member.last_name)
    member.email        = data.get('email', member.email)
    member.phone_number = data.get('phone_number', member.phone_number)

    db.session.commit()
    return jsonify({'message': 'Member updated succesfully!'}), 200

# Delete member route
@app.route('/delete_member/<int:id>', methods=['DELETE'])
@login_required
def delete_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'message': 'Member not found'}), 404
    
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted succesfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
