#|||| Imports ||||#


from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import URLField
from wtforms.validators import DataRequired
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Text, create_engine, MetaData, Column, Table
import os
from dotenv import load_dotenv


#|||| App + Bootstrap initializations ||||#


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("API_KEY")
Bootstrap5(app)


#|||| Connection to the PostgreSQL And Table initialization ||||#


load_dotenv() # In order to read the .env file.

# Creating the arguments for the PostgreSQL Database. (Using .env file to do it!)

user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST") # Pls change the listen_address in the file "postgresql.conf" to listen_address = '*' if you want the localhost to work.
# Also pls don't forget to close and open pg Admin after this. Pretty please :3
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

# Creating a variable that will usher in the connection to the Database.

Database_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"


da_engine = create_engine(Database_URL) # You can see the SQL statements being sent to the DB by passing echo=True when the engine instance is created.

# The engine itself is used to perform all the operations like creating tables, inserting or modifying values into a table, etc.


meta_data_obj = MetaData() # A Python object that represents database concepts like tables and columns.

# This object is essentially a facade around a Python dictionary that stores a series of Table objects keyed to their string name.

cafe_table = Table( # The main table for the PostgreSQL Database.

    "Cafe Data",

    meta_data_obj,

    Column("cafe_name", Text, nullable=False, unique=True),
    Column("location", Text, nullable=False, unique=True),
    Column("open_time", Text, nullable=False),
    Column("close_time", Text, nullable=False),
    Column("coffee_rating", Text, nullable=False),
    Column("wifi_rating", Text, nullable=False),
    Column("power_rating", Text, nullable=False)

)

meta_data_obj.create_all(da_engine) # Emitting DDL (Data Definition Language), which allows me to query the DataBase. (I.e. perform Create, Alter, Drop, Truncate, Comment and Rename actions).


Session = sessionmaker(bind=da_engine) # To show the table's data through the "query" function.


# Passing the bind parameter so it'd have an engine to rely on to fetch the data.


session = Session()


#|||| Submit Form ||||#


class CafeForm(FlaskForm):

    cafe = StringField('Cafe name', validators=[DataRequired()])
    da_location = URLField(label="Location", validators=[DataRequired()])
    time_open = StringField(label="Open Time", validators=[DataRequired()])
    time_close = StringField(label="Closing Time", validators=[DataRequired()])
    da_rating_coffee = SelectField(label="Coffee Rating", validators=[DataRequired()],
                                   choices=[("☕️", "☕️"), ("☕️☕️", "☕️☕️"), ("☕️☕️☕️", "☕️☕️☕️"), ("☕️☕️☕️☕️", "☕️☕️☕️☕️"), ("☕️☕️☕️☕️☕️", "☕️☕️☕️☕️☕️")])
    da_rating_wifi = SelectField(label="Wi-Fi Rating", validators=[DataRequired()],
                                 choices=[("✘", "✘"), ("💪", "💪"), ("💪💪", "💪💪"), ("💪💪💪", "💪💪💪"), ("💪💪💪💪", "💪💪💪💪"), ("💪💪💪💪💪", "💪💪💪💪💪")])
    da_rating_power = SelectField(label="Power Outlet Rating", validators=[DataRequired()],
                                  choices=[("🔌", "🔌"), ("🔌🔌", "🔌🔌"), ("🔌🔌🔌", "🔌🔌🔌"), ("🔌🔌🔌🔌", "🔌🔌🔌🔌"), ("🔌🔌🔌🔌🔌", "🔌🔌🔌🔌🔌")])
    submit = SubmitField('Submit')


#|||| Website Routes ||||#


@app.route("/")
def home(): # Just a home page.

    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe(): # Speaks for itself, takes all the inputs from the form (CafeForm()) and then adds them into the cafe_table.

    form = CafeForm()

    name = form.cafe.data
    location = form.da_location.data
    da_open = form.time_open.data
    da_close = form.time_close.data
    da_coffee = form.da_rating_coffee.data
    da_wifi = form.da_rating_wifi.data
    da_power = form.da_rating_power.data


    if form.validate_on_submit():

        if request.method == "POST":

            with da_engine.connect() as connection:

                connection.execute(cafe_table.insert(), {

                    "cafe_name": name,

                    "location": location,

                    "open_time": da_open,

                    "close_time": da_close,

                    "coffee_rating": da_coffee,

                    "wifi_rating": da_wifi,

                    "power_rating": da_power

                })

                connection.commit()

            return redirect("/cafes")


    return render_template("add.html", form=form)


@app.route('/cafes')
def cafes(): # Shows all the cafés in a table.

    return render_template("cafes.html", cafes=session.query(cafe_table).all())


@app.route("/delete/<cafe_name>", methods=["GET"])
def delete(cafe_name): # Deletes a café using its name as a sort-of replacement for the ID.

    # (Since the website wasn't build with IDs in mind, had to find some workarounds, please bare with me...)

    with da_engine.connect() as connection:

        connection.execute(

            cafe_table.delete().

            where(cafe_table.c.cafe_name == cafe_name) # Tapping into the "cafe_name" column of the "cafe_table" to find the row that has been selected by the user.

            # The query is based on the name of the café that was passed as an argument when the user clicked the "delete café" button.

        )

        connection.commit()

    return redirect("/cafes")


if __name__ == "__main__":
    app.run(debug=True)
