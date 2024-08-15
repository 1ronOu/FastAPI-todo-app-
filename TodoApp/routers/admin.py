from typing import Annotated
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from models import Todos, Users
from database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(Todos).all()


@router.get('/auth', status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(Users).all()


@router.delete('/delete_user/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency, user_id: Annotated[int, Path(ge=1)]):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')

    db.delete(user_model)
    db.commit()


@router.delete('/delete_todo/{todo_id}', status_code=status.HTTP_200_OK)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: Annotated[int, Path(ge=1)]):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    db.delete(todo_model)
    db.commit()
