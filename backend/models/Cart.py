import os
from models.Users import User
from models.MenuCard import MenuCard
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.exc import IntegrityError, NoResultFound, InternalError

DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING')
Base = declarative_base()
engine = create_engine(DB_CONNECTION_STRING)
database = Session(bind=engine)


class Cart(Base):
    __tablename__ = 'cart'
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.uid), nullable=False)
    item_id = Column(Integer, ForeignKey(MenuCard.item_id), nullable=False)
    quantity = Column(Integer, nullable=False)

    def __init__(self, user_id: int, item_id: int = None, quantity: int = None):
        self.user_id = user_id
        self.item_id = item_id
        self.quantity = quantity
        # TODO: Update self.cart after every operation
        self.cart = database.query(Cart).filter_by(user_id=self.user_id)

    def __repr__(self):
        user_id = self.user_id
        item_id = self.item_id
        quantity = self.quantity
        return (
            f"<Cart(user_id={user_id}, item_id={item_id}, quantity={quantity})>"
        )

    def get_cart(self) -> list[dict]:  # To be only used to display item_id, quantity pair
        items = []
        for cart_item in self.cart.all():
            menu_item = database.get(MenuCard, cart_item.item_id)
            items.append(
                {
                    "id": cart_item.item_id,
                    "icon": menu_item.item_icon,
                    "name": menu_item.item_name,
                    "price": menu_item.item_price,
                    "quantity": cart_item.quantity
                }
            )
        return items

    def item_exists(self, item_id: int):
        """Check if an item exists in the database, for that particular user"""
        return self.cart.filter_by(item_id=item_id).first()

    def add_item(self, item: int):
        try:
            existing_item = self.item_exists(item)
            if existing_item:  # If item exists, increment its quantity by 1
                existing_item.quantity += 1
            else:  # Else, append the item to the cart with quantity 1
                self.item_id = item
                self.quantity = 1
                database.add(self)
            database.commit()
            self.cart = database.query(Cart).filter_by(user_id=self.user_id)
        except IntegrityError:  # Occurs when the item is not in the menu
            database.rollback()
            raise Exception("Item does not exist in the menu")
        except InternalError:  # Occurs when item requested is more than in menu
            database.rollback()
            raise Exception("Quantity exceeds available quantity in Menu!")

    def remove_item(self, item: int):
        try:
            # There should be only one and only one item existing in the cart
            existing = self.cart.filter_by(item_id=item).one()
            if existing.quantity > 0:
                existing.quantity -= 1
                database.commit()
                self.cart = database.query(Cart).filter_by(user_id=self.user_id)
            else:  # If the quantity is 0, raise an exception
                raise Exception("No item left to remove")
        except NoResultFound:  # if the item does not exist in the cart
            raise Exception("Item does not exist in the cart")

    def delete_item(self, item: int):
        # TODO: Raise Exception if item does not exist in the cart
        existing = self.cart.filter_by(item_id=item)
        existing.delete()
        database.commit()
        self.cart = database.query(Cart).filter_by(user_id=self.user_id)


Base.metadata.create_all(engine, checkfirst=True)
