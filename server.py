from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql  # Ensure you have this installed (`pip install pymysql`)
import stripe
import os
import dotenv


dotenv.load_dotenv()
from sqlalchemy import select
app = Flask(__name__)

# Remote MySQL Database Connection
DB_USERNAME = "admin"
DB_PASSWORD = "FuckAWS123"
DB_HOST = "military-surplus-database.czoa6guwqu7m.eu-north-1.rds.amazonaws.com"
DB_NAME = "military-surplus"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'AWS_sucks'

# Session Configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#session(app)

db = SQLAlchemy(app)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# Define User Model
class User(db.Model):
    __tablename__ = "users"  # Ensure this matches your MySQL table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Store hashed passwords

class Shopping_Cart(db.Model):
    __tablename__ = "shopping_cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Shopping_Cart_Items(db.Model):
    __tablename__ = "shopping_cart_items"
    id = db.Column(db.Integer, primary_key=True)
    shopping_cart_id = db.Column(db.Integer, db.ForeignKey('shopping_cart.id'),  nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),  nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

# Home Page
@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "GET":
        
       products_list = Products.query.all()
    
    
    
    return render_template("index.html",products = products_list)

# Registration Page (GET and POST)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=name).first()
        if existing_user:
            flash("Username already taken. Please choose another.", "danger")
            return redirect(url_for("register"))

        # Hash password before storing it
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        
        # Create new user and add to database
        new_user = User(username=name, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")

# Login Route
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method== "POST":

        name = request.form.get("username")
        password = request.form.get("password")


        user = User.query.filter_by(username=name).first()  # Fetch user from database
        if check_password_hash(user.password_hash, password):
            flash("Login Successful!", "success")
            print("login successful")

            session["user_id"] = user.id  # Store user ID in session
            
            return redirect(url_for("index"))  # Redirect to dashboard
        else:
            flash("Invalid Credentials. Try Again.", "danger")
            return redirect(url_for("index"))
    
    return render_template("login.html")

# Ensure user has a shopping cart
def get_or_create_cart(user_id):
    cart = Shopping_Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Shopping_Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

# Add product to cart
@app.route("/add/<int:product_id>", methods=["GET","POST"])
def add_to_cart(product_id):
    if "user_id" not in session:
        flash("You must be logged in to add items to your cart.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    cart = get_or_create_cart(user_id)
    
    # Check if product is already in cart
    item = Shopping_Cart_Items.query.filter_by(shopping_cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += 1
    else:
        new_item = Shopping_Cart_Items(shopping_cart_id=cart.id, product_id=product_id, quantity=1)
        db.session.add(new_item)
    
    db.session.commit()
    flash("Product added to cart!", "success")
    return redirect(url_for("view_cart"))

# View cart
@app.route("/cart")
def view_cart():
    if "user_id" not in session:
        flash("You must be logged in to view your cart.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    cart = Shopping_Cart.query.filter_by(user_id=user_id).first()
    items = []
    if cart:
        items = db.session.query(Shopping_Cart_Items, Products).join(Products).filter(Shopping_Cart_Items.shopping_cart_id == cart.id).all()
    return render_template("cart.html", items=items)

# Remove item from cart
@app.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    if "user_id" not in session:
        flash("You must be logged in to remove items from your cart.", "danger")
        return redirect(url_for("login"))
    
    item = Shopping_Cart_Items.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "success")
    return redirect(url_for("view_cart"))

# Clear cart
@app.route("/cart/clear", methods=["POST"])
def clear_cart():
    if "user_id" not in session:
        flash("You must be logged in to clear your cart.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    cart = Shopping_Cart.query.filter_by(user_id=user_id).first()
    if cart:
        Shopping_Cart_Items.query.filter_by(shopping_cart_id=cart.id).delete()
        db.session.commit()
        flash("Shopping cart cleared.", "success")
    return redirect(url_for("view_cart"))

# Dashboard Page
@app.route("/dashboard")
def dashboard():
    return "<h1>Welcome to the Dashboard!</h1>"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    if "user_id" not in session:
        flash("You must be logged in to checkout.", "danger")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    cart = Shopping_Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        flash("Your cart is empty.", "danger")
        return redirect(url_for("view_cart"))

    items = db.session.query(Shopping_Cart_Items, Products).join(Products).filter(Shopping_Cart_Items.shopping_cart_id == cart.id).all()
    if not items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for("view_cart"))

    line_items = []
    for item, product in items:
        stripe_product = stripe.Product.create(
            name=product.name,
            description=product.description,
        )
        stripe_price = stripe.Price.create(
            product=stripe_product.id,
            unit_amount=int(product.price * 100),  # Price in cents
            currency='usd',
        )
        line_items.append({
            'price': stripe_price.id,
            'quantity': item.quantity,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route("/checkout.html")
def checkout():
    return render_template("checkout.html")

@app.route("/success.html")
def success():
    return render_template("success.html")
    
@app.route("/cancel.html")
def cancel():
    return render_template("cancel.html")

def create_stripe_products():
    products = Product.query.all()
    stripe_products = []

    for product in products:
        stripe_product = stripe.Product.create(
            name=product.name,
            description=product.description,
        )
        stripe_price = stripe.Price.create(
            product=stripe_product.id,
            unit_amount=int(product.price * 100), # Price in cents
            currency='usd',
        )
        stripe_products.append({
            'product_id': stripe_product.id,
            'price_id': stripe_price.id,
        })

    return stripe_products

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
