from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from urllib.parse import quote

app = Flask(__name__)
CORS(app)
app.secret_key = 'book_nook_secret_key'

# SQLite Configuration for user data and other app data
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_BINDS'] = {
    'contact_db': 'mysql://root:admin123@localhost/book_nook_db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# User model using default SQLite database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<User {self.name}>'

# Contact model using MySQL database
class ContactMessage(db.Model):
    __bind_key__ = 'contact_db'
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    source = db.Column(db.String(10), default='flask')

# Create database tables (run only once)
with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Create URL-encoded message for notification
            message = quote('Please log in to access this page.')
            return redirect(url_for('login', message=message, type='warning', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

# New status endpoint for Django integration
@app.route("/status")
def status():
    return jsonify({
        "status": "Flask server is running",
        "code": 200
    })

@app.route('/category/<category_name>')
def category(category_name):
    return render_template(f'{category_name}.html')

@app.route('/authors')
def authors():
    return render_template('author.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'signup':
            # Handle sign up
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists. Please use a different email.')
                return redirect(url_for('login'))
            
            # Create new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(name=name, email=email, password=hashed_password)
            
            try:
                db.session.add(new_user)
                db.session.commit()
                # After success, redirect with a message instead of flash
                message = quote('Account created successfully! Please sign in.')
                return redirect(url_for('login', message=message, type='success'))
            except Exception as e:
                db.session.rollback()
                message = quote(f'An error occurred: {str(e)}')
                return redirect(url_for('login', message=message, type='error'))
            
        elif action == 'signin':
            # Handle sign in
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['user_name'] = user.name
                
                # Redirect to the next parameter if it exists
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                
                # If no next parameter, show success message and redirect home
                message = quote('Logged in successfully!')
                return redirect(url_for('home', message=message, type='success'))
            else:
                message = quote('Invalid email or password. Please try again.')
                return redirect(url_for('login', message=message, type='error'))
    
    return render_template('loginpage1.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    message = quote('You have been logged out.')
    return redirect(url_for('login', message=message, type='success'))

@app.route('/cart')
@login_required
def cart():
    return render_template('finalcart.html')

@app.route('/payment')
@login_required
def payment():
    return render_template('payment.html')

@app.route('/checkout')
@login_required
def checkout():
    return render_template('Checkout Page.html')  

@app.route('/upi-payment')
@login_required
def upi_payment():
    return render_template('payupi.html')

@app.route('/credit-payment')
@login_required
def credit_payment():
    return render_template('paycred.html')

@app.route('/checkout-confirmation')
@login_required
def checkout_confirmation():
    return render_template('checkout-confirm.html')

@app.route('/allabout3')
def allabout3():
    return render_template('allabout3.html')


@app.route('/allabout4')
def allabout4():
    return render_template('allabout4.html')

@app.route('/allabout5')
def allabout5():
    return render_template('allabout5.html')

@app.route('/allbooks')
def allbooks():
    return render_template('allbooks.html')

@app.route('/allbook2')
def allbook2():
    return render_template('allbook2.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if name and email and message:
            try:
                new_contact = ContactMessage(
                    name=name,
                    email=email,
                    message=message,
                    source='flask'
                )
                db.session.add(new_contact)
                db.session.commit()
                flash('Thank you! Your message has been sent successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while sending your message. Please try again.', 'error')
        else:
            flash('Please fill in all the required fields.', 'error')
            
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# New route to handle adding to cart
@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        book_data = request.get_json()
        
        # Initialize cart in session if not exists
        if 'cart' not in session:
            session['cart'] = []
        
        # Add the book to cart
        session['cart'].append(book_data)
        session.modified = True
        
        # Return the current cart count
        return jsonify({
            'success': True,
            'message': 'Book added to cart!',
            'cart_count': len(session['cart']),
            'cart_total': sum(float(item['price'].replace('₹', '').strip()) for item in session['cart'])
        })

# New route to get cart data
@app.route('/get-cart-data', methods=['GET'])
def get_cart_data():
    if 'cart' not in session:
        session['cart'] = []
    
    return jsonify({
        'cart_items': session['cart'],
        'cart_count': len(session['cart']),
        'cart_total': sum(float(item['price'].replace('₹', '').strip()) for item in session['cart']) if session['cart'] else 0
    })

# New route to remove item from cart
@app.route('/remove-cart-item', methods=['POST'])
@login_required
def remove_cart_item():
    if request.method == 'POST':
        data = request.get_json()
        item_id = data.get('id')
        
        if 'cart' in session and item_id is not None:
            # Find the item in the cart by id and remove it
            session['cart'] = [item for item in session['cart'] if str(item.get('id')) != str(item_id)]
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': 'Item removed from cart',
                'cart_items': session['cart'],
                'cart_count': len(session['cart']),
                'cart_total': sum(float(item['price'].replace('₹', '').strip()) for item in session['cart']) if session['cart'] else 0
            })
        
        return jsonify({
            'success': False,
            'message': 'Item not found in cart'
        }), 404

# New route to update cart item quantity
@app.route('/update-cart-item', methods=['POST'])
@login_required
def update_cart_item():
    if request.method == 'POST':
        data = request.get_json()
        item_id = data.get('id')
        new_quantity = data.get('quantity')
        
        if 'cart' in session and item_id is not None and new_quantity is not None:
            for item in session['cart']:
                if str(item.get('id')) == str(item_id):
                    item['quantity'] = new_quantity
                    session.modified = True
                    break
            
            return jsonify({
                'success': True,
                'message': 'Cart updated successfully',
                'cart_items': session['cart'],
                'cart_count': len(session['cart']),
                'cart_total': sum(float(item['price'].replace('₹', '').strip()) * item.get('quantity', 1) for item in session['cart']) if session['cart'] else 0
            })
        
        return jsonify({
            'success': False,
            'message': 'Item not found in cart or invalid quantity'
        }), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)







