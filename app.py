import datetime
from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import json
import os
from flask_cors import CORS  # Add this import

app = Flask(__name__)
CORS(app)  # Add this line right after creating the app
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
@app.route('/signup', methods=['POST'])
def signup():
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
        cursor.execute("SELECT user_id, password, username, is_admin FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            current_user_id = user['user_id']
            
            # Check if there's an existing cart that belongs to a different user
            old_cart_owner = session.get('cart_owner')
            
            # Clear the entire session to remove any previous user's data
            session.clear()
            
            # Set new user session data
            session['user_id'] = current_user_id
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)  # Store admin status
            
            # Always set flag to clear localStorage cart on login to ensure isolation
            session['clear_local_cart'] = True
            
            return redirect(url_for('index'))
        else:
            flash("Login Failed: Invalid credentials")
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
    return redirect(url_for('home'))

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
    try:
        connection = get_db_connection()
        if not connection:
            return render_template('menu.html', items=[], error="Database connection failed")
            
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Items")  # Using 'Items' with capital I as per your schema
        items = cursor.fetchall()
        return render_template('menu.html', items=items)
    except mysql.connector.Error as err:
        print(f"Database error in menu: {err}")
        return render_template('menu.html', items=[], error=str(err))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()

# Category specific routes
@app.route('/veg')
def veg():
    clear_local = session.pop('clear_local_cart', False)
    return render_template('veg.html', clear_local_cart=clear_local)

@app.route('/nonveg')
def nonveg():
    clear_local = session.pop('clear_local_cart', False)
    return render_template('nonveg.html', clear_local_cart=clear_local)

@app.route('/snacks')
def snacks():
    clear_local = session.pop('clear_local_cart', False)
    return render_template('snacks.html', clear_local_cart=clear_local)

@app.route('/beverages')
def beverages():
    clear_local = session.pop('clear_local_cart', False)
    return render_template('beverages.html', clear_local_cart=clear_local)

# Cart routes
@app.route('/cart')
def cart():
    clear_local = session.pop('clear_local_cart', False)
    return render_template("cart.html", clear_local_cart=clear_local)

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
        
        # Parse existing cart
        if 'cart_data' not in session:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
            
        cart = json.loads(session['cart_data'])
        
        # Update or remove item
        if str(item_id) in cart['items']:
            if quantity > 0:
                cart['items'][str(item_id)]['quantity'] = quantity
            else:
                del cart['items'][str(item_id)]
                
            # Save updated cart to session
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
        
        # 1. Insert customer details
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
            
            # 1. Insert customer details
            print("Inserting customer details")
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
                SELECT od.*, i.item_name, i.category
                FROM order_details od
                JOIN Items i ON od.item_id = i.item_id
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
        
        return render_template('order_confirmation.html', order_id=order_id)
                              
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
            SELECT i.item_name, i.category, i.price,
                   COUNT(od.item_id) as order_count,
                   SUM(od.quantity) as total_quantity,
                   SUM(od.total_price) as total_revenue
            FROM order_details od
            JOIN Items i ON od.item_id = i.item_id
            GROUP BY od.item_id, i.item_name, i.category, i.price
            ORDER BY total_quantity DESC
            LIMIT 10
        """)
        top_items = cursor.fetchall()
        
        # 6. Revenue by Category
        cursor.execute("""
            SELECT i.category,
                   COUNT(od.item_id) as item_count,
                   SUM(od.total_price) as category_revenue
            FROM order_details od
            JOIN Items i ON od.item_id = i.item_id
            GROUP BY i.category
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

# Make sure to add a debug line to help troubleshoot
if __name__ == '__main__':
    app.run(debug=True)