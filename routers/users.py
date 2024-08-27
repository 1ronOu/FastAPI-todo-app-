import sys
from starlette.responses import RedirectResponse
from starlette import status
sys.path.append("..")
from fastapi import Depends, APIRouter, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_password_hash
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/user",
    tags=["suer"],
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory='templates')

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def verify_password(plain_password, current_hashed_password):
    return pwd_context.verify(plain_password, current_hashed_password)



@router.get('/change_password/{user_id}')
async def password_change(request: Request):
    return templates.TemplateResponse('UI.html', {'request': request})


@router.post('/change_password/{user_id}', response_class=HTMLResponse)
async def change_password(user_id: int, request: Request, db: Session = Depends(get_db),
                          current_password: str = Form(...), new_password: str = Form(...)):

    hashed_current_password = get_password_hash(current_password)
    hashed_new_password = get_password_hash(new_password)
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if not verify_password(current_password, user_model.hashed_password) or current_password == new_password:
        msg = 'Invalid password or passwords are similar'
        return templates.TemplateResponse('UI.html', {'request': request, 'msg': msg})

    user_model.hashed_password = hashed_new_password

    db.add(user_model)
    db.commit()

    msg = 'Password successfully changed'
    return templates.TemplateResponse('login.html', {'request': request, 'msg': msg})
