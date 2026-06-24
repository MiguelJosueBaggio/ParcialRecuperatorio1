from typing import Generator
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

## 
def create_db_and_tables(): 
    SQLModel.metadata.create_all(engine) 


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
