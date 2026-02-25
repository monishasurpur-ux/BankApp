from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import bcrypt
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration - Vercel compatible
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kodbank-secret-key-2024')

# Database configuration - supports both SQLite (local) and PostgreSQL (Vercel/Neon)
# For local development: uses SQLite
# For production (Vercel): uses PostgreSQL from DATABASE_URL or NEON_DB_URL

# Check for PostgreSQL connection string
database_url = os.environ.get('DATABASE_URL') or os.environ.get('NEON_DB_URL')

if database_url:
    # Use PostgreSQL (Neon or other PostgreSQL provider)
    # Fix PostgreSQL URL format for SQLAlchemy if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local development
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    db_path = os.path.join(instance_dir, 'kodbank.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'kodbank-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=10000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_userid = db.Column(db.String(50), nullable=False)
    to_userid = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['userid', 'email', 'phone', 'password', 'full_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} is required'}), 400
    
    if User.query.filter_by(userid=data['userid']).first():
        return jsonify({'success': False, 'message': 'UserID already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    new_user = User(
        userid=data['userid'],
        email=data['email'],
        phone=data['phone'],
        password=hashed.decode('utf-8'),
        full_name=data['full_name'],
        balance=10000.0
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Registration successful! Please login.'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('userid') or not data.get('password'):
        return jsonify({'success': False, 'message': 'UserID and password are required'}), 400
    
    user = User.query.filter_by(userid=data['userid']).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.userid)
    
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'token': access_token,
        'user': {
            'userid': user.userid,
            'full_name': user.full_name,
            'email': user.email,
            'balance': user.balance
        }
    }), 200

@app.route('/api/balance', methods=['GET'])
@jwt_required()
def get_balance():
    userid = get_jwt_identity()
    user = User.query.filter_by(userid=userid).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'balance': user.balance,
        'userid': user.userid,
        'full_name': user.full_name,
        'email': user.email
    }), 200

@app.route('/api/transfer', methods=['POST'])
@jwt_required()
def transfer():
    userid = get_jwt_identity()
    data = request.get_json()
    
    recipient_userid = data.get('to_userid')
    amount = data.get('amount')
    
    if not recipient_userid or not amount:
        return jsonify({'success': False, 'message': 'Recipient and amount are required'}), 400
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400
    
    sender = User.query.filter_by(userid=userid).first()
    if not sender:
        return jsonify({'success': False, 'message': 'Sender not found'}), 404
    
    if sender.balance < amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    recipient = User.query.filter_by(userid=recipient_userid).first()
    if not recipient:
        return jsonify({'success': False, 'message': 'Recipient not found'}), 404
    
    if sender.userid == recipient.userid:
        return jsonify({'success': False, 'message': 'Cannot transfer to yourself'}), 400
    
    sender.balance -= amount
    recipient.balance += amount
    
    transaction = Transaction(
        from_userid=sender.userid,
        to_userid=recipient.userid,
        amount=amount
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Successfully transferred {amount} to {recipient_userid}',
        'new_balance': sender.balance
    }), 200

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    userid = get_jwt_identity()
    
    transactions = Transaction.query.filter(
        (Transaction.from_userid == userid) | (Transaction.to_userid == userid)
    ).order_by(Transaction.timestamp.desc()).limit(10).all()
    
    transaction_list = []
    for t in transactions:
        transaction_list.append({
            'id': t.id,
            'from_userid': t.from_userid,
            'to_userid': t.to_userid,
            'amount': t.amount,
            'type': 'sent' if t.from_userid == userid else 'received',
            'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'transactions': transaction_list
    }), 200

# Serve frontend
@app.route('/')
def index():
    # Read and serve the HTML file - try multiple paths for Vercel compatibility
    possible_paths = [
        'templates/index.html',
        '../templates/index.html',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'index.html')
    ]
    
    for html_path in possible_paths:
        try:
            with open(html_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        except:
            continue
    
    return jsonify({'message': 'KodBank API is running'}), 200

# Vercel handler - Required for serverless deployment
app.debug = False
