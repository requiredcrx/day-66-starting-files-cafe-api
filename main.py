import random

from flask import Flask, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

# Get Random Cafe from the database
@app.route('/random', methods=["GET"])
def get_random_cafe():
    cafe = db.session.execute(db.select(Cafe))
    all_cafes = cafe.scalars().all()
    result = random.choice(all_cafes)
    return jsonify(cafe={
        "id": result.id,
        "name": result.name,
        "map_url": result.map_url,
        "img_url": result.img_url,
        "location": result.location,
        "has_socket": result.has_sockets,
        "has_toilet": result.has_toilet,
        "has_wifi": result.has_wifi,
        "can_take_calls": result.can_take_calls,
        "seat": result.seats,
        "coffee_price": result.coffee_price

    })


# Get all Cafe
@app.route('/all')
def get_all_cafe():
    all_cafe = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    result = all_cafe.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in result])


# Search cafe with location
@app.route("/search")
def get_location():
    location = request.args.get("location")
    if not location:
        # Return all cafes
        cafes = Cafe.query.all()
    else:
        # filter by location
        cafes = Cafe.query.filter_by(location=location).all()

    if not cafes:
        # Return error message
        return jsonify({
            "error": "No cafe found for location '{}'".format(location)
        }), 404

    else:
        # Return JSON response
        return jsonify({"cafes": [cafe.to_dict() for cafe in cafes]})


# Add new cafe
@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"Success": "Successfully added new cafe."})


# Update price of a cafe
@app.route("/update_price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Coffee price has been successfully updated"}), 200
    else:
        return jsonify(response={"Not found": f"No cafe with the id {cafe_id} found"}), 404


# Delete a cafe
@app.route("/report_closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        if request.args.get("api_key") == "TopSecretKey":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": f"Cafe data with name {cafe.name} successfully deleted."}), 200
        else:
            return jsonify(
                response={"Access Denied": "Invalid API Key. You have no authorization to delete cafe data."}), 403
    else:
        return jsonify(response={"Not found": "No cafe with the id is found."}), 404






## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
