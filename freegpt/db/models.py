from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class LLMCallType(enum.Enum):
    COMPLETION = "completion"
    TOOL = "tool"

class LLMCall(Base):
    __tablename__ = 'llm_call'
    __table_args__ = {'schema': 'freegpt'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(LLMCallType), nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    trace_url = Column(String, nullable=True)

    def __repr__(self):
        return f"<LLMCall(id={self.id}, type={self.type}, trace_url={self.trace_url})>"
