from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource: Mapped[str] = mapped_column(unique=True)  # Virtual path to the resource
    file_path: Mapped[str] = mapped_column(
        unique=True
    )  # Location of the file on the server

    def __repr__(self):
        return f"File(id={self.id!r}, resource={self.resource!r}, file_path={self.file_path!r})"
