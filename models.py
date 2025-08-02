from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Vare(Base):
    __tablename__ = "vare"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    succ_description = Column(Text, nullable=False)
    fail_description = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # 관계 설정
    todos = relationship("VareTodo", back_populates="vare", cascade="all, delete-orphan")
    reasons = relationship("VareReason", back_populates="vare", cascade="all, delete-orphan")
    actions = relationship("VareAction", back_populates="vare", cascade="all, delete-orphan")


class VareTodo(Base):
    __tablename__ = "vare_todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vare_id = Column(Integer, ForeignKey("vare.id"), nullable=False)
    todo_text = Column(String(500), nullable=False)
    todo_category = Column(String(100), nullable=False)
    order_seq = Column(SmallInteger, nullable=False, default=1)  # TINYINT 대신 SmallInteger
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    vare = relationship("Vare", back_populates="todos")


class VareReason(Base):
    __tablename__ = "vare_reasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vare_id = Column(Integer, ForeignKey("vare.id"), nullable=False)
    reason_text = Column(Text, nullable=False)
    percent = Column(SmallInteger, nullable=False)  # TINYINT 대신 SmallInteger
    order_seq = Column(SmallInteger, nullable=False, default=1)  # TINYINT 대신 SmallInteger
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    vare = relationship("Vare", back_populates="reasons")


class VareAction(Base):
    __tablename__ = "vare_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vare_id = Column(Integer, ForeignKey("vare.id"), nullable=False)
    action_title = Column(String(255), nullable=False)
    action_desc = Column(Text, nullable=False)
    order_seq = Column(SmallInteger, nullable=False, default=1)  # TINYINT 대신 SmallInteger
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    vare = relationship("Vare", back_populates="actions")