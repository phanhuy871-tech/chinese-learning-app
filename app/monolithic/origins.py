"""Only source-checked claims are eligible for publication as etymology."""
VERIFIED = {
    "大": ("Hình người đứng chính diện, có đầu, thân và tứ chi. Hồ sơ có mẫu giáp cốt (合集21022), kim văn (集成01472) và tiểu triện từ Thuyết văn. Cách liên tưởng dang tay để nhớ ‘lớn’ là mẹo học; nguồn này không chứng minh quan hệ nhân quả ‘chiếm nhiều không gian nên có nghĩa lớn’.", "https://chardb.iis.sinica.edu.tw/evolution.jsp?cid=9518", ""),
    "来": ("Dạng cổ của 來 mô phỏng cây lúa mì chín. Chữ được giả tá (mượn chữ để ghi từ) cho nghĩa ‘đến, qua lại’. Vì vậy không được suy nghĩa gốc là ‘đến’ từ cách dùng hiện đại. Hồ sơ trình bày giáp cốt, kim văn và tiểu triện của 來, không phải của dạng giản thể 来.", "https://chardb.iis.sinica.edu.tw/evolution.jsp?cid=7032", "lúa mì"),
    "心": ("Chữ mô phỏng hình trái tim của người hoặc động vật; bản nghĩa là tim. Đây là mô tả được hồ sơ xác nhận, không đủ cơ sở để khẳng định từng nét là một thùy hay mạch máu cụ thể.", "https://chardb.iis.sinica.edu.tw/evolution.jsp?cid=11227", "tim"),
    "牛": ("Hình chữ nhấn mạnh đầu và sừng của con bò; bản nghĩa là con bò. Có các mẫu chữ cổ được liệt kê trong hồ sơ để đối chiếu, không cần bịa câu chuyện cho từng nét hiện đại.", "https://chardb.iis.sinica.edu.tw/evolution.jsp?cid=16024", "bò"),
    "象": ("Giáp cốt và kim văn mô tả hình con voi, đặc biệt nhấn mạnh chiếc vòi dài và cong. Đây là đặc điểm nhận dạng hình thể được nguồn nêu rõ.", "https://chardb.iis.sinica.edu.tw/evolution.jsp?cid=22724", "voi"),
    "及": ("Hình chữ mô tả một bàn tay bắt lấy người ở phía trước, biểu thị đuổi kịp. Hồ sơ có giáp cốt (合集12510), kim văn (集成05415) và tiểu triện từ Thuyết văn.", "https://chardb.iis.sinica.edu.tw/evolution.jsp?cid=8131", "đuổi kịp"),
}

def origin_fields(char):
    entry = VERIFIED.get(char)
    return {
        "origin_story_vi": entry[0] if entry else "Chưa có thuyết minh nguồn gốc được kiểm chứng riêng cho chữ này. Không suy ra nghĩa gốc từ nghĩa hiện đại. Liên kết tra cứu bên dưới chỉ phục vụ đối chiếu, không phải dẫn chứng cho một diễn giải chưa xác minh.",
        "origin_source_url": entry[1] if entry else "",
        "origin_verified": bool(entry),
        "origin_meaning_vi": entry[2] if entry else "",
    }
