from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FileResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    total_files: int
    files: list[FileResponse]
