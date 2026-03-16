from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = 'postgresql://danis@localhost:5432/chatbot_db'

engine = create_engine(
    DATABASE_URL,
    echo=True,  #  для отладки)
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
