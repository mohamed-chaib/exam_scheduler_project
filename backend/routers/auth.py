from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserLogin, Token
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Secret key (hardcoded for now, should be env var)
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
def login(request: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
        
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "dept_id": user.department_id})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "department_id": user.department_id
    }
