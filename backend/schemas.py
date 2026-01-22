from pydantic import BaseModel, ConfigDict

class ShowDepartment(BaseModel):
    id :int
    nom :str 
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    department_id: int | None = None

class ValidationUpdate(BaseModel):
    status: str
