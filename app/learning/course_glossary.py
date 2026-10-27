"""Curated learning glosses; Sino-Vietnamese readings are not modern translations.

Readings checked against ph0ngp/hanviet-pinyin-wordlist (MIT), with traditional
forms for simplified characters. Modern Vietnamese meanings are contextual.
"""
ENTRIES = [
    ('为什么', 'vị thậm ma', 'Tại sao, vì sao. Đây là âm Hán Việt từng chữ, không phải cách nói tiếng Việt thông dụng.'),
    ('什么', 'thậm ma', 'Gì, cái gì; trong 什么时候: khi nào.'),
    ('怎么样', 'chẩm ma dạng', 'Thế nào, ra sao.'),
    ('北京', 'Bắc Kinh', 'Tên thủ đô Trung Quốc.'),
    ('旅游', 'lữ du', 'Đi du lịch.'),
    ('觉得', 'giác đắc', 'Cảm thấy; cho rằng (nêu cảm nhận/ý kiến).'),
    ('时候', 'thời hậu', 'Lúc, thời điểm.'),
    ('天气', 'thiên khí', 'Thời tiết.'),
    ('喜欢', 'hỉ hoan', 'Thích, yêu thích.'),
    ('运动', 'vận động', 'Vận động; trong bài là thể thao.'),
    ('足球', 'túc cầu', 'Bóng đá; 踢足球: đá bóng.'),
    ('下午', 'hạ ngọ', 'Buổi chiều.'),
    ('我们', 'ngã môn', 'Chúng tôi/chúng ta, tùy ngữ cảnh.'),
    ('一起', 'nhất khởi', 'Cùng nhau.'),
    ('明天', 'minh thiên', 'Ngày mai.'),
    ('椅子', 'ỷ tử', 'Cái ghế. 子 ở đây là hậu tố danh từ.'),
    ('回来', 'hồi lai', 'Trở về, quay lại phía người nói.'),
    ('桌子', 'trác tử', 'Cái bàn. 子 ở đây là hậu tố danh từ.'),
    ('下面', 'hạ diện', 'Bên dưới, phía dưới.'),
    ('漂亮', 'phiếu lượng', 'Xinh, đẹp. Âm Hán Việt không phải cách đọc tiếng Trung.'),
    ('眼睛', 'nhãn tình', 'Mắt, đôi mắt.'),
    ('九月', 'cửu nguyệt', 'Tháng chín.'),
    ('六', 'lục', 'Sáu.'),
    ('三', 'tam', 'Ba.'),
    ('月', 'nguyệt', 'Tháng; cũng có nghĩa là mặt trăng.'),
    ('冷', 'lãnh', 'Lạnh.'),
    ('热', 'nhiệt', 'Nóng.'),
    ('买', 'mãi', 'Mua; khác 卖 (mại): bán.'),
    ('新', 'tân', 'Mới.'),
    ('要', 'yếu', 'Muốn; cần, tùy ngữ cảnh.'),
    ('几', 'kỷ', 'Mấy, bao nhiêu; 几个: vài cái/mấy cái.'),
    ('点', 'điểm', 'Giờ trong 三点 (ba giờ); cũng có nghĩa là điểm/chấm.'),
    ('多', 'đa', 'Nhiều; sau số chỉ phần hơn, như 三点多: hơn ba giờ.'),
    ('大', 'đại', 'Lớn; 多大 hỏi tuổi hoặc kích thước.'),
    ('猫', 'miêu', 'Con mèo.'),
    ('毛', 'mao', 'Lông. Nguồn đang viết 我的毛; có thể gõ nhầm 猫, chưa tự sửa.'),
    ('踢', 'thích', 'Đá bằng chân.'),
    ('最', 'tối', 'Nhất (mức độ cao nhất).'),
    ('好', 'hảo', 'Tốt; 好啊: được thôi/đồng ý.'),
    ('我', 'ngã', 'Tôi, mình.'),
    ('你', 'nễ', 'Bạn, cậu.'),
    ('去', 'khứ', 'Đi.'),
    ('不', 'bất', 'Không (phủ định).'),
    ('能', 'năng', 'Có thể, có khả năng.'),
    ('很', 'ngận', 'Rất; đứng trước tính từ cũng có thể chỉ nối chủ ngữ với vị ngữ.'),
    ('是', 'thị', 'Là; 是啊: đúng vậy.'),
    ('有', 'hữu', 'Có.'),
    ('叫', 'khiếu', 'Gọi; tên là.'),
]


def glossary_for(text):
    # Follow sentence order; prefer a whole word over overlapping single characters.
    candidates = sorted((text.index(word), -len(word), word, reading, meaning)
                        for word, reading, meaning in ENTRIES if word in text)
    result, occupied = [], set()
    for start, _, word, reading, meaning in candidates:
        span = set(range(start, start + len(word)))
        if span & occupied:
            continue
        occupied |= span
        result.append({'hanzi': word, 'han_viet': reading, 'meaning_vi': meaning})
    return result
