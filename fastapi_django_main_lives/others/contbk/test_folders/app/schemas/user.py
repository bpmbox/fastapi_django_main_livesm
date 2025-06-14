from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    profile: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    team: str