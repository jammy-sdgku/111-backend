from flask import Flask, jsonify, request
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

#Health check route -----------------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

#user creation route (for testing purposes) -------------------------------------------------------
@app.post("/api/create_user")
def create_user():
   data=request.get_json()
   username=data.get("username")#get username from request data
   password=data.get("password")#get password from request data
   
   #validation checks
   existing_user=session.query(User).filter_by(username=username).first()#check if user already exists
   if existing_user:
       return jsonify({"error":"Username already exists"}), 400
   if not username or not password:
       return jsonify({"error":"Username and password are required"}), 400
   
   print(data)
   new_user=User(username=username,password=password)#create new User instance
   session.add(new_user)#add new user to the session
   session.commit()#commit the session to save the user to the database
   
   return jsonify({"message":"User registered successfully- OK"}), 201

#login route (for testing purposes) ----------------------------------------------------------------
@app.post("/api/login")
def login():
    data=request.get_json()
    username=data.get("username")#get username from request data
    password=data.get("password")#get password from request data
   
    if username is None or password is None:
        return jsonify({"error":"Username and password are required"}), 400
    
    user=session.query(User).filter_by(username=username,password=password).first()#query to find user with matching username and password
    if user and user.password==password:   #check if user exists and password matches
        return jsonify({"message":"Login successful - OK","user_id":user.id}), 200
    else:
        return jsonify({"error":"Invalid username or password"}), 401
    
#expense creation route ------------------------------------------------------------------------------
@app.post("/api/create_expense")#route to create a new expense
def create_expense():#function to handle expense creation
    data = request.get_json()#get JSON data from the request
    title = data.get("title")#get title from request data
    description = data.get("description")#get description from request data
    amount = data.get("amount")#get amount from request data
    category = data.get("category")#get category from request data
    user_id = data.get("user_id")  # In a real app, this would come from the authenticated user context
    print(data)
    new_expense = Expense( #create new Expense instance
        title=title,
        description=description,
        amount=float(amount), #convert amount to float
        category=category,
        user_id=user_id
    )
    session.add(new_expense) #add new expense to the session
    session.commit() #commit the session to save the expense to the database
    
    return jsonify({"message":"Expense successfully added - OK"}), 201

#ensures the the server runs only when script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
