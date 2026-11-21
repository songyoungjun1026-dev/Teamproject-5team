# Teamproject-5team
도서관리 프로그램(5조)
조원: 김민재, 송영준, 윤완
datas 파일 구성
books.json
book_id: 도서번호
title: 책 제목
writer: 저자
publisher: 출판사 // total_quantity, available_quantity (보유량은 추후 추가)
user.json
user_id: 유저아이디
user_pw: 유저 비밀번호(사용여부 판단 필요)
name: 유저명(사용여부 판단 필요)
lend.json
lend_id: 도서대출번호
book_id: 도서번호
user_id: 유저 아이디
lend_date: 대출 일자
due_date: 반납 예정일
return_date: 반납일
state: 현재상태
