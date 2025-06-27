"""Basic tests for the wholesaler agent."""

import unittest


class TestWholesalerAgent(unittest.TestCase):
    """Test cases for the wholesaler agent."""

    def test_import_modules(self):
        """Test that core modules can be imported."""
        try:
            from src import agent_executor
            from src import gemini_agent
            # If we reach here, imports were successful
            self.assertIsNotNone(agent_executor)
            self.assertIsNotNone(gemini_agent)
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")

    def test_basic_functionality(self):
        """Basic test to ensure the test framework works."""
        self.assertEqual(1 + 1, 2)


if __name__ == '__main__':
    unittest.main()
