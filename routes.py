from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from model import Customer , CustomerRegister,CustomersLogin
# from config import settings
import bcrypt

router = APIRouter()

@router.post("/customers", response_model=dict)
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    user = Customer(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": Customer.id, "name": Customer.name, "email": Customer.email}

@router.get("/customers", response_model=list)
def get_users(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@router.put("/customers/{customers_id}", response_model=dict)
def update_user(customers_id: int, name: str, email: str, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.id == customers_id).first()
    if not Customer:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = name
    user.email = email
    db.commit()
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/register/")
async def register_user(user: CustomerRegister, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    """
    # Check if the email already exists in the database
    existing_user = db.query(Customer).filter(Customer.email == Customer.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Hash the password
    hashed_password = bcrypt.hashpw(Customer.password.encode('utf-8'), bcrypt.gensalt())

    # Create new user and save to database
    new_user = Customer(name=Customer.username, email=Customer.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully.", "user_id": new_user.id}

@router.post("/login/")
async def login_user(user: CustomersLogin, db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user.
    """
    # Fetch user from database
    stored_user = db.query(Customer).filter(Customer.email == Customer.email).first()
    if not stored_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Verify password
    if bcrypt.checkpw(Customer.password.encode('utf-8'), stored_user.hashed_password.encode('utf-8')):
        return {"message": f"Welcome back, {stored_user.name}!"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password.")