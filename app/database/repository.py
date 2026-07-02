from app.learning.lesson_scope import sentence_is_valid_for_lesson, words_available_for_lesson
from app.learning.schemas import GrammarPoint, Lesson, Topic
from app.radicals.schemas import Radical
from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word


class LearningRepository:
    """Kho dữ liệu tạm của ứng dụng.

    Hiện tại app chưa dùng database thật như PostgreSQL. Khi khởi động, dữ liệu từ
    Google Sheet hoặc snapshot local được parse thành object Python rồi lưu trong
    class này. Các API/game chỉ đọc dữ liệu từ repository để logic gọn và dễ test.
    """

    def __init__(self) -> None:
        # Mỗi nhóm dữ liệu dùng dict theo id để tìm nhanh và tránh trùng bản ghi.
        self._words: dict[str, Word] = {}
        self._sentences: dict[str, Sentence] = {}
        self._lessons: dict[str, Lesson] = {}
        self._topics: dict[str, Topic] = {}
        self._grammar_points: dict[str, GrammarPoint] = {}
        self._radicals: dict[str, Radical] = {}

    def replace_words(self, words: list[Word]) -> None:
        # Thay toàn bộ từ vựng hiện có sau mỗi lần đồng bộ dữ liệu.
        self._words = {word.id: word for word in words if word.is_active}

    def replace_sentences(self, sentences: list[Sentence]) -> None:
        # Chỉ giữ câu đang active để game không lấy câu nháp/chưa dùng.
        self._sentences = {sentence.id: sentence for sentence in sentences if sentence.is_active}

    def replace_lessons(self, lessons: list[Lesson]) -> None:
        self._lessons = {lesson.id: lesson for lesson in lessons if lesson.is_active}

    def replace_topics(self, topics: list[Topic]) -> None:
        self._topics = {topic.id: topic for topic in topics if topic.is_active}

    def replace_grammar_points(self, grammar_points: list[GrammarPoint]) -> None:
        self._grammar_points = {
            grammar_point.id: grammar_point
            for grammar_point in grammar_points
            if grammar_point.is_active
        }

    def replace_radicals(self, radicals: list[Radical]) -> None:
        self._radicals = {radical.id: radical for radical in radicals if radical.is_active}

    def list_words(self) -> list[Word]:
        return list(self._words.values())

    def list_sentences(self) -> list[Sentence]:
        return list(self._sentences.values())

    def list_lessons(self) -> list[Lesson]:
        return sorted(self._lessons.values(), key=lambda lesson: lesson.order_index)

    def list_topics(self) -> list[Topic]:
        return list(self._topics.values())

    def list_grammar_points(self) -> list[GrammarPoint]:
        return list(self._grammar_points.values())

    def list_radicals(self) -> list[Radical]:
        return list(self._radicals.values())

    def list_words_for_lesson(self, lesson_order: int) -> list[Word]:
        # Với game bài N, người học được dùng từ bài 1 -> N theo yêu cầu dự án.
        return words_available_for_lesson(self.list_words(), lesson_order)

    def list_sentences_for_lesson(self, lesson_order: int) -> list[Sentence]:
        # Câu của bài N phải hợp lệ: không dùng từ vượt quá phạm vi bài cho phép.
        return [
            sentence
            for sentence in self.list_sentences()
            if sentence.lesson_order == lesson_order
            and sentence_is_valid_for_lesson(sentence, self.list_words())
        ]

    def get_word(self, word_id: str) -> Word | None:
        return self._words.get(word_id)

    def get_radical(self, radical_id: str) -> Radical | None:
        return self._radicals.get(radical_id)

    def has_data(self) -> bool:
        return bool(self._words)


# Một repository dùng chung cho toàn bộ app FastAPI.
repository = LearningRepository()
