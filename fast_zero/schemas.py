from pydantic import BaseModel, EmailStr
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

class Message(BaseModel):  # 🔹 Aqui está o que faltava
    message: str

class UserDB(UserSchema):
    id: int

class UserList(BaseModel):
    users: list[UserPublic]