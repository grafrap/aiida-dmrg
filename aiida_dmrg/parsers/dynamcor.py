# dyncorr_parser.py
import numpy as np
from aiida.parsers import Parser
from aiida.common import NotExistent
from aiida.engine import ExitCode
from aiida.orm import Dict

class DynCorrParser(Parser):
    """Parser for dynamic correlator calculation output."""

    def parse(self, **kwargs):
        """Parse the matrix output file."""
        
        try:
            out_folder = self.retrieved
            if not out_folder:
                return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

            filename = self.node.process_class.OUTPUT_FILE
            if filename not in out_folder.list_object_names():
                return self.exit_codes.ERROR_OUTPUT_MISSING

            content = out_folder.get_object_content(filename)
            
            # Parse the matrix
            matrix = self._parse_matrix(content)
            if matrix is None:
                return self.exit_codes.ERROR_INVALID_OUTPUT
            
            # Store results
            self.out('output_parameters', Dict(dict={
                'correlator_matrix': matrix.tolist()
            }))
            
            return ExitCode(0)

        except Exception:
            return self.exit_codes.ERROR_PARSING_FAILED

    def _parse_matrix(self, content):
        """Parse matrix with semicolon-separated rows."""
        try:
            # Find matrix start/end
            start_idx = content.find('[')
            end_idx = content.find(']')
            
            if start_idx == -1 or end_idx == -1:
                return None
                
            matrix_str = content[start_idx:end_idx+1]
            
            # Split rows on semicolon and clean up
            rows = matrix_str.strip('[]').split(';')
            rows = [row.strip() for row in rows]
            
            # Convert to numpy array
            matrix = np.array([
                [float(x) for x in row.split()]
                for row in rows
            ])
            
            return matrix

        except Exception:
            return None