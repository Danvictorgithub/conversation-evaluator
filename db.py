import os
from sqlalchemy import String, create_engine, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass


class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), default="")
    grammatical_correctness: Mapped[int] = mapped_column(default=0)
    readability: Mapped[int] = mapped_column(default=0)
    descriptiveness: Mapped[int] = mapped_column(default=0)
    coherence: Mapped[int] = mapped_column(default=0)
    conciseness: Mapped[int] = mapped_column(default=0)
    explanation: Mapped[dict] = mapped_column(JSON)  # Use JSON type here


# Create the database engine
engine = create_engine(os.getenv("DATABASE_URL", ""), echo=True)

# Create all tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
