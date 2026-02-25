from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import bcrypt
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kodbank-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'kodbank-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database configuration - Use SQLite for Vercel serverless (no setup needed)
# Use /tmp which is writable in serverless functions
db_path = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'kodbank.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Database initialization: {e}")

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
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
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
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
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/balance', methods=['GET'])
@jwt_required()
def get_balance():
    try:
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
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/transfer', methods=['POST'])
@jwt_required()
def transfer():
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
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
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Serve frontend
@app.route('/')
def index():
    try:
        # Try multiple paths for the HTML file
        possible_paths = [
            'templates/index.html',
            '../templates/index.html',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'index.html'),
            os.path.join(os.getcwd(), 'templates', 'index.html')
        ]
        
        for html_path in possible_paths:
            try:
                if os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        return f.read(), 200, {'Content-Type': 'text/html'}
            except:
                continue
        
        return jsonify({
            'message': 'KodBank API is running',
            'status': 'ok',
            'database': 'sqlite'
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

app.debug = False
