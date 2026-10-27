# Học bài khóa — 27/10/2026

## Viết ghi nhớ ngay trong phần Học hiểu

Phần 1 có ô Viết lại để ghi nhớ, nghĩa Việt và âm Hán Việt gợi nhớ theo từ.
Ẩn/hiện chữ Hán che cả khối nội dung nguồn/pinyin/toàn bài để tự nhớ; audio
vẫn dùng được. Kiểm tra bằng nút, chờ kết thúc IME; không ghi điểm hay lượt
trả lời vào phiên luyện. Bản nháp và trạng thái ẩn lưu tại study_recall,
khóa lesson_id:sentence_id, riêng theo người học. Nội dung nguồn đổi revision
thì giữ bản nháp nhưng bỏ kết quả kiểm tra cũ. Câu mới chưa có Hán Việt ghi rõ
chưa có dữ liệu, không tự bịa phiên âm.
Test: tests/course_recall_browser.cjs đạt ẩn/hiện, chấm đúng/sai, chuyển câu,
reload, bảo toàn phiên luyện trước đó, responsive 320/375/390/430/1280px.

## Nhập theo từ/câu

- Phần 2 có tùy chọn Hỗ trợ từng từ/cụm (mặc định tắt). Các ranh giới từ
  của 20 câu hiện tại được biên soạn trong course_tokens.py, không tách theo
  từng chữ một cách máy móc. Câu mới chưa duyệt ranh giới dùng ô nhập cả câu.
- Kiểm tra từng ô tại compositionend hoặc blur, bỏ qua lúc IME còn đang chọn
  chữ. Ô trống không bị báo sai; không hiện đáp án, không cộng lượt/sai vào
  completed_answers. Chỉ nút Kiểm tra đáp án mới ghi kết quả cả câu/bài.
- Bản nháp nhập cả câu và nhập theo từ giữ riêng; khi tắt hỗ trợ trở về bản
  nháp cả câu trước đó. UI ghi rõ quy tắc này.
- Phần 3 vẫn nhập cả câu Việt và cho tự xác nhận diễn đạt tương đương.
- Phần 4 mỗi câu có một textarea, nghĩa tiếng Việt và âm Hán Việt theo từ
  gợi nhớ. Không hiện chữ Hán đáp án trước khi nộp. Ô đang tập trung quyết
  định câu được mở khi bấm Xem lại; resume giữ tất cả ô theo sentence_id.
- Bản nháp toàn bài cũ được giữ trong legacy_rewrite_draft, đồng thời chia
  theo dòng vào ô mới; phần dư giữ ở ô cuối, không âm thầm bỏ dữ liệu.
- State schema vẫn version 1; các trường mới được thêm lazily. Khi dữ liệu
  đổi, phản hồi từng ô bị xóa và token mode tắt để không chấm bằng ranh giới cũ.
- Kiểm thử: 36 Python, 10 state tests; tests/course_inputs_browser.cjs đã
  kiểm tra IME mô phỏng, blur, bật/tắt, lưu từng ô/reload, câu review đúng ID,
  và responsive 320/375/390/430/1280. Chưa thử bàn phím iOS trên máy thật.

## Cập nhật audio và Hán Việt

- Chẩn đoán thực tế: edge-tts 7.2.8 trả HTTP 403 khi gọi dịch vụ; cập nhật 7.3.1
  đã tạo được file âm thanh. requirements pin đúng phiên bản đã thử.
- A: zh-CN-XiaoxiaoNeural (nữ); B: zh-CN-YunxiNeural (nam), Quan thoại zh-CN.
  Tham chiếu giọng: https://learn.microsoft.com/azure/cognitive-services/speech-service/language-support?tabs=tts
- `scripts/build_course_audio.py` tạo MP3 sẵn và manifest trong static/course-audio.
  Không sửa source; chỉ tái dùng file khi text và speaker khớp. Câu mới/sửa dùng
  endpoint TTS với speaker A/B; có thể chạy lại script để đóng gói audio mới.
- Đã kiểm tra 20/20 MP3 giải mã được trong Edge, độ dài 1.872–4.608 giây;
  đã xác nhận A/B phát, thời gian phát tăng và không có lỗi media.
