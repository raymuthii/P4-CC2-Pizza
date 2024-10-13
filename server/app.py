#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# GET /restaurants - Return all restaurants
class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants])

# GET /restaurants/<int:id> - Return a specific restaurant and its pizzas
class RestaurantDetailResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify(restaurant.to_dict(only=("id", "name", "address", "restaurant_pizzas")))
        else:
            return make_response({"error": "Restaurant not found"}, 404)

    # DELETE /restaurants/<int:id> - Delete a restaurant and its associated RestaurantPizzas
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            # Delete all associated RestaurantPizzas first
            RestaurantPizza.query.filter_by(restaurant_id=id).delete()
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        else:
            return make_response({"error": "Restaurant not found"}, 404)

# GET /pizzas - Return all pizzas
class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas])

# POST /restaurant_pizzas - Create a new RestaurantPizza
class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()

        try:
            price = data['price']
            if not (1 <= price <= 30):
                raise ValueError("Price must be between 1 and 30")

            # Find pizza and restaurant
            pizza = Pizza.query.get(data['pizza_id'])
            restaurant = Restaurant.query.get(data['restaurant_id'])

            if not pizza or not restaurant:
                return make_response({"errors": ["Invalid pizza_id or restaurant_id"]}, 400)

            # Create RestaurantPizza
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            # Return response in the required format
            response = {
                "id": new_restaurant_pizza.id,
                "pizza": pizza.to_dict(only=("id", "name", "ingredients")),
                "pizza_id": new_restaurant_pizza.pizza_id,
                "price": new_restaurant_pizza.price,
                "restaurant": restaurant.to_dict(only=("id", "name", "address")),
                "restaurant_id": new_restaurant_pizza.restaurant_id
            }

            return jsonify(response), 201

        except ValueError as e:
            return make_response({"errors": [str(e)]}, 400)

# Registering routes
api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantDetailResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
