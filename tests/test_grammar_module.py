import unittest

from app.data_sources.local_snapshot import load_local_snapshot
from app.database.repository import repository


class GrammarModuleTest(unittest.TestCase):
    def setUp(self) -> None:
        loaded = load_local_snapshot()
        self.assertIsNotNone(loaded)

    def test_grammar_points_load_from_snapshot(self) -> None:
        # Snapshot local đang là nguồn dữ liệu chính khi Google Sheet chưa OAuth.
        grammar_points = repository.list_grammar_points()

        self.assertGreaterEqual(len(grammar_points), 1)
        self.assertTrue(grammar_points[0].title_vi)
        self.assertTrue(grammar_points[0].pattern)

    def test_grammar_can_filter_by_lesson_order(self) -> None:
        # Module Ngữ pháp trên UI chỉ hiển thị ngữ pháp của bài đang chọn.
        lesson_one = [
            grammar_point
            for grammar_point in repository.list_grammar_points()
            if grammar_point.lesson_order == 1
        ]

        self.assertGreaterEqual(len(lesson_one), 1)
        self.assertTrue(all(grammar_point.lesson_order == 1 for grammar_point in lesson_one))


if __name__ == "__main__":
    unittest.main()
