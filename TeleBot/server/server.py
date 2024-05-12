from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from TeleBot.models.request_model import RequestData, RequestUpdate
from TeleBot.models.request import UserModel
from TeleBot.models.sqlite_conn import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
import aiosqlite
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uvicorn
import codecs

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настроить обслуживание статических файлов из папки "static" внутри вашего проекта
app.mount("/static", StaticFiles(directory="static"), name="static")


async def get_db_connection():
    db_connection = await aiosqlite.connect('TeleBot/data/data.db')
    return db_connection


@app.get('/main', response_class=HTMLResponse)
async def update_status():
    with codecs.open("index.html", 'r', encoding='utf-8') as f:
        html = f.read()
    return HTMLResponse(content=html)


@app.get('/data', response_model=List[RequestData])
async def read_data(db: Session = Depends(get_db)):
    users = db.query(UserModel).order_by(desc(UserModel.dataCreate)).limit(1000)
    return users


@app.post('/update_status')
async def update_status(request: RequestUpdate, db: Session = Depends(get_db)):
    old_request = db.query(UserModel).filter(
        UserModel.dataCreate == request.dataCreate,
        UserModel.user_id == request.user_id,
        UserModel.name == request.name,
    ).first()

    if old_request:
        old_request.status = request.status
        db.commit()
        db.close()
        return {"message": "Status updated successfully"}
    return {"message": "User not found"}


@app.get('/last_data', response_model=List[RequestData])
async def last_data(lastDataCreate: int, db: Session = Depends(get_db)):
    users = db.query(UserModel).filter(
        UserModel.dataCreate > lastDataCreate
    ).order_by(desc(UserModel.dataCreate)).all()
    return users

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8001)
