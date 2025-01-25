from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError

class Base(DeclarativeBase):
    pass

class Operation(Base): # -> (READ, resource)
    __tablename__ = "operations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    resource: Mapped[str] = mapped_column()
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(back_populates="operations")
    
    def __repr__(self):
        return f"Operation(resource={self.resource!r})"
    
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(back_populates="users")
    
    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, role_id={self.role_id!r})"

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    
    operations: Mapped[List[Operation]] = relationship()
    users: Mapped[List[User]] = relationship()
    
    def __repr__(self):
        return f"Role(id={self.id!r}, name={self.name!r})"
    
    
################ Initialize db ############################


def initialize_database(db: SQLAlchemy):
    try:
        db.create_all()
        
        role1 = Role(name="R1")
        
        role2 = Role(name="R2")
        role2_fabio1 = Operation(resource="fabio1", role=role2)
        role2_fabio2 = Operation(resource="fabio2", role=role2)
        
        role3 = Role(name="R3")
        role3_fabio1 = Operation(resource="fabio1", role=role3)
        role3_fabio2 = Operation(resource="fabio2", role=role3)
        role3_fabio3 = Operation(resource="fabio3", role=role3)
        
        user1 = User(username="alice", role=role2)
        user2 = User(username="bob", role=role3)
        user3 = User(username="charlie", role=role1)

        db.session.add_all([
            role1,
            role2, role2_fabio1, role2_fabio2,
            role3, role3_fabio1, role3_fabio2, role3_fabio3,
            user1, user2, user3
        ])
        
        db.session.commit()
    except IntegrityError:
        return