- `app/learning/course_glossary.py` thêm 48 mục từ/chữ liên quan hiện có,
  phân biệt âm Hán Việt và nghĩa hiện đại theo ngữ cảnh. Không tự sinh âm
  Hán Việt cho từ mới chưa biên soạn. Nguồn đối chiếu âm:
  https://github.com/ph0ngp/hanviet-pinyin-wordlist (MIT, giấy phép trong docs/licenses).
  Bản dịch/nghĩa là chú giải biên soạn, không phải thay đổi câu nguồn.
- Test mới: `tests/course_audio_browser.cjs`. Tổng Python tests sau cập nhật: 35/35.
- Chỉ cập nhật bản local; Render chưa deploy. Tải lại trang để nạp JS/API mới.

## Phạm vi

Thêm module Học bài khóa, không thay các game/từ vựng/chữ độc thể hiện có.
4 phần: học và hiểu từng câu/toàn bài; nghe và gõ Hán tự; dịch Việt;
viết lại toàn bộ bài khóa. Dữ liệu gốc và gợi ý từ Sheet được giữ nguyên.

## Dữ liệu

`GET /api/course/lessons` nạp snapshot `data/local/course_lessons.json` (4 bài, 20 câu).
`POST /api/course/refresh` đọc tab `bai khoa` từ Google Sheets công khai,
kiểm tra thiếu/trùng ID, thứ tự; chỉ thay dữ liệu sau khi toàn bộ lô hợp lệ.
Nút **Cập nhật bài khóa từ Sheet** chỉ cập nhật module này, không ghi lên Sheets.
Dữ liệu refresh được kiểm tra rồi lưu file bằng atomic replace trước khi cập nhật cache.
Khởi động lại đọc file đã lưu. `COURSE_DATA_PATH` có thể trỏ tới file trên persistent disk;
mặc định là `data/local/course_lessons.json`. Trên Render phải gắn persistent disk và đặt
biến này để giữ dữ liệu qua redeploy/thay instance. Sheet rỗng hoặc lỗi ghi giữ dữ liệu cũ.

Sửa lỗi được người dùng duyệt: BK04-C02 `那是我的毛，他叫花花` → `那是我的猫，他叫花花`,
máo → māo, lông → con mèo; cập nhật gợi ý và audio tương ứng. Không sửa Sheet từ app.
Khi refresh gặp đúng ID và câu cũ, áp dụng sửa này và lưu `source_hanzi` để đối chiếu.
Nút Xóa tiến độ có xác nhận, xóa cả bản nháp/phiên bài khóa của người học hiện tại;
không xóa dữ liệu bài hoặc tiến độ của người khác.
Muốn giữ nội dung mới sau redeploy cần cập nhật snapshot trong repository.

Tên ảnh trong `image_refs` ánh xạ `/static/course-images/<tên file>`;
link HTTPS được giữ nguyên. Khi để trống, dùng ảnh chung `<lesson_id>.jpg` nếu có.
Đã copy 4 ảnh BK01–BK04 do người dùng cung cấp, không tạo ảnh mới.
File audio HTTPS hoặc tên file được ưu tiên; khi trống dùng `/api/tts` hiện có
(giọng Quan thoại Xiaoxiao). Link chia sẻ OneDrive/Drive không được tự chuyển
thành link ảnh trực tiếp. Tên file mới cần được đưa vào thư mục static khi deploy.

## Trạng thái

`localStorage[chinese-course-v1:<user_id>]`, version=1.
Mỗi phiên riêng theo `lesson_id:practice_section`: lesson_id, practice_section,
segment_id (mã bài cho phần viết toàn bài), sentence_id, question_index,
draft_answer, completed_answers, grading_state, revision, sentence_revisions,
finished và archived. `return_target` ở trạng thái điều hướng gốc.

Lưu đồng bộ theo sự kiện input và thao tác điều hướng. Xem lại không gọi chấm điểm,
không chuyển câu và không ghi thêm kết quả. Resume dùng ID phiên cũ,
không dùng câu đang được xem trong phần học. Đổi bài khi đang xem lại giữ nút
quay về phiên cũ. Đổi phần luyện chủ động kết thúc luồng xem lại, nhưng phiên
cũ vẫn được giữ để chọn lại. Đổi người học tách hoàn toàn khóa lưu.

