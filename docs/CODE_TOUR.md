# Hướng dẫn vừa xem vừa học code

Tài liệu này giúp bạn mở VS Code và đọc chương trình theo đúng luồng chạy của app.
Trong code, mình đã thêm comment tiếng Việt ở các file chính để bạn vừa xem app vừa hiểu từng phần.

## 1. Điểm khởi động app

File: `app/main.py`

- Tạo ứng dụng FastAPI.
- Gắn route API và route web.
- Khi app khởi động, nạp dữ liệu theo thứ tự:
  - Google Sheet online.
  - Snapshot local trong `data/local`.
  - Dữ liệu mẫu trong code.

## 2. API backend

File: `app/api/routes.py`

- `/api/sync`: đồng bộ dữ liệu.
- `/api/lessons`: lấy danh sách bài/nhóm.
- `/api/study/vocabulary`: lấy thẻ học từ vựng cho module học từ.
- `/api/radicals`: lấy kiến thức bộ thủ.
- `/api/grammar`: lấy điểm ngữ pháp theo bài.
- `/api/games/{game_type}/question`: tạo câu hỏi game.

## 3. Kho dữ liệu trong bộ nhớ

File: `app/database/repository.py`

- Lưu words, sentences, lessons, grammar, radicals sau khi đọc dữ liệu.
- Quy định phạm vi học: bài N được dùng từ bài 1 đến bài N.
- Lọc câu game để câu không dùng từ vượt quá bài cho phép.

## 4. Dữ liệu từ Google Sheet / snapshot

File: `app/data_sources/local_snapshot.py`

- Đọc các file `data/local/*.tsv`.
- Parse words, sentences, grammar, radicals, lessons, topics.
- Tự bổ sung bài học nếu tab `lessons` thiếu nhóm nhưng tab `từ vựng` có nhóm đó.

File: `app/data_sources/google_sheets/parser.py`

- Chuyển dữ liệu dạng hàng/cột trong Sheet thành object Python.
- Ví dụ: một dòng trong tab `từ vựng` thành `Word`.

## 5. Module học từ vựng

File: `app/vocabulary/study_service.py`

- Tìm bộ thủ liên quan đến từ.
- Tìm câu ví dụ liên quan đến từ.
- Tạo `study card` gồm `word`, `radicals`, `sentences`.

## 6. Module bộ thủ

File chính: `app/web/static/js/app.js`

- `loadRadicals()`: gọi API lấy danh sách bộ thủ.
- `renderRadicalList()`: vẽ danh sách bộ thủ.
- `renderRadicalDetail()`: vẽ chi tiết một bộ thủ.
- `selectRadical()`: chọn bộ thủ và tô active.

## 7. Module ngữ pháp

File chính: `app/web/static/js/app.js`

- `loadGrammar()`: gọi API lấy ngữ pháp theo bài đang chọn.
- `renderGrammarList()`: vẽ danh sách điểm ngữ pháp.
- `renderGrammarDetail()`: vẽ công thức, giải thích, ví dụ và tags.
- `selectGrammar()`: chọn điểm ngữ pháp và tô active.

## 8. Module game

File: `app/games/registry.py`

- Khai báo danh sách game.
- Khai báo nhãn tiếng Việt và mô tả cho giao diện.
- Điều phối game sang engine phù hợp.

File: `app/games/engine.py`

- Tạo câu hỏi game từ vựng.
- Tạo game sắp xếp câu.
- Tạo game điền từ vào câu.

## 9. Người học và tiến độ

File backend: `app/users/progress_store.py`

- Dùng SQLite ở `data/users.sqlite3`.
- Tự tạo 10 hồ sơ mặc định: `Người học 1` đến `Người học 10`.
- Lưu tiến độ riêng cho từng người học.

File API: `app/api/routes.py`

- `/api/users`: lấy danh sách người học.
- `/api/users/{user_id}/progress`: lấy/lưu tiến độ.
- `/api/users/{user_id}/progress/reset`: xóa tiến độ của một người.

File frontend: `app/web/static/js/app.js`

- `loadUsers()`: tải danh sách người học.
- `loadProgressForUser()`: tải tiến độ theo người học đang chọn.
- `saveProgressToServer()`: lưu tiến độ vào SQLite backend.
- `recordStudiedWord()`: cộng từ đã xem khi mở chi tiết từ vựng.
- `recordGameAnswer()`: cộng câu đã làm, đúng hoặc sai.
- `renderProgress()`: cập nhật các ô thống kê trên giao diện.

Hiện tại chưa có mật khẩu/đăng nhập thật. Cách này phù hợp cho lớp nhỏ khoảng chục người
dùng chung một app. Sau này có thể nâng lên tài khoản + mật khẩu.

## 10. Giao diện frontend

File: `app/web/templates/home.html`

- Khung HTML của trang web.
- Có 4 module chính: `Học từ vựng`, `Bộ thủ`, `Ngữ pháp`, `Game luyện tập`.

File: `app/web/static/js/app.js`

- Gọi API backend.
- Hiện danh sách từ.
- Hiện chi tiết từ.
- Xử lý nút nghe/phát âm.
- Xử lý chuyển bài/chuyển module.
- Xử lý chọn đáp án game.
- Xử lý danh sách/chi tiết ngữ pháp.
- Xử lý tiến độ học theo người dùng qua API/SQLite.

File: `app/web/static/css/app.css`

- Kiểu hiển thị giao diện.
- Chia cột bài học, danh sách, chi tiết.
- Responsive cho mobile.

## 11. Test

File: `tests/test_study_module.py`

- Test nối bộ thủ với từ vựng.
- Test lấy câu ví dụ theo từ.
- Test cấu trúc study card.
- Test lọc từ theo bài.

File: `tests/test_game_module.py`

- Test tạo câu hỏi game.
- Test game pinyin không chọn đáp án cùng cách đọc khi cần.
- Test game câu.

Lệnh chạy test:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```
