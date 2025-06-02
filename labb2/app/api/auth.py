from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserMe
from app.cruds.user import get_user_by_email, create_user, verify_password
from app.core.security import create_access_token
from app.db.session import get_db
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user.email, user.password)
    token = create_access_token({"sub": new_user.email})
    return UserOut(id=new_user.id, email=new_user.email, token=token)

@router.post("/login/", response_model=UserOut)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token({"sub": db_user.email})
    return UserOut(id=db_user.id, email=db_user.email, token=token)

@router.get("/users/me/", response_model=UserMe)
def get_me(current_user: UserMe = Depends(get_current_user)):
    return current_user 