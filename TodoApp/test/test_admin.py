from .utils import *
from ..routers.admin import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_todos_authenticated(test_todo):
    response = client.get('admin/todo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Learn to code',
                                'description': 'need to learn every day',
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1,
                                'id': 1}]


def test_admin_delete_todo(test_todo):
    response = client.delete('/admin/delete_todo/1')
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete('/admin/delete_todo/1123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}


def test_admin_read_all_users(test_user):
    response = client.get('admin/auth')
    assert response.status_code == status.HTTP_200_OK


def test_admin_delete_user(test_user):
    response = client.delete('/admin/delete_user/1')
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_user_not_found(test_user):
    response = client.delete('/admin/delete_user/1123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}
