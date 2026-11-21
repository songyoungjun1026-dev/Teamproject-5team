"""도서 검색 (담당: 김민재)"""
from data_manager import load, BOOKS_FILE


def search_books():
    keyword = input("검색어(제목/저자/출판사): ").strip().lower()
    books = load(BOOKS_FILE)

    result = []

    for b in books:
        title = str(b.get("title", "")).lower()
        writer = str(b.get("writer", "")).lower()
        publisher = str(b.get("publisher", "")).lower()

        if keyword in title or keyword in writer or keyword in publisher:
            result.append(b)

    if not result:
        print("검색 결과가 없습니다.")
        return

    for b in result:
        print(f"[{b['book_id']}] {b['title']} / {b['writer']} / {b['publisher']}")