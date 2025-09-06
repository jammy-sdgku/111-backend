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

#get user by id route -------------------------------------------------------------------------------
@app.get("/api/users/<user_id>")#route to get user details by user_id
def get_user(user_id):#function to handle getting user details
    user = session.query(User).filter_by(id=user_id).first()#query to find user by id
    if not user:
        return jsonify({"error":"User not found"}), 404
    
    user_data = { #prepare user data to return
        "id": user.id,
        "username": user.username}
    return jsonify(user_data), 200

#update a user route -------------------------------------------------------------------------------
@app.put("/api/users/<user_id>")#route to update user details by user_id
def update_user(user_id):#function to handle updating user details
    data=request.get_json()#get JSON data from the request
    new_username=data.get("username")#get new username from request data
    new_password=data.get("password")#get new password from request data
    user=session.query(User).filter_by(id=user_id).first()#query to find user by id
    if not user:
        return jsonify({"error":"User not found"}), 404
    if new_username:
        user.username=new_username#update username if provided
    if new_password:
        user.password=new_password#update password if provided
    session.commit()#commit the session to save changes to the database
    return jsonify({"message":"User updated successfully - OK"}), 200

#delete a user route -------------------------------------------------------------------------------
@app.delete("/api/users/<user_id>")#route to delete user by user_id
def delete_user(user_id):#function to handle deleting user
    user=session.query(User).filter_by(id=user_id).first()#query to find user by id
    if not user:
        return jsonify({"error":"User not found"}), 404
    session.delete(user)#delete user from the session
    session.commit()#commit the session to save changes to the database
    return jsonify({"message":"User deleted successfully - OK"}), 200

#expense routes 

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
    allowed_categories = ["Food", "Auto", "Education", "Entertainment", "Other"]
    if category not in allowed_categories:
        return jsonify({"error": "Invalid category"}), 400
    if not title or not amount or not category or not user_id:
        return jsonify({"error": "Title, amount, category, and user_id are required"}), 400
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


#expense retrieval route ----------------------------------------------------------------------------
@app.get("/api/expenses/<user_id>")#route to get all expenses for a user by user_id
def get_expenses(user_id):#function to handle getting expenses for a user
    expenses=session.query(Expense).filter_by(user_id=user_id).all()#query to find all expenses for the user
    if not expenses:
        return jsonify({"error":"No expenses found for this user"}), 404   
    expenses_data=[]#list to hold expense data
    for expense in expenses:#iterate over expenses and prepare data to return
        expenses_data.append({
            "id": expense.id,
            "title": expense.title,
            "description": expense.description,
            "amount": expense.amount,
            "date": expense.date.isoformat(), #convert date to ISO format string
            "category": expense.category
        })
    return jsonify(expenses_data), 200

#expense update route --------------------------------------------------------------------------------
@app.put("/api/expenses/<expense_id>")#route to update an expense by expense_id
def update_expense(expense_id):#function to handle updating an expense
    data=request.get_json()#get JSON data from the request
    expense=session.query(Expense).filter_by(id=expense_id).first()#query to find expense by id
    if not expense:
        return jsonify({"error":"Expense not found"}), 404
    title=data.get("title")#get new title from request data
    description=data.get("description")#get new description from request data
    amount=data.get("amount")#get new amount from request data
    category=data.get("category")#get new category from request data
    allowed_categories=["Food", "Auto", "Education", "Entertainment", "Other"]
    if category and category not in allowed_categories:
        return jsonify({"error":"Invalid category"}), 400
    if title:
        expense.title=title#update title if provided
    if description:
        expense.description=description#update description if provided
    if amount:
        expense.amount=float(amount)#update amount if provided, convert to float
    if category:
        expense.category=category#update category if provided
    session.commit()#commit the session to save changes to the database
    return jsonify({"message":"Expense updated successfully - OK"}), 200

#expense deletion route ------------------------------------------------------------------------------
@app.delete("/api/expenses/<expense_id>")#route to delete an expense by expense_id
def delete_expense(expense_id):#function to handle deleting an expense
    expense=session.query(Expense).filter_by(id=expense_id).first()#query to find expense by id
    if not expense:
        return jsonify({"error":"Expense not found"}), 404
    session.delete(expense)#delete expense from the session
    session.commit()#commit the session to save changes to the database
    return jsonify({"message":"Expense deleted successfully - OK"}), 200

#ensures the the server runs only when script is executed directly ------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
