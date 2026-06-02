from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, inspect, text
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from io import BytesIO
import json
import os
import re
import secrets
import socket
import qrcode

app = Flask(__name__)
app.secret_key = 'shopease-secret-key-2024'
app.debug = False
PUBLIC_URL_FILE = os.path.join(app.instance_path, "public_base_url.txt")

# ── SQLite Database Setup ─────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopease.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 30},
    'pool_pre_ping': True,
}
db = SQLAlchemy(app)

# Configure SQLite for better concurrency
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if getattr(dbapi_conn, "__class__", None).__module__ == "sqlite3":
        cursor = dbapi_conn.cursor()
        try:
            cursor.execute("PRAGMA busy_timeout = 30000")
            try:
                cursor.execute("PRAGMA journal_mode=WAL")
            except Exception:
                pass
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")
        finally:
            cursor.close()

# ── Jinja2 Filters ─────────────────────────────────────────────
@app.template_filter('strftime')
def format_datetime(value, format_string):
    if value is None:
        return ''
    return value.strftime(format_string)

@app.template_filter('currency')
def format_currency(value):
    """Format number as INR currency with comma separators"""
    try:
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return "0"

# ── User Model ────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    cart_items = db.Column(db.Text, nullable=False, default='{}')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

# ── Order Model ───────────────────────────────────────────────
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.now)
    items = db.Column(db.Text, nullable=False)  # JSON string of cart items
    status = db.Column(db.String(20), default='completed')
    
    # Address fields
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<Order {self.id} - {self.payment_method}>'


class PaymentSession(db.Model):
    __tablename__ = 'payment_sessions'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(120), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkout_data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    order_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<PaymentSession {self.token} - {self.status}>'

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "cart_items" not in user_columns:
        with db.engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN cart_items TEXT NOT NULL DEFAULT '{}'"))

# ── Authentication Decorator ──────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login or register to continue", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ── Product Data ──────────────────────────────────────────────
PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 650, "category": "Electronics",
     "image": "headphones.jpg",
     "description": "Premium matte black wireless headphones with noise cancellation and 30-hour battery life."},
    {"id": 2, "name": "Classic Wristwatch", "price": 1200, "category": "Accessories",
     "image": "watch.jpg",
     "description": "Minimalist analog watch with genuine leather strap and Japanese quartz movement."},
    {"id": 3, "name": "Canvas Tote Bag", "price": 270, "category": "Accessories",
     "image": "bag.jpg",
     "description": "Durable organic cotton canvas tote bag, perfect for everyday carry."},
    {"id": 4, "name": "White Sneakers", "price": 800, "category": "Footwear",
     "image": "sneakers.jpg",
     "description": "Clean minimal sneakers crafted from premium leather with cushioned insole."},
    {"id": 5, "name": "Ceramic Mug", "price": 156, "category": "Home",
     "image": "mug.jpg",
     "description": "Handcrafted matte white ceramic mug, microwave and dishwasher safe."},
    {"id": 6, "name": "Portable Speaker", "price": 499, "category": "Electronics",
     "image": "speaker.jpg",
     "description": "Compact Bluetooth speaker with rich bass and 12-hour playtime."},
    {"id": 7, "name": "Sunglasses", "price": 1999, "category": "Accessories",
     "image": "sunglasses.jpg",
     "description": "UV-protective polarized sunglasses with stainless steel frame."},
    {"id": 8, "name": "Running Shoes", "price": 844, "category": "Footwear",
     "image": "Running shoes.jpeg",
     "description": "Lightweight breathable running shoes with cushioned sole for maximum comfort."},
    {"id": 9, "name": "Bluetooth Earbuds", "price": 699, "category": "Electronics",
     "image": "bluethoot earbuds.jpeg",
     "description": "True wireless earbuds with active noise cancellation and touch controls."},
    {"id": 10, "name": "Desk Lamp", "price": 119, "category": "Home",
     "image": "desk lamp.jpeg",
     "description": "Adjustable LED desk lamp with USB charging port and three brightness modes."},
    {"id": 11, "name": "Leather Belt", "price": 329, "category": "Accessories",
     "image": "leather belt.jpeg",
     "description": "Genuine leather belt with stainless steel buckle, available in black and brown."},
    {"id": 12, "name": "Coffee Maker", "price": 299, "category": "Home",
     "image": "coffee_maker.jpg",
     "description": "Programmable coffee maker with thermal carafe and auto-shutoff feature."},
    {"id": 14, "name": "Phone Stand", "price": 1999, "category": "Electronics",
     "image": "phone stand.jpeg",
     "description": "Adjustable aluminum phone stand compatible with all smartphones and tablets."},
    {"id": 15, "name": "Pillow", "price": 369, "category": "Home",
     "image": "pillow.jpeg",
     "description": "Memory foam pillow with cooling gel technology for better sleep quality."},
]

