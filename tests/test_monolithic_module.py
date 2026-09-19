import unittest

from app.data_sources.local_snapshot import load_local_snapshot
from app.database.repository import repository


class MonolithicModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_local_snapshot()

    def test_curriculum_has_284_characters_and_140_core_items(self) -> None:
        characters = repository.list_monolithic_characters()
        self.assertEqual(len(characters), 284)
        self.assertEqual(sum(item.is_core for item in characters), 140)

    def test_each_character_has_learning_path_and_evolution_links(self) -> None:
        for item in repository.list_monolithic_characters():
            self.assertIn(item.week, range(1, 6))
            self.assertTrue(item.oracle_image_url.startswith("https://"))
            self.assertTrue(item.bronze_image_url.startswith("https://"))
            self.assertTrue(item.seal_image_url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
