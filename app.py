import datetime
import json
import os
from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  
app.secret_key = os.environ.get('SECRET_KEY', '1234')

# Database Configuration
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='restaurant_management'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Home page route
@app.route('/')
def home():
    return render_template('signup.html')

# Authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    # POST request handling
    if request.is_json:
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = generate_password_hash(data['password'])
    else:
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

    try:
        db = get_db_connection()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
            
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO user (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()
        # Get the user ID to store in session
        user_id = cursor.lastrowid
        session['user_id'] = user_id
        session['username'] = username
        session['cart_owner'] = user_id
        # Set flag to clear any existing localStorage cart from anonymous browsing
        session['clear_local_cart'] = True
        return redirect(url_for('index'))
    except mysql.connector.Error as err:
        print(f"Database error in signup: {err}")
        if 'db' in locals() and db:
            db.rollback()
        return jsonify({'message': str(err)}), 400
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    try:
        db = get_db_connection()
        if not db:
            flash("Database connection failed")
            return render_template('login.html')
            
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, password, username, is_admin
            FROM user
            WHERE username = %s
            LIMIT 1
        """, (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            current_user_id = user['user_id']
            
            # Check if there's an existing cart that belongs to a different user
            old_cart_owner = session.get('cart_owner')
            existing_cart = session.get('cart_data') if old_cart_owner == current_user_id else None
            
            # Clear the entire session to remove any previous user's data
            session.clear()
            
            # Set new user session data
            session['user_id'] = current_user_id
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)  # Store admin status
            session['cart_owner'] = current_user_id
            
            if existing_cart:
                session['cart_data'] = existing_cart
                session['clear_local_cart'] = False
            else:
                session['clear_local_cart'] = True
            
            return redirect(url_for('index'))
        else:
            flash("Wrong username or password", "error")
            return render_template('login.html')
    except mysql.connector.Error as err:
        print(f"Database error in login: {err}")
        flash(f"Error: {str(err)}")
        return render_template('login.html')
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# Profile management
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Update profile
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        try:
            db = get_db_connection()
            if not db:
                flash('Database connection failed')
                return redirect(url_for('profile'))
            
            cursor = db.cursor()
            cursor.execute(
                "UPDATE user SET full_name = %s, phone = %s, address = %s WHERE user_id = %s",
                (full_name, phone, address, user_id)
            )
            db.commit()
            flash('Profile updated successfully!')
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            flash('Error updating profile')
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()
        
        return redirect(url_for('profile'))
    
    # GET request - fetch user profile
    try:
        db = get_db_connection()
        if not db:
            flash('Database connection failed')
            return render_template('profile.html', user={})
        
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, email, full_name, phone, address FROM user WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        return render_template('profile.html', user=user)
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('Error loading profile')
        return render_template('profile.html', user={})
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

# Main pages
@app.route('/index')
def index():
    # Pop the flag so it only triggers once after login/signup
    clear_local = session.pop('clear_local_cart', False)
    return render_template('index.html', clear_local_cart=clear_local)

# Menu Routes
@app.route('/menu')
def menu():
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if not db:
            return render_template('menu.html', categories=[], error="Database connection failed")
            
        cursor = db.cursor(dictionary=True)
        
        # Get all categories with item counts
        cursor.execute("""
            SELECT c.*, COUNT(i.item_id) as item_count 
            FROM categories c 
            LEFT JOIN Items i ON c.category_id = i.category_id 
            GROUP BY c.category_id 
            ORDER BY c.is_custom, c.category_name
        """)
        categories = cursor.fetchall()
        
        # Add icon mapping for categories
        icon_map = {
            'Veg': 'leaf',
            'Non-Veg': 'drumstick-bite',
            'Snacks': 'cookie-bite',
            'beverages': 'mug-hot'
        }
        
        for category in categories:
            # Set icon based on category
            cat_name = category['category_name']
            if cat_name in icon_map:
                category['icon'] = icon_map[cat_name]
            else:
                category['icon'] = 'utensils'  # default icon
        
        return render_template('menu.html', categories=categories)
    except mysql.connector.Error as err:
        print(f"Database error in menu: {err}")
        return render_template('menu.html', categories=[], error=str(err))
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def _normalize_category_key(value: str) -> str:
    """Collapse a category label to a lowercase alphanumeric slug for comparisons."""
    if not value:
        return ''
    return ''.join(ch for ch in value.lower() if ch.isalnum())


# Category specific routes
def render_category_page(category_name):
    """Render a category page with live menu data from the Items table."""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM categories WHERE category_name = %s", (category_name,))
        category = cursor.fetchone()
        if not category:
            flash("Category not found")
            return redirect(url_for('menu'))

        # Fetch items by category_id using the FK relationship
        cursor.execute("""
            SELECT i.* FROM Items i
            WHERE i.category_id = %s
            ORDER BY i.item_name
        """, (category['category_id'],))
        items = cursor.fetchall()

        clear_local = session.pop('clear_local_cart', False)
        return render_template('dynamic_category.html',
                               category=category,
                               items=items,
                               clear_local_cart=clear_local)
    except mysql.connector.Error as err:
        flash(f"Database error: {err}")
        return redirect(url_for('menu'))
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

@app.route('/veg')
def veg():
    return render_category_page('Veg')

@app.route('/nonveg')
def nonveg():
    return render_category_page('Non-Veg')

@app.route('/snacks')
def snacks():
    return render_category_page('Snacks')

@app.route('/beverages')
def beverages():
    return render_category_page('beverages')

# Cart routes
@app.route('/cart')
def cart():
    clear_local = session.pop('clear_local_cart', False)
    server_cart = None
    cart_snapshot = session.get('cart_data')
    if cart_snapshot:
        try:
            server_cart = json.loads(cart_snapshot)
        except (json.JSONDecodeError, TypeError):
            server_cart = None
    return render_template("cart.html", clear_local_cart=clear_local, server_cart=server_cart)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        
        # Get item details from database
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Items WHERE item_id = %s", (item_id,))  # Using 'Items' with capital I
        item = cursor.fetchone()
        
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        
        # Initialize cart if not exists
        if 'cart_data' not in session:
            session['cart_data'] = json.dumps({"items": {}})
            
        # Parse existing cart
        cart = json.loads(session['cart_data'])
        
        # Add/update item in cart
        if str(item_id) in cart['items']:
            cart['items'][str(item_id)]['quantity'] += 1
        else:
            cart['items'][str(item_id)] = {
                'id': item_id,
                'name': item['item_name'],
                'price': float(item['price']),
                'category': item['category'],
                'quantity': 1
            }
            
        # Save updated cart to session
        session['cart_data'] = json.dumps(cart)
        
        return jsonify({
            'success': True, 
            'message': f"{item['item_name']} added to cart",
            'cart': cart
        })
        
    except mysql.connector.Error as err:
        print(f"Database error in add-to-cart: {err}")
        return jsonify({'success': False, 'message': f'Database error: {str(err)}'}), 500
    except Exception as e:
        print(f"General error in add-to-cart: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/update-cart', methods=['POST'])
def update_cart():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 0))
        
        # Parse existing cart, initialize if missing so we can resync from client state
        if 'cart_data' not in session:
            session['cart_data'] = json.dumps({"items": {}})
        cart = json.loads(session['cart_data'])
        
        item_key = str(item_id)
        if quantity > 0 and item_key not in cart['items']:
            # create entry so quantity sync can succeed even if server cart missed earlier additions
            conn = get_db_connection()
            item_row = None
            try:
                if conn:
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM Items WHERE item_id = %s", (item_id,))
                    item_row = cur.fetchone()
            finally:
                if 'cur' in locals():
                    cur.close()
                if conn:
                    conn.close()

            if not item_row:
                return jsonify({'success': False, 'message': 'Item not found'}), 404

            cart['items'][item_key] = {
                'id': item_id,
                'name': item_row['item_name'],
                'price': float(item_row['price']),
                'category': item_row['category'],
                'quantity': 0
            }
        
        if item_key in cart['items']:
            if quantity > 0:
                cart['items'][item_key]['quantity'] = quantity
            else:
                del cart['items'][item_key]
                
            session['cart_data'] = json.dumps(cart)
            return jsonify({
                'success': True,
                'message': 'Cart updated',
                'cart': cart
            })
        else:
            return jsonify({'success': False, 'message': 'Item not found in cart'}), 404
            
    except Exception as e:
        print(f"Error in update-cart: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    session.pop('cart_data', None)
    return redirect(url_for('cart'))

# Checkout process
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Fetch user profile data for auto-fill
    user_profile = {}
    if 'user_id' in session:
        try:
            db = get_db_connection()
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute(
                    "SELECT full_name, phone, address, email FROM user WHERE user_id = %s",
                    (session['user_id'],)
                )
                user_profile = cursor.fetchone() or {}
                cursor.close()
                db.close()
        except mysql.connector.Error as err:
            print(f"Error fetching user profile: {err}")
    
    if request.method == 'POST':
        # Check if this is an order placement request (has required order fields)
        if request.form.get('customer_name') and request.form.get('cart'):
            # This is an order placement, not just saving cart data
            db = None
            cursor = None
            try:
                # Get customer details from the form
                name = request.form.get('customer_name')
                address = request.form.get('customer_address')
                phone_no = request.form.get('customer_phone')
                email = request.form.get('customer_email')
                delivery_option = request.form.get('delivery_option', 'Delivery')
                
                # Check if user is logged in
                if 'user_id' not in session:
                    return jsonify({'success': False, 'message': 'Please login to continue'})
                
                # Update user profile if logged in (for future auto-fill)
                user_id = session['user_id']
                if name and phone_no and address:
                    try:
                        db = get_db_connection()
                        if db:
                            cursor = db.cursor()
                            cursor.execute(
                                "UPDATE user SET full_name = %s, phone = %s, address = %s WHERE user_id = %s",
                                (name, phone_no, address, user_id)
                            )
                            db.commit()
                            cursor.close()
                            db.close()
                    except mysql.connector.Error as e:
                        print(f"Error updating user profile: {e}")
                
                # Get cart data from form
                cart_data = request.form.get('cart')
                if not cart_data:
                    return jsonify({'success': False, 'message': 'No cart data found'})
                    
                # Try to parse cart data
                try:
                    cart = json.loads(cart_data)
                    print(f"DEBUG: Cart data received: {cart}")
                except Exception as e:
                    print(f"Error parsing cart data: {e}")
                    return jsonify({'success': False, 'message': 'Invalid cart data'})
                
                # Connect to database
                db = get_db_connection()
                if not db:
                    return jsonify({'success': False, 'message': 'Database connection failed'})
                    
                cursor = db.cursor()
                
                # 1. Insert or update customer details
                # First, check if customer with this email already exists
                cursor.execute(
                    "SELECT customer_id FROM customer WHERE email = %s AND user_id = %s",
                    (email, user_id)
                )
                existing_customer = cursor.fetchone()
                
                if existing_customer:
                    # Update existing customer
                    customer_id = existing_customer[0]
                    cursor.execute(
                        "UPDATE customer SET name = %s, address = %s, phone_no = %s, delivery_option = %s WHERE customer_id = %s",
                        (name, address, phone_no, delivery_option, customer_id)
                    )
                else:
                    # Insert new customer
                    cursor.execute(
                        "INSERT INTO customer (name, address, phone_no, email, delivery_option, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, address, phone_no, email, delivery_option, user_id)
                    )
                    customer_id = cursor.lastrowid
                
                # Store customer details in session for the confirmation page
                session['customer_data'] = {
                    'customer_id': customer_id,
                    'name': name,
                    'address': address, 
                    'phone_no': phone_no,
                    'email': email,
                    'delivery_option': delivery_option
                }
                
                # Calculate total amount from cart
                total_amount = 0
                # Cart structure is {itemId: {name, price, quantity}} directly
                items = cart if isinstance(cart, dict) else cart.get('items', {})
                print(f"DEBUG: Cart items: {items}")
                for item_id, item_data in items.items():
                    if item_data and int(item_data.get('quantity', 0)) > 0:
                        item_price = float(item_data.get('price', 0))
                        item_quantity = int(item_data.get('quantity', 0))
                        item_subtotal = item_price * item_quantity
                        total_amount += item_subtotal
                        print(f"DEBUG: Item {item_id}: price={item_price}, qty={item_quantity}, subtotal={item_subtotal}")
                
                print(f"DEBUG: Total amount calculated: {total_amount}")
                
                # 2. Insert into orders table
                username = session.get('username', name)
                
                cursor.execute(
                    "INSERT INTO orders (user_id, bill_amt, username) VALUES (%s, %s, %s)",
                    (user_id, total_amount, username)
                )
                new_order_id = cursor.lastrowid
                print(f"DEBUG: Order inserted with ID {new_order_id}, bill_amt: {total_amount}")
                
                # 3. Insert each item into order_details table
                for item_id, item_data in items.items():
                    if item_data and int(item_data.get('quantity', 0)) > 0:
                        item_quantity = int(item_data.get('quantity', 0))
                        item_price = float(item_data.get('price', 0))
                        item_total = item_price * item_quantity
                        
                        cursor.execute(
                            "INSERT INTO order_details (order_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                            (new_order_id, item_id, item_quantity, item_total)
                        )
                
                # Commit the transaction
                db.commit()
                
                # Clear cart data from session after successful order
                session.pop('cart_data', None)
                
                return jsonify({'success': True, 'order_id': new_order_id, 'message': 'Order placed successfully'})
                
            except mysql.connector.Error as err:
                print(f"MySQL Error in checkout: {str(err)}")
                if db:
                    db.rollback()
                return jsonify({'success': False, 'message': f'Database Error: {str(err)}'})
            except Exception as e:
                print(f"General Error in checkout: {str(e)}")
                if db:
                    db.rollback()
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
            finally:
                if cursor:
                    cursor.close()
                if db and db.is_connected():
                    db.close()
        else:
            # Save cart data in session for later order processing
            cart_data = request.form.get('cart_data')
            if cart_data:
                session['cart_data'] = cart_data
            return render_template("checkout.html", cart_data=cart_data, user_profile=user_profile)
    
    # In case of GET request, use cart data from session if available
    cart_data = session.get('cart_data')
    return render_template("checkout.html", cart_data=cart_data, user_profile=user_profile)


@app.route('/submit-checkout', methods=['POST'])
def submit_checkout():
    db = None
    cursor = None
    try:
        # Get customer details from the form
        name = request.form.get('name')
        address = request.form.get('address')
        phone_no = request.form.get('phone_no')
        email = request.form.get('email')
        delivery_option = request.form.get('delivery_option', 'Delivery')
        
        # Update user profile if logged in (for future auto-fill)
        if 'user_id' in session and name and phone_no and address:
            try:
                cursor.execute(
                    "UPDATE user SET full_name = %s, phone = %s, address = %s WHERE user_id = %s",
                    (name, phone_no, address, session['user_id'])
                )
            except mysql.connector.Error as e:
                print(f"Error updating user profile: {e}")
        
        # Get cart data from session
        cart_data = session.get('cart_data')
        if not cart_data:
            flash("No cart data found")
            return redirect(url_for('cart'))
            
        # Try to parse cart data
        try:
            cart = json.loads(cart_data)
        except Exception as e:
            print(f"Error parsing cart data: {e}")
            flash("Invalid cart data")
            return redirect(url_for('cart'))
            
        # Get user_id from session if logged in
        user_id = session.get('user_id')
        
        # Connect to database
        db = get_db_connection()
        if not db:
            flash("Database connection failed")
            return redirect(url_for('checkout'))
            
        cursor = db.cursor()
        
        # 1. Check if customer exists and insert/update accordingly
        cursor.execute(
            "SELECT customer_id FROM customer WHERE email = %s",
            (email,)
        )
        existing_customer = cursor.fetchone()
        
        if existing_customer:
            # Update existing customer
            customer_id = existing_customer[0]
            cursor.execute(
                "UPDATE customer SET name = %s, address = %s, phone_no = %s, delivery_option = %s WHERE customer_id = %s",
                (name, address, phone_no, delivery_option, customer_id)
            )
        else:
            # Insert new customer
            cursor.execute(
                "INSERT INTO customer (name, address, phone_no, email, delivery_option, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, address, phone_no, email, delivery_option, user_id)
            )
            customer_id = cursor.lastrowid
        
        # Store customer details in session for the confirmation page
        session['customer_data'] = {
            'customer_id': customer_id,
            'name': name,
            'address': address, 
            'phone_no': phone_no,
            'email': email,
            'delivery_option': delivery_option
        }
        
        # Calculate total amount from cart
        total_amount = 0
        items = cart.get('items', {})
        for item_id, item_data in items.items():
            if item_data and int(item_data.get('quantity', 0)) > 0:
                total_amount += float(item_data.get('price', 0)) * int(item_data.get('quantity', 0))
        
        # 2. Insert into orders table
        # Check if username is needed or name should be used
        username = session.get('username', name)  # Fallback to name if username not in session
        
        cursor.execute(
            "INSERT INTO orders (user_id, bill_amt, username) VALUES (%s, %s, %s)",
            (user_id, total_amount, username)
        )
        # Get the order_id of the newly inserted order
        new_order_id = cursor.lastrowid
        
        # 3. Insert each item into order_details table
        for item_id, item_data in items.items():
            if item_data and int(item_data.get('quantity', 0)) > 0:
                item_quantity = int(item_data.get('quantity', 0))
                item_price = float(item_data.get('price', 0))
                item_total = item_price * item_quantity
                
                cursor.execute(
                    "INSERT INTO order_details (order_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                    (new_order_id, item_id, item_quantity, item_total)
                )
        
        # Commit the transaction
        db.commit()
        
        # Clear cart data from session after successful order
        session.pop('cart_data', None)
        
        # Redirect to confirmation page
        return redirect(url_for('order_confirmation', orderId=new_order_id))
        
    except mysql.connector.Error as err:
        print(f"MySQL Error in submit-checkout: {str(err)}")
        if db:
            db.rollback()
        flash(f"Database Error: {str(err)}")
        return redirect(url_for('checkout'))
    except Exception as e:
        print(f"General Error in submit-checkout: {str(e)}")
        if db:
            db.rollback()
        flash(f"Error: {str(e)}")
        return redirect(url_for('checkout'))
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()
@app.route('/place-order', methods=['POST'])
def place_order():
    print("===== PLACE ORDER ROUTE CALLED =====")
    print(f"Request method: {request.method}")
    print(f"Request Content-Type: {request.headers.get('Content-Type', 'Not provided')}")
    
    try:
        # Try to get data and handle potential parsing errors
        try:
            if request.is_json:
                data = request.get_json(force=True)  # force=True tries to parse JSON even if Content-Type is incorrect
                print("Processing JSON data")
            else:
                data = request.form.to_dict()
                print("Processing form data")
        except Exception as json_error:
            print(f"Data parsing error: {str(json_error)}")
            print(f"Request data: {request.data}")
            return jsonify({'success': False, 'error': f"Failed to parse request data: {str(json_error)}"})
        
        print(f"Received data: {data}")
        
        # Extract customer details
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        address = data.get('address')
        delivery_option = data.get('delivery_option', 'standard')
        
        print(f"Customer details - Name: {name}, Phone: {phone}, Email: {email}")
        
        # Get user_id from session if logged in
        user_id = session.get('user_id')
        print(f"User ID from session: {user_id}")
        
        # Connect to database
        print("Connecting to database...")
        db = get_db_connection()
        if not db:
            print("Database connection failed")
            return jsonify({'success': False, 'error': 'Database connection failed'})
        
        print("Database connected, creating cursor")
        cursor = db.cursor()
        
        try:
            # Start transaction
            db.start_transaction()
            
            # 1. Check if customer exists and insert/update accordingly
            print("Checking for existing customer")
            cursor.execute(
                "SELECT customer_id FROM customer WHERE email = %s",
                (email,)
            )
            existing_customer = cursor.fetchone()
            
            if existing_customer:
                # Update existing customer
                customer_id = existing_customer[0]
                print(f"Updating existing customer ID: {customer_id}")
                cursor.execute(
                    "UPDATE customer SET name = %s, address = %s, phone_no = %s, delivery_option = %s WHERE customer_id = %s",
                    (name, address, phone, delivery_option, customer_id)
                )
            else:
                # Insert new customer
                print("Inserting new customer")
                cursor.execute(
                    "INSERT INTO customer (name, address, phone_no, email, delivery_option, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, address, phone, email, delivery_option, user_id)
                )
                customer_id = cursor.lastrowid
                print(f"Customer ID created: {customer_id}")
            
            # Calculate total amount
            subtotal = data.get('subtotal', 0)
            if isinstance(subtotal, str) and subtotal.startswith('₹'):
                subtotal = subtotal[1:]  # Remove rupee symbol
            subtotal = float(subtotal) if subtotal else 0
            
            delivery_fee = data.get('delivery_fee', 0)
            if isinstance(delivery_fee, str) and delivery_fee.startswith('₹'):
                delivery_fee = delivery_fee[1:]  # Remove rupee symbol
            delivery_fee = float(delivery_fee) if delivery_fee else 0
            
            total_amount = data.get('total_amount', 0)
            if isinstance(total_amount, str) and total_amount.startswith('₹'):
                total_amount = total_amount[1:]  # Remove rupee symbol
            total_amount = float(total_amount) if total_amount else 0
            
            print(f"Calculated amounts - Subtotal: {subtotal}, Delivery: {delivery_fee}, Total: {total_amount}")
            
            # 2. Insert into orders table
            print("Creating order record")
            cursor.execute(
                "INSERT INTO orders (user_id, bill_amt, username) VALUES (%s, %s, %s)",
                (user_id, total_amount, name)
            )
            new_order_id = cursor.lastrowid
            print(f"Order ID created: {new_order_id}")
            
            # 3. Insert each item into order_details table
            items = data.get('items', {})
            print(f"Processing {len(items)} items")
            
            for item_id, item_data in items.items():
                if item_data and item_data.get('quantity', 0) > 0:
                    item_quantity = item_data.get('quantity', 0)
                    item_price = item_data.get('price', 0)
                    item_total = item_price * item_quantity
                    
                    print(f"Adding item: ID {item_id}, Quantity: {item_quantity}, Price: {item_price}")
                    cursor.execute(
                        "INSERT INTO order_details (order_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                        (new_order_id, item_id, item_quantity, item_total)
                    )
            
            # Commit the transaction
            print("Committing transaction")
            db.commit()
            
            # Generate a proper order ID format to return to the client
            formatted_order_id = f"{new_order_id}"
            print(f"Order successfully created: {formatted_order_id}")
            
            return jsonify({
                'success': True,
                'orderId': formatted_order_id,
                'message': 'Order placed successfully'
            })
            
        except mysql.connector.Error as err:
            print(f"MySQL Error in place-order: {str(err)}")
            db.rollback()
            return jsonify({'success': False, 'error': f"Database Error: {str(err)}"})
            
    except mysql.connector.Error as err:
        print(f"MySQL Error in place-order: {str(err)}")
        if 'db' in locals() and db and hasattr(db, 'rollback'):
            db.rollback()
        return jsonify({'success': False, 'error': f"Database Error: {str(err)}"})
        
    except Exception as e:
        print(f"General Error in place-order: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'db' in locals() and db and hasattr(db, 'rollback'):
            db.rollback()
        return jsonify({'success': False, 'error': f"Error: {str(e)}"})
        
    finally:
        print("Cleaning up database resources")
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db and hasattr(db, 'close') and hasattr(db, 'is_connected') and db.is_connected():
            db.close()
            print("Database connection closed")

@app.route('/order-confirmation')
def order_confirmation():
    try:
        # Get order ID from query parameters
        order_id = request.args.get('orderId')
        
        if not order_id:
            return "Order ID not provided", 400
            
        # Get customer data from session
        customer_data = session.get('customer_data', {})
        
        # Get order details from database
        db = get_db_connection()
        if not db:
            return render_template('order_confirmation.html', 
                                  order_id=order_id,
                                  error="Database connection failed")
            
        cursor = db.cursor(dictionary=True)
        
        # Try to find the order in the database
        # If the order_id has a format like "ORD-123", we need to handle that
        numeric_id = order_id
        if order_id and order_id.startswith('ORD-'):
            try:
                numeric_id = order_id[4:]  # Extract the part after "ORD-"
            except:
                pass
        
        try:
            # Try to convert to int if it's numeric
            numeric_id = int(numeric_id)
        except:
            # If not numeric, just use as is
            pass
            
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (numeric_id,))
        order = cursor.fetchone()
        
        # If order found, get items
        items = []
        if order:
            cursor.execute("""
                SELECT od.*, i.item_name, c.category_name as category
                FROM order_details od
                JOIN Items i ON od.item_id = i.item_id
                LEFT JOIN categories c ON i.category_id = c.category_id
                WHERE od.order_id = %s
            """, (order['order_id'],))
            items = cursor.fetchall()
            
            # Convert Decimal values to float for JSON serialization
            for item in items:
                if 'total_price' in item and hasattr(item['total_price'], 'to_eng_string'):
                    item['total_price'] = float(item['total_price'])
                    
            # Store the order data to make it available to the template's JavaScript
            order_data = {
                'total_amount': float(order['bill_amt']) if 'bill_amt' in order else 0,
                'delivery_option': customer_data.get('delivery_option', 'standard'),
                'payment_method': 'Cash on Delivery'  # Default or get from order if available
            }
            session['last_order_data'] = json.dumps(order_data)
        
        return render_template('order-confirmation.html', order_id=order_id)
                              
    except mysql.connector.Error as err:
        print(f"Database error in order-confirmation: {err}")
        return render_template('order-confirmation.html', 
                              order_id=order_id if 'order_id' in locals() else 'Unknown',
                              error=str(err))
    except Exception as e:
        print(f"General error in order-confirmation: {e}")
        return render_template('order-confirmation.html', 
                              order_id=order_id if 'order_id' in locals() else 'Unknown',
                              error=str(e))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

# Admin Dashboard Route
@app.route('/admin-dashboard')
def admin_dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("Please login to access the admin dashboard")
        return redirect(url_for('login_page'))
    
    # Check if user is admin
    if not session.get('is_admin', False):
        flash("Access Denied: Admin privileges required")
        return redirect(url_for('index'))
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        if not db:
            flash("Database connection failed")
            return redirect(url_for('index'))
        
        cursor = db.cursor(dictionary=True)
        
        # 1. Total Revenue
        cursor.execute("SELECT COALESCE(SUM(bill_amt), 0) as total_revenue FROM orders")
        total_revenue = cursor.fetchone()['total_revenue']
        
        # 2. Total Orders
        cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
        total_orders = cursor.fetchone()['total_orders']
        
        # 3. Total Customers
        cursor.execute("SELECT COUNT(DISTINCT user_id) as total_customers FROM orders WHERE user_id IS NOT NULL")
        total_customers = cursor.fetchone()['total_customers']
        
        # 4. Average Order Value
        cursor.execute("SELECT COALESCE(AVG(bill_amt), 0) as avg_order_value FROM orders WHERE bill_amt > 0")
        avg_order_value = cursor.fetchone()['avg_order_value']
        
        # 5. Top 10 Selling Items
        cursor.execute("""
            SELECT i.item_name, c.category_name as category, i.price,
                   COUNT(od.item_id) as order_count,
                   SUM(od.quantity) as total_quantity,
                   SUM(od.total_price) as total_revenue
            FROM order_details od
            JOIN Items i ON od.item_id = i.item_id
            LEFT JOIN categories c ON i.category_id = c.category_id
            GROUP BY od.item_id, i.item_name, c.category_name, i.price
            ORDER BY total_quantity DESC
            LIMIT 10
        """)
        top_items = cursor.fetchall()
        
        # 6. Revenue by Category
        cursor.execute("""
            SELECT c.category_name as category,
                   COUNT(od.item_id) as item_count,
                   SUM(od.total_price) as category_revenue
            FROM order_details od
            JOIN Items i ON od.item_id = i.item_id
            LEFT JOIN categories c ON i.category_id = c.category_id
            GROUP BY c.category_name
            ORDER BY category_revenue DESC
        """)
        category_revenue = cursor.fetchall()
        
        # 7. Recent Orders
        cursor.execute("""
            SELECT o.order_id, o.username, o.bill_amt, o.order_date,
                   c.name as customer_name, c.delivery_option
            FROM orders o
            LEFT JOIN customer c ON o.user_id = c.user_id
            ORDER BY o.order_date DESC
            LIMIT 10
        """)
        recent_orders = cursor.fetchall()
        
        # 8. Daily Revenue (Last 7 Days)
        cursor.execute("""
            SELECT DATE(order_date) as order_day,
                   COUNT(*) as order_count,
                   SUM(bill_amt) as daily_revenue
            FROM orders
            WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(order_date)
            ORDER BY order_day DESC
        """)
        daily_revenue = cursor.fetchall()
        
        # 9. Orders by Delivery Type
        cursor.execute("""
            SELECT c.delivery_option, COUNT(o.order_id) as order_count
            FROM orders o
            LEFT JOIN customer c ON o.user_id = c.user_id
            WHERE c.delivery_option IS NOT NULL
            GROUP BY c.delivery_option
        """)
        delivery_stats = cursor.fetchall()
        
        # 10. Monthly Revenue (Current Year)
        cursor.execute("""
            SELECT MONTH(order_date) as month,
                   MONTHNAME(order_date) as month_name,
                   COUNT(*) as order_count,
                   SUM(bill_amt) as monthly_revenue
            FROM orders
            WHERE YEAR(order_date) = YEAR(CURDATE())
            GROUP BY MONTH(order_date), MONTHNAME(order_date)
            ORDER BY month
        """)
        monthly_revenue = cursor.fetchall()
        
        return render_template('admin_dashboard.html',
                             total_revenue=total_revenue,
                             total_orders=total_orders,
                             total_customers=total_customers,
                             avg_order_value=avg_order_value,
                             top_items=top_items,
                             category_revenue=category_revenue,
                             recent_orders=recent_orders,
                             daily_revenue=daily_revenue,
                             delivery_stats=delivery_stats,
                             monthly_revenue=monthly_revenue)
        
    except mysql.connector.Error as err:
        print(f"Database error in admin dashboard: {err}")
        flash(f"Database error: {err}")
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in admin dashboard: {e}")
        flash(f"Error loading dashboard: {e}")
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# Admin Menu Management Routes
@app.route('/admin-menu-management')
def admin_menu_management():
    # Check if user is logged in and is admin
    if 'user_id' not in session:
        flash("Please login to access this page")
        return redirect(url_for('login_page'))
    
    if not session.get('is_admin', False):
        flash("Access Denied: Admin privileges required")
        return redirect(url_for('index'))
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        if not db:
            flash("Database connection failed")
            return redirect(url_for('admin_dashboard'))
        
        cursor = db.cursor(dictionary=True)
        
        # Get all categories with item counts
        cursor.execute("""
            SELECT c.*, COUNT(i.item_id) as item_count 
            FROM categories c 
            LEFT JOIN Items i ON c.category_id = i.category_id 
            GROUP BY c.category_id 
            ORDER BY c.is_custom, c.category_name
        """)
        categories = cursor.fetchall()
        
        # Get all items with category names
        cursor.execute("""
            SELECT i.*, c.category_name as category 
            FROM Items i
            LEFT JOIN categories c ON i.category_id = c.category_id
            ORDER BY c.category_name, i.item_name
        """)
        items = cursor.fetchall()
        
        # Get stats
        cursor.execute("SELECT COUNT(*) as total_categories FROM categories")
        total_categories_result = cursor.fetchone()
        total_categories = total_categories_result['total_categories'] if total_categories_result else 0
        
        cursor.execute("SELECT COUNT(*) as total_items FROM Items")
        total_items_result = cursor.fetchone()
        total_items = total_items_result['total_items'] if total_items_result else 0
        
        cursor.execute("SELECT COUNT(*) as custom_categories FROM categories WHERE is_custom = TRUE")
        custom_categories_result = cursor.fetchone()
        custom_categories = custom_categories_result['custom_categories'] if custom_categories_result else 0
        
        stats = {
            'total_categories': total_categories,
            'total_items': total_items,
            'custom_categories': custom_categories
        }
        
        return render_template('admin_menu_management.html', 
                             categories=categories, 
                             items=items, 
                             stats=stats)
        
    except mysql.connector.Error as err:
        flash(f"Database error: {err}")
        return redirect(url_for('admin_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# API Routes for Menu Management
@app.route('/api/add-category', methods=['POST'])
def api_add_category():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    category_name = data.get('category_name', '').strip()
    display_name = data.get('display_name', '').strip()
    
    if not category_name or not display_name:
        return jsonify({'success': False, 'message': 'Category name and display name are required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if category already exists
        cursor.execute("SELECT * FROM categories WHERE category_name = %s", (category_name,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Category already exists'})
        
        # Insert new category
        cursor.execute("""
            INSERT INTO categories (category_name, display_name, is_custom) 
            VALUES (%s, %s, TRUE)
        """, (category_name, display_name))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Category added successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

@app.route('/api/add-item', methods=['POST'])
def api_add_item():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    item_name = data.get('item_name', '').strip()
    price = data.get('price')
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    
    if not item_name or not price or not category:
        return jsonify({'success': False, 'message': 'Item name, price, and category are required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Get category_id from category name
        cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (category,))
        cat_result = cursor.fetchone()
        if not cat_result:
            return jsonify({'success': False, 'message': 'Invalid category'})
        
        category_id = cat_result[0]
        
        # Insert new item
        cursor.execute("""
            INSERT INTO Items (item_name, price, category_id, description) 
            VALUES (%s, %s, %s, %s)
        """, (item_name, price, category_id, description if description else None))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Item added successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

@app.route('/api/get-item/<int:item_id>')
def api_get_item(item_id):
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Get item with category name via JOIN
        cursor.execute("""
            SELECT i.*, c.category_name as category 
            FROM Items i
            LEFT JOIN categories c ON i.category_id = c.category_id
            WHERE i.item_id = %s
        """, (item_id,))
        item = cursor.fetchone()
        
        if item:
            return jsonify({'success': True, 'item': item})
        else:
            return jsonify({'success': False, 'message': 'Item not found'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

@app.route('/api/update-item', methods=['POST'])
def api_update_item():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    item_id = data.get('item_id')
    item_name = data.get('item_name', '').strip()
    price = data.get('price')
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    
    if not item_id or not item_name or not price or not category:
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Get category_id from category name
        cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (category,))
        cat_result = cursor.fetchone()
        if not cat_result:
            return jsonify({'success': False, 'message': 'Invalid category'})
        
        category_id = cat_result[0]
        
        cursor.execute("""
            UPDATE Items 
            SET item_name = %s, price = %s, category_id = %s, description = %s 
            WHERE item_id = %s
        """, (item_name, price, category_id, description if description else None, item_id))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Item updated successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

@app.route('/api/delete-item', methods=['POST'])
def api_delete_item():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({'success': False, 'message': 'Item ID is required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if item exists in any orders
        cursor.execute("SELECT COUNT(*) as count FROM order_details WHERE item_id = %s", (item_id,))
        result = cursor.fetchone()
        if result and result[0] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete item: It exists in order history'})
        
        # Delete the item
        cursor.execute("DELETE FROM Items WHERE item_id = %s", (item_id,))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# Dynamic Category Page Route
@app.route('/category/<category_name>')
def dynamic_category(category_name):
    return render_category_page(category_name)

# Table Orders Management Routes
@app.route('/table-orders')
def table_orders():
    if 'user_id' not in session or not session.get('is_admin', False):
        flash("Access Denied: Admin privileges required")
        return redirect(url_for('index'))
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        if not db:
            flash("Database connection failed")
            return redirect(url_for('admin_dashboard'))
        
        cursor = db.cursor(dictionary=True)
        
        # Get all tables with their current orders
        cursor.execute("""
            SELECT 
                t.*,
                o.table_order_id,
                o.total_amount,
                o.status as order_status
            FROM restaurant_tables t
            LEFT JOIN table_orders o ON t.table_id = o.table_id AND o.status = 'active'
            ORDER BY t.table_number
        """)
        tables_data = cursor.fetchall()
        
        # Process tables
        tables = []
        for table in tables_data:
            table_dict = {
                'table_id': table['table_id'],
                'table_number': table['table_number'],
                'table_name': table['table_name'],
                'seats': table['seats'],
                'status': table['status'],
                'current_order': None
            }
            
            if table['table_order_id']:
                table_dict['current_order'] = {
                    'table_order_id': table['table_order_id'],
                    'total_amount': table['total_amount']
                }
            
            tables.append(table_dict)
        
        # Get all menu items
        cursor.execute("SELECT item_id, item_name, price, category FROM Items ORDER BY category, item_name")
        menu_items = cursor.fetchall()
        
        # Get stats
        cursor.execute("SELECT COUNT(*) as total FROM restaurant_tables")
        total_tables = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as available FROM restaurant_tables WHERE status = 'available'")
        available_tables = cursor.fetchone()['available']
        
        cursor.execute("SELECT COUNT(*) as occupied FROM restaurant_tables WHERE status = 'occupied'")
        occupied_tables = cursor.fetchone()['occupied']
        
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as revenue 
            FROM table_orders 
            WHERE DATE(completed_at) = CURDATE() AND status = 'completed'
        """)
        total_revenue = cursor.fetchone()['revenue']
        
        stats = {
            'total_tables': total_tables,
            'available_tables': available_tables,
            'occupied_tables': occupied_tables,
            'total_revenue': total_revenue
        }
        
        return render_template('table_orders.html', 
                             tables=tables, 
                             menu_items=menu_items,
                             stats=stats)
        
    except mysql.connector.Error as err:
        flash(f"Database error: {err}")
        return redirect(url_for('admin_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# API: Add Table
@app.route('/api/add-table', methods=['POST'])
def api_add_table():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    table_number = data.get('table_number')
    table_name = data.get('table_name', '').strip()
    seats = data.get('seats', 4)
    
    if not table_number:
        return jsonify({'success': False, 'message': 'Table number is required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if table number exists
        cursor.execute("SELECT * FROM restaurant_tables WHERE table_number = %s", (table_number,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Table number already exists'})
        
        # Insert new table
        cursor.execute("""
            INSERT INTO restaurant_tables (table_number, table_name, seats) 
            VALUES (%s, %s, %s)
        """, (table_number, table_name if table_name else None, seats))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Table added successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# API: Delete Table
@app.route('/api/delete-table', methods=['POST'])
def api_delete_table():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    table_id = data.get('table_id')
    
    if not table_id:
        return jsonify({'success': False, 'message': 'Table ID is required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Check if table has active orders
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM table_orders 
            WHERE table_id = %s AND status = 'active'
        """, (table_id,))
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete table with active orders'})
        
        # Delete table
        cursor.execute("DELETE FROM restaurant_tables WHERE table_id = %s", (table_id,))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Table deleted successfully'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# API: Save Table Order
@app.route('/api/save-table-order', methods=['POST'])
def api_save_table_order():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    table_id = data.get('table_id')
    order_id = data.get('order_id')
    items = data.get('items', {})
    
    if not table_id or not items:
        return jsonify({'success': False, 'message': 'Table ID and items are required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Calculate total
        total_amount = sum(item['price'] * item['quantity'] for item in items.values())
        
        if order_id:
            # Update existing order
            cursor.execute("""
                UPDATE table_orders 
                SET total_amount = %s 
                WHERE table_order_id = %s
            """, (total_amount, order_id))
            
            # Delete old items
            cursor.execute("DELETE FROM table_order_items WHERE table_order_id = %s", (order_id,))
        else:
            # Create new order
            cursor.execute("""
                INSERT INTO table_orders (table_id, total_amount, status) 
                VALUES (%s, %s, 'active')
            """, (table_id, total_amount))
            order_id = cursor.lastrowid
            
            # Update table status
            cursor.execute("""
                UPDATE restaurant_tables 
                SET status = 'occupied' 
                WHERE table_id = %s
            """, (table_id,))
        
        # Insert order items
        for item_id, item_data in items.items():
            subtotal = item_data['price'] * item_data['quantity']
            cursor.execute("""
                INSERT INTO table_order_items 
                (table_order_id, item_id, quantity, price, subtotal) 
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item_id, item_data['quantity'], item_data['price'], subtotal))
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Order saved successfully', 'order_id': order_id})
        
    except mysql.connector.Error as err:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# API: Get Table Order
@app.route('/api/get-table-order/<int:order_id>')
def api_get_table_order(order_id):
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                toi.*,
                i.item_name
            FROM table_order_items toi
            JOIN Items i ON toi.item_id = i.item_id
            WHERE toi.table_order_id = %s
        """, (order_id,))
        
        items = cursor.fetchall()
        
        if not items:
            return jsonify({'success': False, 'message': 'No items in this order. Please add items before completing.'})
        
        return jsonify({'success': True, 'items': items})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# API: Complete Table Order
@app.route('/api/complete-table-order', methods=['POST'])
def api_complete_table_order():
    if 'user_id' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    table_id = data.get('table_id')
    order_id = data.get('order_id')
    
    if not table_id or not order_id:
        return jsonify({'success': False, 'message': 'Table ID and Order ID are required'})
    
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Get order items with details
        cursor.execute("""
            SELECT 
                toi.*,
                i.item_name
            FROM table_order_items toi
            JOIN Items i ON toi.item_id = i.item_id
            WHERE toi.table_order_id = %s
        """, (order_id,))
        
        items = cursor.fetchall()
        
        if not items:
            return jsonify({'success': False, 'message': 'Order not found or has no items'})
        
        # Calculate total
        total_amount = sum(float(item['subtotal']) for item in items)
        
        # Update order with total and mark as completed
        cursor.execute("""
            UPDATE table_orders 
            SET total_amount = %s, status = 'completed', completed_at = NOW() 
            WHERE table_order_id = %s
        """, (total_amount, order_id))
        
        # Update table status
        cursor.execute("""
            UPDATE restaurant_tables 
            SET status = 'available' 
            WHERE table_id = %s
        """, (table_id,))
        
        db.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Order completed successfully',
            'total': float(total_amount),
            'items': items
        })
        
    except mysql.connector.Error as err:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

# Make sure to add a debug line to help troubleshoot
if __name__ == '__main__':
    app.run(debug=True)