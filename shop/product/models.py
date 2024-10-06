from shop.app import db,web
from flask import *
from sqlalchemy import event
from sqlalchemy.orm.relationships import *




class Category(db.Model):
    __tablename__ = 'category'

    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(50), nullable=False)

    
    def __repr__(self):
        return self.cname
    # subcategories = db.relationship('Subcategory', back_populates='category', lazy=True)

class Subcategory(db.Model):
    __tablename__ = 'subcategory'

    sub_id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(50), nullable=False)
    cid = db.Column(db.Integer, db.ForeignKey('category.cid', ondelete='CASCADE'), nullable=False)


    category= db.relationship('Category', backref=db.backref('subcategories', lazy=True))

# Define event listener to delete subcategories when a category is deleted
# @event.listens_for(Category, 'before_delete')
# def delete_subcategories(mapper, connection, target):
#     Subcategory.query.filter_by(cid=target.cid).delete()

class Product(db.Model):
    __tablename__ = 'product'

    pid = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    material = db.Column(db.String(50), nullable=True)
    sleeves = db.Column(db.String(50), nullable=True)
    neck = db.Column(db.String(50), nullable=True)
    cid = db.Column(db.Integer, db.ForeignKey('category.cid'), nullable=False)  # Foreign key for category
    sid = db.Column(db.Integer, db.ForeignKey('size.sid'), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('color.color_id'), nullable=False)  # Foreign key for color
    stock = db.Column(db.Integer, nullable=False)
    image1 = db.Column(db.String(100), nullable=False)
    image2 = db.Column(db.String(100), nullable=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('subcategory.sub_id'), nullable=True)

    category = db.relationship('Category', backref=db.backref('products', lazy=True))  # Relationship with Category
    size = db.relationship('Size', backref=db.backref('products', lazy=True))
    color = db.relationship('Color', backref=db.backref('products', lazy=True))  # Relationship with Color
    subcategories = db.relationship('Subcategory', backref=db.backref('products', lazy=True))



class Size(db.Model):
    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Color(db.Model):
    color_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Gallery(db.Model):
    __tablename__ = 'gallery'

    gallery_id = db.Column(db.Integer, primary_key=True)
    path1 = db.Column(db.String(100))
    path2 = db.Column(db.String(100))
    pid = db.Column(db.Integer, db.ForeignKey('product.pid'))
    product = db.relationship('Product', backref=db.backref('gallery', uselist=False))
    def __repr__(self):
        return f"<Gallery {self.gallery_id}>"
    

    
    
         
with web.app_context():
    db.create_all()