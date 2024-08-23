from typing import Annotated
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    tags=['todo']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    complete: bool


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: Annotated[int, Path(ge=1)], user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')


@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()


@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_id: Annotated[int, Path(ge=1)], todo_request: TodoRequest,
                      user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: Annotated[int, Path(ge=1)], user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    db.delete(todo_model)
    db.commit()
