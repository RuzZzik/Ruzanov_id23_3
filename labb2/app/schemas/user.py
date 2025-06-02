from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    token: str

    class Config:
        orm_mode = True

class UserMe(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True 