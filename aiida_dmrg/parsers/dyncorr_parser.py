import ast
from aiida.parsers import Parser
from aiida.orm import Dict
from aiida.engine import ExitCode
from aiida.common import NotExistent

class DynCorrParser(Parser):
    """Parser for Dynamic Correlator output files."""

    def parse(self, **kwargs):
        """Parse the Dynamic Correlator output file."""

        fname = self.node.process_class.OUTPUT_FILE

        try:
            out_folder = self.retrieved
            available_files = out_folder.base.repository.list_object_names()
            if fname not in available_files:
                print(f"Available files: {available_files}")
                return self.exit_codes.ERROR_OUTPUT_MISSING
            log_file_string = out_folder.base.repository.get_object_content(fname)
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER
        except OSError:
            return self.exit_codes.ERROR_OUTPUT_LOG_READ

        exit_code = self._parse_output(log_file_string)
        if exit_code is not None:
            return exit_code

        return ExitCode(0)

    def _parse_output(self, content):
        """Parse the Dynamic Correlator output file content."""

        if "Error:" in content or "ERROR" in content:
            return self.exit_codes.ERROR_CALCULATION_FAILED

        try:
            # Parse the arrays
            output_matrix = self._extract_output_matrix(content)
            if output_matrix is None:
                return self.exit_codes.ERROR_PARSING_OUTPUT
            self.out("output_matrix", Dict(dict={'matrix': output_matrix}))
            return None
        
        except Exception as exception:
            return self.exit_codes.ERROR_PARSING_OUTPUT


    def _extract_output_matrix(self, content):
        """Extract the output matrix from the content."""
        
        try:
            start_idx = content.find("[")
            end_idx = content.find("]", start_idx + 5) + 1
            if start_idx + 1 == end_idx:
                return None
            matrix_string = content[start_idx:end_idx].split("\n")[0]

            # Convert the matrix string to a Python list/array
            formatted_matrix_string = matrix_string.replace("; ", '],[').replace(" ", ', ')
            output_matrix = ast.literal_eval(f'[{formatted_matrix_string}]')
            return output_matrix

        except Exception as exception:
            print(f"Error extracting output matrix: {exception}")
            return None

