from sqlalchemy import (
    Column, String, Text, Enum, DateTime, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import enum
import uuid

Base = declarative_base()

class LLMCallType(enum.Enum):
    COMPLETION = "completion"
    TOOL = "tool"


class Agent(Base):
    __tablename__ = 'agents'

    name = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class LLMCall(Base):
    __tablename__ = 'llm_calls'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String, ForeignKey('agents.name'), nullable=False)
    type = Column(Enum(LLMCallType), nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    trace_url = Column(String, nullable=True)
