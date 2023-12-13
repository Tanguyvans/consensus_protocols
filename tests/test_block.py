import unittest
from block import Block

class TestBlock(unittest.TestCase):
    def setUp(self):
        self.block = Block(index=1, timestamp="1234567890", data="Sample Data", previous_hash="0")

    def test_to_dict(self):
        expected_dict = {
            "index": 1,
            "timestamp": "1234567890",
            "data": "Sample Data",
            "previous_hash": "0",
            "current_hash": self.block.current_hash
        }
        self.assertEqual(self.block.to_dict(), expected_dict)

    def test_current_hash(self):
        expected_hash = "4155afa7eca4b3d6562ec60c9afa7bf7e0953bed9da5df0ceddd581d55648f1d"
        self.assertEqual(self.block.current_hash, expected_hash)

    def test_str(self):
        expected_str = "================\n" \
                       "prev_hash:\t 0\n" \
                       "Data:\t\t Sample Data\n" \
                       f"Hash:\t\t {self.block.current_hash}\n"
        self.assertEqual(str(self.block), expected_str)

if __name__ == "__main__":
    unittest.main()
