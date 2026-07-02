import unittest

from app.api.routes import health
from app.data_sources.local_snapshot import load_local_snapshot


class ApiHealthTest(unittest.TestCase):
    def setUp(self) -> None:
        loaded = load_local_snapshot()
        self.assertIsNotNone(loaded)

    def test_health_reports_loaded_data(self) -> None:
        # Health check dùng khi deploy online để biết app còn chạy và đã có dữ liệu.
        data = health()

        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["words"], 1)
        self.assertGreaterEqual(data["lessons"], 1)


if __name__ == "__main__":
    unittest.main()
