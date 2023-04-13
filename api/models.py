from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
    last_login = Column(TIMESTAMP)
    token = Column(String(255))
    signed_files = relationship("SignedFile", back_populates="user")

class SignedFile(Base):
    __tablename__ = 'signed_files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
    user = relationship("User", back_populates="signed_files")