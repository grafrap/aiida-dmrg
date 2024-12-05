# test_dyncorr.py

import unittest
from unittest.mock import MagicMock, PropertyMock
from aiida.orm import Dict, Node
from aiida.common import AttributeDict
from aiida_dmrg.parsers.dyncorr_parser import DynCorrParser
from aiida.common.exceptions import ValidationError

class TestDynCorrParser:
    def setup_method(self):
        mock_node = MagicMock(spec=Node)
        mock_process_class = MagicMock
        mock_process_class.OUTPUT_FILE = 'dyncorr.out'
        mock_node.process_class = mock_process_class
        self.parser = DynCorrParser(node=mock_node)
        self.out_folder = MagicMock()

        # Mock the 'retrieved' property
        type(self.parser).retrieved = PropertyMock(return_value=self.out_folder)

    def test_parse_success(self):
        self.out_folder.base.repository.list_object_names.return_value = ['dyncorr.out']
        self.out_folder.base.repository.get_object_content.return_value = """
        Dynamic correlator:
        [1.0 2.0; 3.0 4.0]
        """
        exit_code = self.parser.parse()
        assert exit_code.status == 0

    def test_missing_output_file(self):
        self.out_folder.base.repository.list_object_names.return_value = []
        exit_code = self.parser.parse()
        assert exit_code == self.parser.ERROR_OUTPUT_MISSING

    def test_invalid_output(self):
        self.out_folder.base.repository.list_object_names.return_value = ['dyncorr.out']
        self.out_folder.base.repository.get_object_content.return_value = "Invalid content"
        exit_code = self.parser.parse()
        assert exit_code == self.parser.ERROR_PARSING_OUTPUT

if __name__ == '__main__':
    unittest.main()
