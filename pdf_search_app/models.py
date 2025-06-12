from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

# This sets up the base class all your models will inherit from
Base = declarative_base()

# Define the Contract table structure
class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    artist_name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    keywords = Column(String, nullable=True)
    preview = Column(Text, nullable=True)

# This is just for testing or creating the database manually
if __name__ == "__main__":
    engine = create_engine('sqlite:///contracts.db')
    Base.metadata.create_all(engine)
    print("Database and table created!")
