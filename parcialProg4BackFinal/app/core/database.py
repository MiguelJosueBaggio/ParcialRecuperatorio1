import os
from typing import Generator
from sqlmodel import create_engine,SQLModel,Session,create_engine
DATABASE_URL = os.getenv ( 
"DATABASE_URL", 
"postgresql+psycopg://postgres:postgres@localhost:5432/parcial_1" 
) 
engine = create_engine(DATABASE_URL, echo=True)

## 
def create_db_and_tables(): 
    SQLModel.metadata.create_all(engine) 


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
