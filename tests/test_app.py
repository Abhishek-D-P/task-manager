import json
import threading
import unittest

from app import app, tasks


class AppTests(unittest.TestCase):
    def test_query_definitions_include_task_crud_queries(self):
        with open("query.json") as handle:
            queries = json.load(handle)

        self.assertIn("get_tasks", queries)
        self.assertIn("create_task", queries)
        self.assertIn("update_task", queries)
        self.assertIn("delete_task", queries)

    def test_tasks_handler_can_run_in_a_different_thread(self):
        errors = []

        def worker():
            try:
                with app.test_request_context("/tasks", method="GET"):
                    tasks()
            except Exception as exc:  # pragma: no cover - regression guard
                errors.append(exc)

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
