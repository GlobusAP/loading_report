from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base


class Node(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    operators: Mapped[list['Operator']] = relationship('Operator', back_populates='node')


class Operator(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_number: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    CIC: Mapped[int] = mapped_column(Integer, nullable=False)
    node_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'), nullable=False)

    node: Mapped['Node'] = relationship('Node', back_populates='operators')
