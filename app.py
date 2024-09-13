# Imports
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# TODO Do not let the user add an empty task!

# Command to activate the virtual env (powershell) : .\venv\Scripts\Activate.ps1 
# Command to deactivate the venv: deactivate

# My App Setup
app = Flask(__name__)
Scss(app)

# Configure the SQLite database, with SQLALchemy (database name here)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db" 
# Add a flag for SQLAlchemy (to generate a db for each user vs having a pre-existing db)
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False 
db = SQLAlchemy(app)

# Create a MODEL for our db (MODEL is a row of data in our db)
# Data Class - Row of data
class MyTask(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.now) #utcnow is deprecated

    # Dunder method (string representation)
    def __repr__(self) -> str:
        return f"Task {self.id}"

# We moved the context manager here (???)
with app.app_context():
    db.create_all()

# Create a Task                             (Create a route with a decorator (@))
@app.route("/", methods=["POST","GET"])     # "/" Is for the HOME PAGE
def index():
    # Add a task
    if request.method == "POST":
        current_task = request.form["content"]
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)    # Create task
            db.session.commit()         # Commit to the db
            return redirect("/")        # Redirect to the home page
        except Exception as e:
            print(f"Error the problem is that {e}...")
            return f"Error the problem is that {e}..."
    # See all current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()     # Order by the date created
        return render_template("index.html", tasks=tasks)

# Delete an item
@app.route("/delete/<int:id>")                      # "/delete/" is the route and "<int:id>" represents each unique item
def delete(id:int):                                 # We will edit stuff based on the primary key (id)
    delete_task = MyTask.query.get_or_404(id)       # Delete the task or show error
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"Error: {e}."

# Edit an item 
@app.route("/edit/<int:id>", methods=["GET","POST"]) 
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}." 
    else:
        return render_template("edit.html", task=task)


# Code to deploy the app
if __name__ == "__main__":
    app.run(debug=True)    

# Run the program in debugging mode
# if __name__ in "__main__":
#     # Context manager
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

