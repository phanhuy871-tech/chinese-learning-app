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

    def test_teaching_examples_match_target_and_have_translations(self) -> None:
        for item in repository.list_monolithic_characters():
            self.assertTrue(item.meanings, item.simplified)
            self.assertIn(len(item.examples), (2, 3), item.simplified)
            for example in item.examples:
                self.assertIn(item.simplified, example["focus"])
                self.assertIn(example["focus"], example["hanzi"])
                self.assertTrue(example["pinyin"])
                self.assertTrue(example["meaning_vi"])

    def test_common_readings_do_not_default_to_surnames_or_obsolete_forms(self) -> None:
        items = {item.simplified: item for item in repository.list_monolithic_characters()}
        for char, pinyin, meaning in [("水", "shuǐ", "nước"), ("鸟", "niǎo", "chim"), ("页", "yè", "trang giấy"), ("也", "yě", "cũng")]:
            self.assertEqual(items[char].pinyin, pinyin)
            self.assertIn(meaning, items[char].meaning_vi)
        self.assertEqual({reading["pinyin"] for reading in items["重"].readings}, {"zhòng", "chóng"})

    def test_unverified_origins_are_not_presented_as_facts(self) -> None:
        items = {item.simplified: item for item in repository.list_monolithic_characters()}
        self.assertTrue(items["大"].origin_verified)
        self.assertIn("Chưa có thuyết minh", items["了"].origin_story_vi)
        self.assertEqual(items["了"].origin_source_url, "")


if __name__ == "__main__":
    unittest.main()