CATEGORIES = ["All"] + list(set(p["category"] for p in PRODUCTS))


def normalize_cart(cart):
    normalized = {}
    for product_id, quantity in (cart or {}).items():
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            continue
        if qty > 0:
            normalized[str(product_id)] = qty
    return normalized


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def load_user_cart(user):
    if not user or not user.cart_items:
        return {}
    try:
        return normalize_cart(json.loads(user.cart_items))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def persist_user_cart(cart, user=None):
    user = user or get_current_user()
    if not user:
        return

    user.cart_items = json.dumps(normalize_cart(cart))
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_cart():
    cart = normalize_cart(session.get("cart", {}))
    session["cart"] = cart
    return cart


def save_cart(cart):
    normalized_cart = normalize_cart(cart)
    session["cart"] = normalized_cart
    persist_user_cart(normalized_cart)


def clear_user_cart_data(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return

    user.cart_items = json.dumps({})
    db.session.commit()


def validate_checkout_input(payment_method, street_address, city, state, zip_code, phone,
                            cardholder_name="", card_number="", expiry_date="", cvv=""):
    valid_methods = ["credit_card", "debit_card", "paypal", "google_pay", "apple_pay", "cash_on_delivery"]
    if payment_method not in valid_methods:
        return "Invalid payment method selected"

    if not all([street_address, city, state, zip_code, phone]):
        return "Please fill in all address fields"

    if payment_method in {"credit_card", "debit_card"}:
        normalized_card_number = re.sub(r"\D", "", card_number)
        normalized_cvv = re.sub(r"\D", "", cvv)
        expiry_match = re.fullmatch(r"(0[1-9]|1[0-2])\/(\d{2})", expiry_date)

        if not all([cardholder_name, normalized_card_number, expiry_date, normalized_cvv]):
            return "Please complete all card details before placing the order"

        if len(normalized_card_number) < 16 or len(normalized_card_number) > 19:
            return "Card number must be between 16 and 19 digits"

        if not expiry_match:
            return "Expiry date must be in MM/YY format"

        if len(normalized_cvv) not in {3, 4}:
            return "CVV must be 3 or 4 digits"

    return None


def build_order_items(cart_data):
    total = 0
    items_info = []
    for pid_str, qty in cart_data.items():
        product = next((p for p in PRODUCTS if p["id"] == int(pid_str)), None)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            items_info.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": qty
            })
    return total, items_info


def create_order_for_user(user_id, payment_method, cart_data, street_address, city, state, zip_code, phone):
    total, items_info = build_order_items(cart_data)
    if not items_info:
        return None

    order = Order(
        user_id=user_id,
        total_amount=total,
        payment_method=payment_method,
        order_date=datetime.now(),
        items=json.dumps(items_info),
        status="completed",
        street_address=street_address,
        city=city,
        state=state,
        zip_code=zip_code,
        phone=phone
    )
    db.session.add(order)
    db.session.commit()
    return order


def get_lan_base_url():
    host = request.host.split(":")[0]
    if host not in {"127.0.0.1", "localhost"}:
        return request.host_url.rstrip("/")

    port = request.host.split(":")[1] if ":" in request.host else "5000"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
        return f"{request.scheme}://{local_ip}:{port}"
    except OSError:
        return request.host_url.rstrip("/")


def get_public_base_url():
    public_base_url = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if public_base_url:
        return public_base_url

    if os.path.exists(PUBLIC_URL_FILE):
        try:
            with open(PUBLIC_URL_FILE, "r", encoding="utf-8") as handle:
                file_url = handle.read().strip().rstrip("/")
            if file_url:
                return file_url
        except OSError:
            pass

    return ""


def get_checkout_base_url():
    return get_public_base_url() or get_lan_base_url()


# ── Routes ────────────────────────────────────────────────────
@app.route("/")
@login_required
def index():
    category = request.args.get("category", "All")
    if category == "All":
        filtered = PRODUCTS
    else:
        filtered = [p for p in PRODUCTS if p["category"] == category]
    cart = get_cart()
    total_items = sum(cart.values())
    return render_template("index.html", products=filtered, categories=CATEGORIES,
                           active_category=category, total_items=total_items)


@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    save_cart(cart)
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if product:
        flash(f'{product["name"]} added to cart!', "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart")
