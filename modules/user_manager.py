"""회원 정보 조회 모듈"""

from data_manager import load, find, USERS_FILE


def get_user(user_id):
    users = load(USERS_FILE)
    return find(users, "user_id", user_id)