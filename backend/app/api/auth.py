from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os
import xml.etree.ElementTree as ET
import bcrypt
from pathlib import Path

router = APIRouter()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    role: str

class UserInDB(User):
    hashed_password: str

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # In production, use os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# XML path - relative to project root
XML_PATH = Path("storage/users.xml")

# Create the users.xml file if it doesn't exist
def init_user_xml():
    if not XML_PATH.exists():
        # Ensure directory exists
        XML_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Create root XML structure
        root = ET.Element("users")
        
        # Add default admin user
        user = ET.SubElement(root, "user")
        ET.SubElement(user, "username").text = "admin"
        # Password: admin123
        ET.SubElement(user, "password").text = "$2b$12$LN3g6.GkmspVcN9aUXj8T.6MYVVHbJs3UPad2RcHgbPshmWgZ5OEK"
        ET.SubElement(user, "role").text = "admin"
        
        # Write to file
        tree = ET.ElementTree(root)
        tree.write(XML_PATH, encoding="utf-8", xml_declaration=True)

# Initialize the OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User authentication functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user(username: str):
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        
        for user_elem in root.findall("user"):
            if user_elem.find("username").text == username:
                return UserInDB(
                    username=username,
                    hashed_password=user_elem.find("password").text,
                    role=user_elem.find("role").text
                )
    except (FileNotFoundError, ET.ParseError):
        init_user_xml()  # Create the file if it doesn't exist
    
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

# Endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Initialize the XML file when the module is imported
init_user_xml()