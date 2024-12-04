import re
from aiida.parsers import Parser
from aiida.orm import Dict, ExitCode

class DynCorrParser(Parser):
    """Parser for Dynamic Correlator output files."""

    def parse(self, **kwargs):
        try:
            retrieved = self.retrieved
            output_file = self.node.process_class.OUTPUT_FILE
            if output_file not in retrieved.list_object_names():
                return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

            content = retrieved.get_object_content(output_file)
            matrix = self._parse_output(content)

            self.out('output_matrix', Dict(dict=matrix))

            return ExitCode(0)
        except Exception:
            return self.exit_codes.ERROR_PARSING_OUTPUT

    def _parse_output(self, content):
        matrix_match = re.search(r"\[\s*(.+?)\s*\]", content, re.DOTALL)

        matrix_str = matrix_match.group(1).replace('\n', '').strip()
        matrix = eval(matrix_str)

        return matrix