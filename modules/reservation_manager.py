
"""예약 및 중복 방지 처리 (담당: 윤완)

[규칙]
1. 같은 책을 이미 대출 중이면 다시 대출/예약할 수 없다.
2. 같은 책을 중복 예약할 수 없다.
3. 재고가 있으면 예약할 수 없다. (바로 대출)
4. 예약자가 있는 책은 예약 순서대로 먼저 대출할 수 있다.
"""

from datetime import date

from data_manager import (
    load, save, find,
    BOOKS_FILE, LENDS_FILE, RESERVES_FILE
)
from user_manager import get_user


# ==================== 예약번호 생성 ====================

def next_reserve_id(reserves):
    """r001, r002, r003 형식의 예약번호 생성"""
    numbers = []

    for r in reserves:
        reserve_id = str(r.get("reserve_id", ""))

        if reserve_id.startswith("r") and reserve_id[1:].isdigit():
            numbers.append(int(reserve_id[1:]))

    next_num = max(numbers, default=0) + 1
    return f"r{next_num:03d}"


# ==================== 다른 모듈이 사용하는 함수 ====================

def is_borrowing(user_id, book_id):
    """이 유저가 이 책을 대출 중인가?"""
    for l in load(LENDS_FILE):
        if (
            l["user_id"] == user_id
            and l["book_id"] == book_id
            and l["state"] == "대출중"
        ):
            return True

    return False


def waiting_list(book_id):
    """해당 도서의 예약중 목록 (예약 순서대로)"""
    return [
        r for r in load(RESERVES_FILE)
        if r["book_id"] == book_id and r["state"] == "예약중"
    ]


def can_lend(book, user_id):
    """대출 가능 여부 확인"""

    book_id = book["book_id"]

    # 이미 대출 중인지 확인
    if is_borrowing(user_id, book_id):
        return False, "이미 대출 중인 도서입니다."

    # 재고 확인
    available = book.get("available_quantity", 0)

    if available <= 0:
        return False, "대출 가능한 재고가 없습니다. 예약 메뉴를 이용해 주세요."

    # 예약 순서 확인
    queue = [r["user_id"] for r in waiting_list(book_id)]

    if user_id in queue:
        if queue.index(user_id) < available:
            return True, ""

        return False, "앞 순번 예약자가 먼저 대출할 수 있습니다."

    # 예약자에게 돌아갈 재고를 제외하고 대출 가능 여부 확인
    if available > len(queue):
        return True, ""

    return False, "예약자가 우선 대출 대기 중인 도서입니다."


def mark_lent(user_id, book_id):
    """대출 성공 시 해당 유저의 예약을 대출완료로 변경"""

    reserves = load(RESERVES_FILE)

    for r in reserves:
        if (
            r["user_id"] == user_id
            and r["book_id"] == book_id
            and r["state"] == "예약중"
        ):
            r["state"] = "대출완료"

    save(RESERVES_FILE, reserves)


def notify_next(book_id):
    """반납 후 다음 예약자 안내"""

    queue = waiting_list(book_id)

    if queue:
        print(
            f"[알림] 예약자 {queue[0]['user_id']}님이 "
            "먼저 대출할 수 있습니다."
        )


# ==================== 4번. 도서 예약 ====================

def reserve_book():
    books = load(BOOKS_FILE)
    reserves = load(RESERVES_FILE)

    user_id = input("유저 아이디: ").strip()

    # 유저 존재 여부
    if not get_user(user_id):
        print("없는 유저입니다.")
        return

    # 문자열 도서번호 입력 (b001)
    book_id = input("예약할 도서번호 (예: b001): ").strip()

    book = find(books, "book_id", book_id)

    # 도서 존재 여부
    if book is None:
        print("존재하지 않는 도서입니다.")
        return

    # 이미 대출 중인지 확인
    if is_borrowing(user_id, book_id):
        print("이미 대출 중인 도서는 예약할 수 없습니다.")
        return

    # 재고가 있으면 예약 불가
    if book.get("available_quantity", 0) > 0:
        print("재고가 있어 바로 대출할 수 있습니다.")
        return

    # 이미 예약했는지 확인
    queue = waiting_list(book_id)

    if user_id in [r["user_id"] for r in queue]:
        print("이미 예약한 도서입니다.")
        return

    # 예약 등록
    reserves.append({
        "reserve_id": next_reserve_id(reserves),
        "book_id": book_id,
        "user_id": user_id,
        "reserve_date": str(date.today()),
        "state": "예약중",
    })

    save(RESERVES_FILE, reserves)

    # 예약 순번 표시
    new_queue = waiting_list(book_id)

    print(f"예약 완료! 대기 순번: {len(new_queue)}번")


# ==================== 5번. 내 예약 조회 ====================

def show_my_reservations():
    books = load(BOOKS_FILE)
    reserves = load(RESERVES_FILE)

    user_id = input("유저 아이디: ").strip()

    # 유저 존재 여부 확인
    if not get_user(user_id):
        print("없는 유저입니다.")
        return

    found = False

    for r in reserves:
        if r["user_id"] == user_id and r["state"] == "예약중":

            book = find(books, "book_id", r["book_id"])

            title = book["title"] if book else "도서 정보 없음"

            queue = waiting_list(r["book_id"])

            reserve_ids = [w["reserve_id"] for w in queue]

            order = reserve_ids.index(r["reserve_id"]) + 1

            print(
                f"[예약번호 {r['reserve_id']}] "
                f"{title} / 대기 {order}번"
            )

            found = True

    if not found:
        print("예약 중인 도서가 없습니다.")


# ==================== 6번. 예약 취소 ====================

def cancel_reservation():
    books = load(BOOKS_FILE)
    reserves = load(RESERVES_FILE)

    user_id = input("유저 아이디: ").strip()

    # 유저 존재 여부 확인
    if not get_user(user_id):
        print("없는 유저입니다.")
        return

    # 해당 유저의 예약 목록
    mine = [
        r for r in reserves
        if r["user_id"] == user_id and r["state"] == "예약중"
    ]

    if not mine:
        print("예약 중인 도서가 없습니다.")
        return

    # 예약 목록 표시
    for r in mine:
        book = find(books, "book_id", r["book_id"])

        title = book["title"] if book else "도서 정보 없음"

        print(f"[예약번호 {r['reserve_id']}] {title}")

    # 문자열 예약번호 입력 (r001)
    reserve_id = input("취소할 예약번호 (예: r001): ").strip()

    # 본인의 예약에서만 찾기
    target = find(mine, "reserve_id", reserve_id)

    if target is None:
        print("잘못된 예약번호입니다.")
        return

    # 예약 취소
    target["state"] = "취소"

    save(RESERVES_FILE, reserves)

    print("예약이 취소되었습니다.")