@login_required
def cart():
    cart_data = get_cart()
    items = []
    total = 0
    for pid_str, qty in cart_data.items():
        product = next((p for p in PRODUCTS if p["id"] == int(pid_str)), None)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            items.append({**product, "quantity": qty, "subtotal": subtotal})
    total_items = sum(cart_data.values())
    return render_template("cart.html", items=items, total=total, total_items=total_items)


@app.route("/update_cart/<int:product_id>/<action>")
@login_required
def update_cart(product_id, action):
    cart = get_cart()
    key = str(product_id)
    if action == "increase":
        cart[key] = cart.get(key, 0) + 1
    elif action == "decrease":
        current = cart.get(key, 0)
        if current <= 1:
            cart.pop(key, None)
        else:
            cart[key] = current - 1
    elif action == "remove":
        cart.pop(key, None)
    save_cart(cart)
    return redirect(url_for("cart"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        if not email or not password:
            flash("Please enter email and password", "error")
        else:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session_cart = get_cart()
                saved_cart = load_user_cart(user)
                merged_cart = saved_cart.copy()
                for product_id, quantity in session_cart.items():
                    merged_cart[product_id] = merged_cart.get(product_id, 0) + quantity

                session["user_id"] = user.id
                session["user_email"] = user.email
                session["user_name"] = user.fullname
                session.permanent = True
                save_cart(merged_cart)
                flash(f"Welcome back, {user.fullname}!", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid email or password", "error")
    
    # Check if user is already logged in
    if "user_id" in session:
        return redirect(url_for("index"))
    total_items = 0
    return render_template("login.html", total_items=total_items)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not fullname or not email or not password or not confirm_password:
            flash("Please fill in all fields", "error")
        elif password != confirm_password:
            flash("Passwords do not match", "error")
        else:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please login instead.", "error")
            else:
                # Create new user
                new_user = User(fullname=fullname, email=email, cart_items=json.dumps(get_cart()))
                new_user.set_password(password)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                except OperationalError:
                    db.session.rollback()
                    flash("Database is busy right now. Please close any open database tools and try again.", "error")
                    return redirect(url_for("register"))
                except Exception:
                    db.session.rollback()
                    flash("We couldn't create your account right now. Please try again.", "error")
                    return redirect(url_for("register"))
                
                session["user_id"] = new_user.id
                session["user_email"] = new_user.email
                session["user_name"] = new_user.fullname
                session.permanent = True
                save_cart(load_user_cart(new_user))
                flash(f"Account created! Welcome, {fullname}!", "success")
                return redirect(url_for("index"))
    
    # Check if user is already logged in
    if "user_id" in session:
        return redirect(url_for("index"))
    total_items = 0
    return render_template("register.html", total_items=total_items)


@app.route("/logout")
def logout():
    persist_user_cart(get_cart())
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    payment_method = request.form.get("payment_method", "").strip()
    street_address = request.form.get("street_address", "").strip()
    city = request.form.get("city", "").strip()
    state = request.form.get("state", "").strip()
    zip_code = request.form.get("zip_code", "").strip()
    phone = request.form.get("phone", "").strip()
    cardholder_name = request.form.get("cardholder_name", "").strip()
    card_number = request.form.get("card_number", "").strip()
    expiry_date = request.form.get("expiry_date", "").strip()
    cvv = request.form.get("cvv", "").strip()
    
    validation_error = validate_checkout_input(
        payment_method,
        street_address,
        city,
        state,
        zip_code,
        phone,
        cardholder_name=cardholder_name,
        card_number=card_number,
        expiry_date=expiry_date,
        cvv=cvv
    )
    if validation_error:
        flash(validation_error, "error")
        return redirect(url_for("cart"))
    
    # Get cart data
    cart_data = get_cart()
    if not cart_data:
        flash("Your cart is empty", "error")
        return redirect(url_for("index"))

    try:
        order = create_order_for_user(
            session.get("user_id"),
            payment_method,
            cart_data,
            street_address,
            city,
            state,
            zip_code,
            phone
        )
        if not order:
            flash("We couldn't build the order from your cart.", "error")
            return redirect(url_for("cart"))
    except OperationalError:
        db.session.rollback()
        flash("Database is busy right now. Please try checkout again in a moment.", "error")
        return redirect(url_for("cart"))
    except Exception:
        db.session.rollback()
        flash("We couldn't place your order right now. Please try again.", "error")
        return redirect(url_for("cart"))
    
    # Clear cart
    save_cart({})
    
    # Redirect to order confirmation
    return redirect(url_for("order_confirmation", order_id=order.id))


@app.route("/google-pay/prepare", methods=["POST"])
@login_required
def prepare_google_pay():
    street_address = request.form.get("street_address", "").strip()
    city = request.form.get("city", "").strip()
    state = request.form.get("state", "").strip()
    zip_code = request.form.get("zip_code", "").strip()
    phone = request.form.get("phone", "").strip()

    validation_error = validate_checkout_input(
        "google_pay",
        street_address,
        city,
        state,
        zip_code,
        phone
    )
    if validation_error:
        return jsonify({"error": validation_error}), 400

    cart_data = get_cart()
    if not cart_data:
        return jsonify({"error": "Your cart is empty"}), 400

    PaymentSession.query.filter_by(user_id=session.get("user_id"), status="pending").delete()

    payment_session = PaymentSession(
        token=secrets.token_urlsafe(24),
        user_id=session.get("user_id"),
        checkout_data=json.dumps({
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "phone": phone,
            "cart": cart_data
        }),
        status="pending"
    )
    db.session.add(payment_session)
    db.session.commit()

    return jsonify({
        "token": payment_session.token,
        "qr_image_url": url_for("google_pay_qr_image", token=payment_session.token),
        "status_url": url_for("google_pay_status", token=payment_session.token)
    })


@app.route("/google-pay/qr/<token>")
def google_pay_qr_image(token):
    payment_session = PaymentSession.query.filter_by(token=token).first()
    if not payment_session:
        abort(404)

    checkout_url = f"{get_checkout_base_url()}{url_for('complete_google_pay', token=token)}"
    qr = qrcode.QRCode(border=2, box_size=8)
    qr.add_data(checkout_url)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


@app.route("/google-pay/complete/<token>")
def complete_google_pay(token):
    payment_session = PaymentSession.query.filter_by(token=token).first_or_404()

    if payment_session.status == "completed" and payment_session.order_id:
        if session.get("user_id") == payment_session.user_id:
            save_cart({})
            return redirect(url_for("order_confirmation", order_id=payment_session.order_id))
        return "<h2>Payment received</h2><p>Your order has already been placed successfully.</p>"

    try:
        checkout_data = json.loads(payment_session.checkout_data)
    except (TypeError, ValueError, json.JSONDecodeError):
        abort(400)

    try:
        order = create_order_for_user(
            payment_session.user_id,
            "google_pay",
            normalize_cart(checkout_data.get("cart", {})),
            checkout_data.get("street_address", "").strip(),
            checkout_data.get("city", "").strip(),
            checkout_data.get("state", "").strip(),
            checkout_data.get("zip_code", "").strip(),
            checkout_data.get("phone", "").strip()
        )
        if not order:
            abort(400)

        payment_session.status = "completed"
        payment_session.order_id = order.id
        payment_session.completed_at = datetime.utcnow()
        db.session.commit()
        clear_user_cart_data(payment_session.user_id)
    except OperationalError:
        db.session.rollback()
        return "<h2>Payment processing delayed</h2><p>Please scan again in a moment.</p>", 503
    except Exception:
        db.session.rollback()
        return "<h2>Payment failed</h2><p>We could not place the order from this QR code.</p>", 500

    if session.get("user_id") == payment_session.user_id:
        save_cart({})
        return redirect(url_for("order_confirmation", order_id=order.id))

    return "<h2>Payment successful</h2><p>Your order has been placed successfully.</p>"


@app.route("/google-pay/status/<token>")
@login_required
def google_pay_status(token):
    payment_session = PaymentSession.query.filter_by(token=token, user_id=session.get("user_id")).first_or_404()

    if payment_session.status == "completed" and payment_session.order_id:
        save_cart({})
        return jsonify({
            "status": "completed",
            "redirect_url": url_for("order_confirmation", order_id=payment_session.order_id)
        })

    return jsonify({"status": "pending"})


@app.route("/order_confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Security check - ensure user can only view their own orders
    if order.user_id != session.get("user_id"):
        flash("Unauthorized access", "error")
        return redirect(url_for("index"))
    
    # Parse items JSON
    items = json.loads(order.items)
    
    # Get product details for display
    items_with_details = []
    for item in items:
        product = next((p for p in PRODUCTS if p["id"] == item["id"]), None)
        if product:
            items_with_details.append({
                **item,
                "image": product.get("image", ""),
                "subtotal": item["price"] * item["quantity"]
            })
    
    # Get user info
    user = User.query.get(order.user_id)
    
    total_items = sum(item["quantity"] for item in items_with_details)
    
    return render_template("order_confirmation.html", 
                         order=order, 
                         items=items_with_details, 
                         user=user,
                         total_items=total_items)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=5000, threaded=True)
