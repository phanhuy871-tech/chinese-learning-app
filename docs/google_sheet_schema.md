# Google Sheet schema

Sheet goc nen chia thanh 5 tab. App se doc cac cot nay de tao game va kiem tra quy tac bai hoc.

## 1. lessons

```csv
lesson_id,lesson_order,lesson_name,level,description,is_active
lesson-1,1,Bai 1,HSK1,Chao hoi co ban,true
lesson-2,2,Bai 2,HSK1,Truong hoc va ngon ngu,true
lesson-3,3,Bai 3,HSK1,Thoi gian va sinh hoat,true
```

## 2. topics

```csv
topic_id,topic_name,description,is_active
greeting,Chao hoi,Nhom tu chao hoi,true
school,Truong hoc,Nhom tu ve truong hoc,true
language,Ngon ngu,Nhom tu ve ngon ngu,true
```

## 3. grammar

```csv
grammar_id,title_vi,pattern,explanation_vi,example_hanzi,example_pinyin,example_vi,level,lesson_id,lesson_order,tags,is_active
grammar-like,Cau truc thich lam gi,S + xihuan + V/O,Dung de noi ai do thich mot viec,我喜欢学习中文,wo xi huan xue xi zhong wen,Toi thich hoc tieng Trung,HSK1,lesson-2,2,verb|sentence,true
```

## 4. words

```csv
word_id,hanzi,pinyin,pinyin_no_tone,meaning_vi,meaning_en,word_type,level,lesson_id,lesson_order,topic_id,grammar_ids,audio_url,image_url,decomposition,difficulty,tags,is_active
w1,你好,ni hao,ni hao,xin chao,hello,phrase,HSK1,lesson-1,1,greeting,,,,Bo nhan dung + bo khau,1,greeting,true
w2,谢谢,xie xie,xie xie,cam on,thank you,phrase,HSK1,lesson-1,1,greeting,,,1,greeting,true
w3,再见,zai jian,zai jian,tam biet,goodbye,phrase,HSK1,lesson-1,1,greeting,,,1,greeting,true
w4,老师,lao shi,lao shi,giao vien,teacher,noun,HSK1,lesson-2,2,school,,,1,school,true
w5,学生,xue sheng,xue sheng,hoc sinh,student,noun,HSK1,lesson-2,2,school,,,1,school,true
w6,中文,zhong wen,zhong wen,tieng Trung,Chinese,noun,HSK1,lesson-2,2,language,grammar-like,,1,language,true
w7,喜欢,xi huan,xi huan,thich,like,verb,HSK1,lesson-2,2,language,grammar-like,,1,verb,true
w8,学习,xue xi,xue xi,hoc tap,study,verb,HSK1,lesson-2,2,school,grammar-like,,1,verb,true
```

## 5. sentences

```csv
sentence_id,target_word_id,target_hanzi,sentence_slot,sentence_hanzi,sentence_pinyin,sentence_vi,words,word_ids,blank_sentence,blank_answer_hanzi,blank_answer_word_id,blank_options_word_ids,grammar_ids,level,lesson_id,lesson_order,max_word_lesson_order,topic_id,audio_url,difficulty,tags,is_active,validation_status,scope_rule,note
s0001_1,w0001,我,1,我很好。,wo hen hao,Toi rat tot,我|很|好,w0001|w0020|w0002,___很好。,我,w0001,,,HSK1,lesson-1,1,1,basic,,1,Nhóm 1|sentence_slot_1,true,ready,only_words_from_lesson_1_to_1,auto_from_vocab_example
s0001_2,w0001,我,2,,,,,,,,,,,HSK1,lesson-1,1,1,basic,,1,Nhóm 1|sentence_slot_2,true,needs_content,only_words_from_lesson_1_to_1,can_bo_sung_cau_chua_tu_vung_nay
```

## Quy tac quan trong

- `lesson_order` la so thu tu bai hoc.
- Tu vung bai 1 co `lesson_order = 1`.
- Tu vung bai 2 co `lesson_order = 2`.
- Cau bai 2 co `lesson_order = 2`.
- Cau bai 2 chi duoc dung `word_ids` co `lesson_order <= 2`.
- Cau bai 3 chi duoc dung `word_ids` co `lesson_order <= 3`.
- Cot `max_word_lesson_order` cho phep khoa pham vi tu vung cua cau. Mac dinh bang `lesson_order`.
- Cot `word_ids` la danh sach ID tu vung trong cau, cach nhau bang dau `|`.
- Cot `blank_options_word_ids` la danh sach dap an cho game dien tu, cach nhau bang dau `|`.
- Moi `target_word_id` nen co 2-3 dong cau trong tab `cau trong game`.
- `sentence_slot` la so thu tu cau cho mot tu vung: 1, 2, hoac 3.
- `validation_status = ready` nghia la app co the dung cau do de tao game.
- `validation_status = needs_content` nghia la dong do chi la cho trong de bo sung cau sau, app se bo qua khi tao game.
- Cau cua bai N chi duoc dung tu vung co `lesson_order <= N`; cot `scope_rule` ghi ro quy tac nay de kiem tra bang mat.

## 6. radicals

Tab `bo thu` la kho kien thuc bo thu. Cac bo thu xuat hien trong tab `tu vung` nen duoc thong ke tai day.

```csv
radical_id,bo_thu,hanzi_in_words,pinyin,han_viet,meaning_vi,memory_tip,semantic_note,common_words,is_active
radical-person,人 / 亻,他|你|们,ren,Nhan,nguoi,Dang nguoi dung thang,Lien quan den con nguoi,他|你|他们,true
```

Module `hoc tu vung` se:

- hien thi tu theo `lesson_order`;
- cho nghe am thanh bang `audio_url`, neu chua co thi dung giong doc trinh duyet;
- hien thi `hanzi`, `pinyin`, `meaning_vi`, `decomposition`, vi du;
- doc tab `bo thu` de hien thi bo thu lien quan trong phan chiet tu.
