from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql  # Ensure you have this installed (`pip install pymysql`)
import stripe
import os
import dotenv


dotenv.load_dotenv()
app = Flask(__name__)

# Remote MySQL Database Connection
DB_USERNAME = "admin"
DB_PASSWORD = "FuckAWS123"
DB_HOST = "military-surplus-database.czoa6guwqu7m.eu-north-1.rds.amazonaws.com"
DB_NAME = "military-surplus"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'AWS_sucks'

db = SQLAlchemy(app)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Define User Model
class User(db.Model):
    __tablename__ = "users"  # Ensure this matches your MySQL table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Store hashed passwords

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

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
            return redirect(url_for("dashboard"))  # Redirect to dashboard
        else:
            flash("Invalid Credentials. Try Again.", "danger")
            return redirect(url_for("index"))
    
    return render_template("login.html")

# Dashboard Page
@app.route("/dashboard")
def dashboard():
    return "<h1>Welcome to the Dashboard!</h1>"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    print(os.getenv("STRIPE_SECRET_KEY"))
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1QwPHgJAlkdUJocHDyvZBXLK',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url= "http://127.0.0.1:5000" + '/success.html',
            cancel_url= "http://127.0.0.1:5000" + '/cancel.html',
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

product = stripe.Product.create(
    name="T-shirt",
    description="Comfortable cotton t-shirt",
)

# Create a price for the product
price = stripe.Price.create(
    product=product.id,
    unit_amount=2000,  # Amount in cents (e.g., $20.00)
    currency="usd",
)

print(f"Product ID: {product.id}")
print(f"Price ID: {price.id}")

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
