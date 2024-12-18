from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Metadata setup for naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Customer Model
class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reviews = db.relationship('Review', back_populates='customer')
    items = association_proxy('reviews', 'item')  # Adding association proxy for items

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'

    def to_dict(self, include_reviews=True):
        data = {
            'id': self.id,
            'name': self.name,
        }
        if include_reviews:
            data['reviews'] = [review.to_dict(include_customer=False, include_item=False) for review in self.reviews]
        return data


# Item Model
class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    reviews = db.relationship('Review', back_populates='item')

    def __repr__(self):
        return f'<Item {self.id}, {self.name}>'

    def to_dict(self, include_reviews=True):
        data = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
        }
        if include_reviews:
            data['reviews'] = [review.to_dict(include_customer=False, include_item=False) for review in self.reviews]
        return data


# Review Model
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'

    def to_dict(self, include_customer=True, include_item=True):
        data = {
            'id': self.id,
            'comment': self.comment,
        }
        # Serialize customer and item only if needed, avoiding circular references
        if include_customer:
            data['customer'] = self.customer.to_dict(include_reviews=False) if self.customer else None
        if include_item:
            data['item'] = self.item.to_dict(include_reviews=False) if self.item else None
        return data
