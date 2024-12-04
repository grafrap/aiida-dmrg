# dyncorr_parser.py

import re
import ast
from aiida.parsers import Parser
from aiida.orm import Dict
from aiida.engine import ExitCode
from aiida.common.exceptions import ValidationError

class DynCorrParser(Parser):
    """Parser for Dynamic Correlator output files."""

    ERROR_OUTPUT_MISSING = ExitCode(
        300,
        "ERROR_OUTPUT_MISSING",
        "The output file 'dyncorr.out' is missing."
    )
    ERROR_NO_RETRIEVED_FOLDER = ExitCode(
        301,
        "ERROR_NO_RETRIEVED_FOLDER",
        "Retrieved folder could not be accessed."
    )
    ERROR_OUTPUT_LOG_READ = ExitCode(
        302,
        "ERROR_OUTPUT_LOG_READ",
        "Error reading the output log file."
    )
    ERROR_PARSING_OUTPUT = ExitCode(
        303,
        "ERROR_PARSING_OUTPUT",
        "Error parsing the output file."
    )
    ERROR_CALCULATION_FAILED = ExitCode(
        304,
        "ERROR_CALCULATION_FAILED",
        "The calculation failed."
    )

    def parse(self, **kwargs):
        """Parse the Dynamic Correlator output file."""

        fname = self.node.process_class.OUTPUT_FILE

        try:
            out_folder = self.retrieved
            available_files = out_folder.base.repository.list_object_names()
            if fname not in available_files:
                print(f"Available files: {available_files}")
                return self.ERROR_OUTPUT_MISSING
            log_file_string = out_folder.base.repository.get_object_content(fname)
        except FileNotFoundError:
            return self.ERROR_NO_RETRIEVED_FOLDER
        except OSError:
            return self.ERROR_OUTPUT_LOG_READ

        exit_code = self._parse_output(log_file_string)
        print(f"Exit code: {exit_code}")
        if exit_code is not None:
            return exit_code

        return ExitCode(0)

    def _parse_output(self, content):
        """Parse the Dynamic Correlator output file content."""

        try:
            # Parse the arrays
            output_matrix = self._extract_output_matrix(content)
        except Exception as exception:
            return self.ERROR_PARSING_OUTPUT
        
        if isinstance(output_matrix, ExitCode):
            return output_matrix

        self.out("output_matrix", Dict(dict={'matrix': output_matrix}))
        return None

    def _extract_output_matrix(self, content):
        """Extract the output matrix from the content."""
        
        # Extract the matrix from the content
        try:
            start_idx = content.find("[")
            end_idx = content.find("]", start_idx) + 1
            if start_idx + 1 == end_idx:
                return self.ERROR_PARSING_OUTPUT
            matrix_string = content[start_idx:end_idx].split("\n")[0]

            # Convert the matrix string to a Python list/array
            formatted_matrix_string = matrix_string.replace("; ", '],[').replace(" ", ', ')
            output_matrix = ast.literal_eval(f'[{formatted_matrix_string}]')
            return output_matrix

        except (ValueError, SyntaxError):
            raise ValidationError("Failed to parse the output matrix.")
        except Exception as exception:
            raise ValidationError(f"An unexpected error occurred: {exception}")

        return None