from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship: A Restaurant has many RestaurantPizzas
    restaurant_pizzas = relationship('RestaurantPizza', backref='restaurant', cascade="all, delete-orphan")
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Serialization rules to limit recursion
    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship: A Pizza has many RestaurantPizzas
    restaurant_pizzas = relationship('RestaurantPizza', backref='pizza', cascade="all, delete-orphan")
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Serialization rules to limit recursion
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.pizzas')

    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys and relationships: RestaurantPizza belongs to a Restaurant and a Pizza
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)

    # Serialization rules to limit recursion
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # Validation for price: must be between 1 and 30
    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'