
"""대출 / 반납 (담당: 송영준)"""

from datetime import date, timedelta

from data_manager import load, save, find, BOOKS_FILE, LENDS_FILE
from user_manager import get_user
from reservation_manager import can_lend, mark_lent, notify_next

LOAN_DAYS = 14       # 대출 기간(일)
MAX_LOANS = 3        # 1인 최대 동시 대출 권수


def active_lends(lends, user_id):
    """해당 유저의 대출중 목록"""
    return [
        l for l in lends
        if l["user_id"] == user_id and l["state"] == "대출중"
    ]


def next_lend_id(lends):
    """l001, l002, l003 형식으로 대출번호 생성"""
    numbers = []

    for lend in lends:
        lend_id = str(lend.get("lend_id", ""))

        if lend_id.startswith("l") and lend_id[1:].isdigit():
            numbers.append(int(lend_id[1:]))

    next_num = max(numbers, default=0) + 1
    return f"l{next_num:03d}"


def lend_book():
    """도서 대출"""
    books = load(BOOKS_FILE)
    lends = load(LENDS_FILE)

    # 사용자 확인
    user_id = input("유저 아이디: ").strip()

    if not get_user(user_id):
        print("없는 유저입니다.")
        return

    # 최대 대출 권수 확인
    if len(active_lends(lends, user_id)) >= MAX_LOANS:
        print(f"최대 {MAX_LOANS}권까지만 대출할 수 있습니다.")
        return

    # 도서번호 입력 (b001 형식)
    book_id = input("도서번호 (예: b001): ").strip()

    # 도서 존재 여부 확인
    book = find(books, "book_id", book_id)

    if book is None:
        print("존재하지 않는 도서입니다.")
        return

    # 재고 확인
    if book.get("available_quantity", 0) <= 0:
        print("대출 가능한 재고가 없습니다.")
        return

    # 중복 대출 및 예약 우선순위 확인
    ok, msg = can_lend(book, user_id)

    if not ok:
        print(msg)
        return

    # 대출 날짜 설정
    today = date.today()
    due = today + timedelta(days=LOAN_DAYS)

    # 대출 기록 추가
    lends.append({
        "lend_id": next_lend_id(lends),
        "book_id": book_id,
        "user_id": user_id,
        "lend_date": str(today),
        "due_date": str(due),
        "return_date": None,
        "state": "대출중",
    })

    # 재고 감소
    book["available_quantity"] -= 1

    # 파일 저장
    save(LENDS_FILE, lends)
    save(BOOKS_FILE, books)

    # 예약 상태 갱신
    mark_lent(user_id, book_id)

    print(f"'{book['title']}' 대출 완료!")
    print(f"대출번호: {lends[-1]['lend_id']}")
    print(f"반납 예정일: {due}")


def show_my_lends():
    """내 대출 목록 조회"""
    books = load(BOOKS_FILE)
    lends = load(LENDS_FILE)

    user_id = input("유저 아이디: ").strip()

    if not get_user(user_id):
        print("없는 유저입니다.")
        return

    mine = active_lends(lends, user_id)

    if not mine:
        print("대출 중인 도서가 없습니다.")
        return

    today = str(date.today())

    print("\n===== 내 대출 목록 =====")

    for l in mine:
        book = find(books, "book_id", l["book_id"])

        if book is None:
            title = "도서 정보 없음"
        else:
            title = book["title"]

        late = " (연체!)" if l["due_date"] < today else ""

        print(
            f"[대출번호 {l['lend_id']}] "
            f"{title} / 반납예정 {l['due_date']}{late}"
        )


def return_book():
    """도서 반납"""
    books = load(BOOKS_FILE)
    lends = load(LENDS_FILE)

    user_id = input("유저 아이디: ").strip()

    if not get_user(user_id):
        print("없는 유저입니다.")
        return

    # 해당 유저의 대출 목록
    mine = active_lends(lends, user_id)

    if not mine:
        print("반납할 도서가 없습니다.")
        return

    print("\n===== 반납할 도서 목록 =====")

    for l in mine:
        book = find(books, "book_id", l["book_id"])

        title = book["title"] if book else "도서 정보 없음"

        print(
            f"[대출번호 {l['lend_id']}] "
            f"{title} / 반납예정 {l['due_date']}"
        )

    # 대출번호는 l001 형식이므로 문자열로 입력
    lend_id = input("반납할 대출번호 (예: l001): ").strip()

    # 내 대출 목록에서 해당 대출 찾기
    lend = find(mine, "lend_id", lend_id)

    if lend is None:
        print("잘못된 대출번호입니다.")
        return

    # 도서 정보 확인
    book = find(books, "book_id", lend["book_id"])

    if book is None:
        print("도서 정보를 찾을 수 없습니다.")
        return

    # 반납 처리
    today = date.today()

    lend["return_date"] = str(today)
    lend["state"] = "반납완료"

    # 재고 복구
    book["available_quantity"] += 1

    # 파일 저장
    save(LENDS_FILE, lends)
    save(BOOKS_FILE, books)

    # 연체 여부 확인
    if str(today) > lend["due_date"]:
        print("반납 완료! (반납 예정일이 지나 연체 반납입니다.)")
    else:
        print("반납 완료!")

    print(f"반납 도서: {book['title']}")

    # 예약자가 있는 경우 알림
    notify_next(lend["book_id"])
