from flask import Flask
from sqlalchemy import (
    create_engine, 
    Column, 
    Integer, 
    String, 
    Float, 
    Date, 
    ForeignKey, 
    Enum,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import date

#create Flask app instance
app = Flask(__name__)

#Database setup ---------------------------------------------------------------------------------------
engine = create_engine('sqlite:///budget_manager.db') #connect to SQLite database (or create it if it doesn't exist).
Base = declarative_base() #base class for declarative class definitions. define models by inheriting from this base class.
Session = sessionmaker(bind=engine) #session factory, binds to the engine, prepares sessions for database interactions.
session = Session() #create a session to interact with the database.

#Define models -----------------------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(30), nullable=False)
    expenses = relationship("Expense", back_populates="user") #one-to-many relationship with Expense, user.expenses, list of all expenses for the user.
   
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200))
    amount = Column(Float, nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    category = Column(Enum("Food", "Education", "Entertainment", "Other"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id")) #foreign key to link to User
    user = relationship("User", back_populates="expenses") #many-to-one relationship with User, expense.user.username

#Create tables in the database
Base.metadata.create_all(engine)

#ensures the the server runs only when script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
