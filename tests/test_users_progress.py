import unittest

from app.users.progress_store import (
    empty_progress,
    get_progress,
    init_user_database,
    list_users,
    reset_progress,
    save_progress,
)


class UsersProgressTest(unittest.TestCase):
    def setUp(self) -> None:
        init_user_database()

    def test_default_users_exist(self) -> None:
        users = list_users()

        self.assertGreaterEqual(len(users), 10)
        self.assertEqual(users[0]["id"], "user-01")

    def test_progress_is_saved_per_user(self) -> None:
        user_one = "user-01"
        user_two = "user-02"
        reset_progress(user_one)
        reset_progress(user_two)

        progress = empty_progress()
        progress["studiedWords"] = {"word-001": True}
        progress["answered"] = 2
        progress["correct"] = 1
        save_progress(user_one, progress)

        self.assertEqual(get_progress(user_one)["answered"], 2)
        self.assertEqual(get_progress(user_two)["answered"], 0)


if __name__ == "__main__":
    unittest.main()
