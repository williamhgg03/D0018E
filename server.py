from flask import Flask,render_template
 
 
# A bit of starting code to reshape later 
app = Flask(__name__)
 
@app.route("/")


# Serving a base index page for facilitating login and and a future search function
def index():
    return render_template("index.html")
 
 
 
# main
if __name__ == "__main__":
    app.run()