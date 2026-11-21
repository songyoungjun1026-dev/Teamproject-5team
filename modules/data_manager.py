"""공통 데이터 처리: JSON 읽기/쓰기, 검색 도우미 (모든 모듈이 이 파일을 사용)"""
import json
import os

# modules/ 의 상위 폴더 아래 datas/ 를 가리킴
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "datas")

BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
USERS_FILE = os.path.join(DATA_DIR, "user.json")
LENDS_FILE = os.path.join(DATA_DIR, "lend.json")
RESERVES_FILE = os.path.join(DATA_DIR, "reserve.json")


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find(items, key, value):
    """key == value 인 첫 항목 (없으면 None)"""
    for item in items:
        if item[key] == value:
            return item
    return None


def next_id(items, key):
    return max((i[key] for i in items), default=0) + 1
