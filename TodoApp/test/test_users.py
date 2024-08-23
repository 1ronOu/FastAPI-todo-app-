from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user(test_user):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'IronOu'
    assert response.json()['email'] == 'ironou7@gmail.com'
    assert response.json()['first_name'] == 'qwe'
    assert response.json()['last_name'] == 'wwq'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '11111111111111'


def test_change_password_success(test_user):
    response = client.put('/user/password', json={'password': 'testpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_fail(test_user):
    response = client.put('/user/password', json={'password': 'wrong_password', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}


def test_change_phone_number(test_user):
    response = client.put('/user/phone_number', params={'new_phone_number': '22222222222'})
    assert response.status_code == status.HTTP_204_NO_CONTENT

