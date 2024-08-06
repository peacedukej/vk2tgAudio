from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import core, database

from routers.main_router import router as main_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


app.include_router(
    router=main_router,
    tags=["Главный роутер"], 
    #prefix="/",
)

#database.Base.metadata.create_all(bind=database.engine)

# # Dependency для получения сессии базы данных
# def get_db():
#     db = database.SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.post("/tokens/")
# def create_token(token: core.TokenCreate, db: Session = Depends(get_db)):
#     db_token = core.Token(access_token=token.access_token, user_id=token.user_id)
#     db.add(db_token)
#     db.commit()
#     db.refresh(db_token)
#     return db_token

# @app.get("/tokens/{user_id}")
# def read_token(user_id: int, db: Session = Depends(get_db)):
#     return db.query(core.Token).filter(core.Token.user_id == user_id).first()
