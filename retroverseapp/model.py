from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy




db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Relationship to Order (admin could be linked to orders if needed)
    # orders = db.relationship('Order', backref='admin', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationship to Product
    

class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)  # e.g., 'LA', 'AB', etc.

    # Relationship to Customer
    customers = db.relationship('Customer', backref='state', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(95), nullable=False)
    # Foreign key to State
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=True)

    # Relationship to Order
    orders = db.relationship('Order', backref='customer')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    size = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    
    # Foreign key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Add a field for tags (optional)
    tags = db.Column(db.String(255), nullable=True)  # E.g., 'latest, summer, men'

    
    

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(50), nullable=False)  # e.g., 'pending', 'shipped', 'delivered'
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Foreign key to Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    # Relationship to OrderItem
    order_items = db.relationship('OrderItem', backref='order')

    # Relationship to Delivery
    delivery = db.relationship('Delivery', backref='order')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    # Foreign key to Product
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Foreign key to Order
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    delivery_status = db.Column(db.String(50), nullable=False)  # e.g., 'pending', 'in transit', 'delivered'
    delivery_address = db.Column(db.String(255), nullable=False)

    # Foreign key to Order
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Link to the customer
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)    # Link to the product
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)  # New quantity field
    # Relationships
    customer = db.relationship('Customer', backref='wishlists')
    product = db.relationship('Product', backref='wishlists')
