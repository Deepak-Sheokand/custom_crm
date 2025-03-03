from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
import bcrypt

# Database Configuration
DATABASE_URL = "postgresql://postgres:nada-dev-123@34.32.11.227:5432/custom_crm_dev"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use the new import style and bind the engine in the SessionLocal
Base = declarative_base()

# Reflect existing table
customer_table = Table("customer", Base.metadata, autoload_with=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic Model for Input Validation
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone_no: str | None = None
    password: str | None = None


# Pydantic Model for Response Data
class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_no: str | None = None
    password: str | None = None

    class Config:
        orm_mode = True

class CustomersLogin(BaseModel):
    email: EmailStr
    password: str


# Initialize FastAPI App
app = FastAPI()


#customer_login
@app.post("/register/")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    query = db.execute(customer_table.select().where(customer_table.c.email == customer.email)).fetchone()
    if query:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Insert customer data
    new_customer = {
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone_no,
        "password": customer.password,
    }
    insert_statement = customer_table.insert().values(**new_customer)
    result = db.execute(insert_statement)
    db.commit()

    return {"message": "Customer registered successfully", "customer_id": result.inserted_primary_key[0]}

# All customers data
@app.get("/customers/")
def get_all_customers(db: Session = Depends(get_db)):
    query = db.execute(customer_table.select()).fetchall()

    # Use row._mapping to convert RowProxy to a dictionary
    customers = [dict(row._mapping) for row in query]

    return customers

# Get customer data by ID (excluding password)
@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    # Retrieve customer by id
    db_customer = db.query(customer_table).filter(customer_table.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Return the customer data, excluding the password field
    return db_customer


# Get customer data by email (excluding password)
@app.get("/customers/{customer_email}", response_model=CustomerResponse)
def get_customer(customer_email: EmailStr, db: Session = Depends(get_db)):
    # Retrieve customer by id
    db_customer = db.query(customer_table).filter(customer_table.email == customer_email).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Return the customer data, excluding the password field
    return db_customer

@app.post("/login/")
def login_user(user: CustomersLogin, db: Session = Depends(get_db)):
    stored_user = db.query(customer_table).filter(customer_table.email == user.email).first()
    if not stored_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if bcrypt.checkpw(user.password.encode('utf-8'), stored_user.hashed_password.encode('utf-8')):
        return {"message": f"Welcome back, {stored_user.name}!"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