Khi dữ liệu đổi revision hoặc mất câu, hiển thị bản nháp + chọn vị trí hợp lệ;
không tự chuyển bản nháp sang câu khác. Giữ tối đa 10 bản lưu trước phục hồi/luyện lại.
Chỉ giữ kết quả cũ nếu nội dung câu không đổi; phần 4 vô hiệu kết quả toàn bài khi
bài thay đổi. Bài bị xóa vẫn có phiên cũ trong storage và cho chọn bài khác.

## Chấm đáp án

So khớp bỏ dấu câu/khoảng trắng, chuẩn Unicode NFC và chữ hoa/thường.
Không bỏ dấu tiếng Việt, không đổi thứ tự chữ, không gọi AI API.
Phần 3 hiển thị "chưa khớp mẫu", không khẳng định bản dịch khác là sai;
người học có thể tự xác nhận tương đương (đánh dấu self_assessed).
Kết quả bài khóa hiển thị trong module, không cộng vào bộ đếm game chung.

## Kiểm thử

Kết quả chạy: 33/33 Python tests đạt; 8/8 state tests mới đạt và bộ hồi quy
monolithic-game đạt. Playwright/Edge headless đạt toàn bộ luồng bên dưới;
đã xem ảnh mobile 430px và desktop 1280px. Đã sửa xung đột sticky mobile
để thanh chọn module không che nút Tiếp tục khi cuộn.

```
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"
node --test tests/course_state.test.cjs
# Chạy server với SYNC_ON_STARTUP=false ở 127.0.0.1:8765
# NODE_PATH trỏ tới nơi có playwright; cần Edge cài sẵn
node tests/course_browser.cjs
```

Browser test bao phủ bản nháp Hán/Việt/nhiều dòng, xem nhiều câu, đổi bài khi xem lại,
xem lại nhiều lần, đã chấm đáp án, kết quả các câu trước, reload trong review/practice,
khôi phục localStorage trong context mới, đổi revision/thứ tự, xóa câu/bài,
và viewport 320/375/390/430/1280. Kiểm tra scrollWidth=clientWidth, scrollX=0.
Ảnh kiểm thử nằm trong outputs/course-qa (không là tài nguyên app).

## Giới hạn

Tiến độ nằm trên trình duyệt/thiết bị, không đồng bộ giữa điện thoại và máy tính.
Xóa dữ liệu trình duyệt/private mode có thể làm mất tiến độ; storage đầy/bị chặn
hiển thị cảnh báo. Nhiều tab cùng người học chưa có giải quyết xung đột (ghi cuối thắng).
Context mới trong test dùng bản sao storage để mô phỏng mở lại, không phải test
Safari/iPhone vật lý. TTS phụ thuộc mạng/dịch vụ hiện có, không chấm phát âm.
Không đổi ID đã dùng để tránh mất liên kết tiến độ. Lần triển khai này không tự
push/deploy Render; cần deploy các file mới và ảnh cùng ứng dụng.

## File thay đổi

- `app/learning/course.py`: parser, media URL, revision và API đọc/refresh bài khóa.
- `app/main.py`: đăng ký router mới.
- `app/web/templates/home.html`: tab/module 4 phần và nạp JS mới.
- `app/web/static/js/course-state.js`: chuyển trạng thái, chấm mẫu, recovery.
- `app/web/static/js/course.js`: UI, localStorage, review/resume, audio/image.
- `app/web/static/js/app.js`: thông báo đổi người học cho module mới.
- `app/web/static/css/app.css`: bố cục responsive, nút 44px và sticky action.
- `data/local/course_lessons.json`: snapshot 20 câu từ tab bai khoa, không sửa nguồn.
- `app/web/static/course-images/BK01.jpg` đến `BK04.jpg`: ảnh người dùng cung cấp.
- `tests/test_course.py`, `tests/course_state.test.cjs`, `tests/course_browser.cjs`: kiểm thử.
