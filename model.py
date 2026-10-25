from database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__= "users"
    id: Mapped[int]= mapped_column(primary_key= True, index= True)
    username: Mapped[str]= mapped_column(String(50), unique= True)
    password_hash: Mapped[str]= mapped_column(nullable= False)
    role: Mapped[str]= mapped_column(
        default= "user",
        nullable= False
    )
class RevokedToken(Base):
    __tablename__= "revokedtokens"
    id: Mapped[int]= mapped_column(primary_key= True)
    token: Mapped[str]= mapped_column(
        unique= True
    )    

     
