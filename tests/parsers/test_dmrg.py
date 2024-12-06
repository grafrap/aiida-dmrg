import unittest
from unittest.mock import MagicMock, PropertyMock

from aiida.orm import Node

from aiida_dmrg.parsers.dmrg import DMRGBaseParser


class TestDMRGBaseParser(unittest.TestCase):
    def setUp(self):
        mock_node = MagicMock(spec=Node)
        mock_process_class = MagicMock()
        mock_process_class.OUTPUT_FILE = "dmrg.out"
        mock_node.process_class = mock_process_class
        self.parser = DMRGBaseParser(node=mock_node)
        self.out_folder = MagicMock()

        # Mock the 'retrieved' property
        type(self.parser).retrieved = PropertyMock(
            return_value=self.out_folder,
        )

    def test_parse_success(self):
        repo = self.out_folder.base.repository
        repo.list_object_names.return_value = ["dmrg.out"]
        repo.get_object_content.return_value = """
        List of E:
        [1.0, 2.0, 3.0]
        List of S²:
        [0.5, 0.5, 0.5]
        List of Sz(i):
        [0.1, 0.1, 0.1]
        total time = 123.45
        """
        exit_code = self.parser.parse()
        self.assertEqual(exit_code.status, 0)

    def test_missing_output_file(self):
        repo = self.out_folder.base.repository
        repo.list_object_names.return_value = []
        exit_code = self.parser.parse()
        ec = self.parser.exit_codes
        self.assertEqual(exit_code, ec.ERROR_OUTPUT_MISSING)

    def test_error_in_log(self):
        repo = self.out_folder.base.repository
        repo.list_object_names.return_value = ["dmrg.out"]
        repo.get_object_content.return_value = "Error: Calculation failed."
        exit_code = self.parser.parse()
        ec = self.parser.exit_codes
        self.assertEqual(exit_code, ec.ERROR_CALCULATION_FAILED)

    def test_invalid_output(self):
        repo = self.out_folder.base.repository
        repo.list_object_names.return_value = ["dmrg.out"]
        repo.get_object_content.return_value = "Invalid content"
        exit_code = self.parser.parse()
        ec = self.parser.exit_codes
        self.assertEqual(exit_code, ec.ERROR_OUTPUT_MISSING)


if __name__ == "__main__":
    unittest.main()
