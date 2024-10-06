from shop.app import db,web,User
from flask import *
from sqlalchemy import *
from sqlalchemy.orm.relationships import *
from shop.product.models import Category,Subcategory,Product
from datetime import datetime



class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    profile_pic = db.Column(db.String(255))
    gender = db.Column(db.Enum('Male', 'Female', 'Other'))
    age = db.Column(db.Integer)
    user = db.relationship('User', backref='profile')


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.pid'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    __tablename__ = 'order'

    ord_id = db.Column(db.String(10), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ord_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='Pending')  # Status field added
    cus_name = db.Column(db.String(100))  # Assuming 100 characters for customer name
    ord_city = db.Column(db.String(100))  # Assuming 100 characters for city
    pincode = db.Column(db.String(20))  # Assuming 20 characters for pincode
    shipping_address = db.Column(db.String(100))
    payment_type = db.Column(db.String(50), nullable=True)
    telephone=db.Column(db.Integer,nullable=True)

    user = db.relationship('User', backref='orders')
    order_details = db.relationship('OrderDetail', backref='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Order {self.order_id}>"


class OrderDetail(db.Model):
    __tablename__ = 'order_detail'

    id = db.Column(db.Integer, primary_key=True)
    ord_id = db.Column(db.String(10), db.ForeignKey('order.ord_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.pid'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', backref='order_details')

    def __repr__(self):
        return f"<OrderDetail {self.order_det_id}>"
    




