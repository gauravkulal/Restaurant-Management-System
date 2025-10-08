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
            password='password',  # Replace with your MySQL password
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
        cursor.execute("SELECT user_id, password, username FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
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

# Main pages
@app.route('/index')
def index():
    return render_template('index.html')

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
    return render_template('veg.html')

@app.route('/nonveg')
def nonveg():
    return render_template('nonveg.html')

@app.route('/snacks')
def snacks():
    return render_template('snacks.html')

@app.route('/beverages')
def beverages():
    return render_template('beverages.html')

# Cart routes
@app.route('/cart')
def cart():
    return render_template("cart.html")

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
    if request.method == 'POST':
        # Save cart data in session for later order processing
        cart_data = request.form.get('cart_data')
        if cart_data:
            session['cart_data'] = cart_data
        return render_template("checkout.html", cart_data=cart_data)
    
    # In case of GET request, use cart data from session if available
    cart_data = session.get('cart_data')
    return render_template("checkout.html", cart_data=cart_data)

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

# Make sure to add a debug line to help troubleshoot
if __name__ == '__main__':
    app.run(debug=True)