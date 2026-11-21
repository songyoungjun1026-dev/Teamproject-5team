"""실행 파일: python modules/main.py"""
from book_manager import search_books
from lend_manager import lend_book, show_my_lends, return_book
from reservation_manager import reserve_book, show_my_reservations, cancel_reservation


def main():
    menu = {
        "1": ("도서 검색", search_books),
        "2": ("도서 대출", lend_book),
        "3": ("내 대출 현황", show_my_lends),
        "4": ("도서 반납", return_book),
        "5": ("도서 예약", reserve_book),
        "6": ("내 예약 현황", show_my_reservations),
        "7": ("예약 취소", cancel_reservation),
    }
    while True:
        print("\n===== 도서관 =====")
        for key, (name, _) in menu.items():
            print(f"{key}. {name}")
        print("0. 종료")

        choice = input("선택: ").strip()
        if choice == "0":
            break
        if choice in menu:
            try:
                menu[choice][1]()
            except Exception as e:
              print("오류 종류:", type(e).__name__)
              print("오류 내용:", e)


if __name__ == "__main__":
    main()
