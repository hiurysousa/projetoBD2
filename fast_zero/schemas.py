from pydantic import BaseModel, ConfigDict, EmailStr
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class Message(BaseModel):  # 🔹 Aqui está o que faltava
    message: str

class UserDB(UserSchema):
    id: int

class UserList(BaseModel):
    users: list[UserPublic]