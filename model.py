from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel, EmailStr

# SQLAlchemy model for database
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class CustomerRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class CustomersLogin(BaseModel):
    email: EmailStr
    password: str