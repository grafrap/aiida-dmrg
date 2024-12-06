import unittest
from unittest.mock import MagicMock, PropertyMock

from aiida.orm import Node

from aiida_dmrg.parsers.dyncorr_parser import DynCorrParser


class TestDynCorrParser(unittest.TestCase):
    def setUp(self):
        mock_node = MagicMock(spec=Node)
        mock_process_class = MagicMock()
        mock_process_class.OUTPUT_FILE = "dyncorr.out"
        mock_node.process_class = mock_process_class
        self.parser = DynCorrParser(node=mock_node)
        self.out_folder = MagicMock()

        # Mock the 'retrieved' property
        type(self.parser).retrieved = PropertyMock(
            return_value=self.out_folder,
        )

    def test_parse_success(self):
        repo = self.out_folder.base.repository
        repo.list_object_names.return_value = ["dyncorr.out"]
        repo.get_object_content.return_value = """
        N = 201	 i = 3	 Error = 0.006710181959374006
        sum_χ = 0.45679996344513446
        Δsum = 4.996774021231998e-5	 Δt = 48 milliseconds
        N > N_max
        [1 2; 3 4]
        """
        exit_code = self.parser.parse()
        self.assertEqual(exit_code.status, 0)

    def test_missing_output_file(self):
        self.out_folder.base.repository.list_object_names.return_value = []
        exit_code = self.parser.parse()
        ec = self.parser.exit_codes
        self.assertEqual(exit_code, ec.ERROR_OUTPUT_MISSING)

    def test_invalid_output(self):
        repo = self.out_folder.base.repository
        repo.list_object_names.return_value = ["dyncorr.out"]
        repo.get_object_content.return_value = "Invalid content"
        exit_code = self.parser.parse()
        ec = self.parser.exit_codes
        self.assertEqual(exit_code, ec.ERROR_PARSING_OUTPUT)


if __name__ == "__main__":
    unittest.main()
