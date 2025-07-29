from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "mysql+pymysql://root:lMDyxrqOlWGIhknuPCIgwRTVPEeacJJI@ballast.proxy.rlwy.net:47753/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("✅ Conexión exitosa a la base de datos MySQL.")
    except SQLAlchemyError as e:
        print("❌ Error al conectar a la base de datos:")
        print(e)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()