"""AiiDA-DMRG output parser"""

import datetime
import re
import io

import cclib
import numpy as np
from aiida.common import NotExistent
from aiida.engine import ExitCode
from aiida.orm import Dict, List
from aiida.parsers import Parser

class DMRGBaseParser(Parser):
    """Parser for DMRG output files"""
    
    def parse(self, **kwargs):
        """Parse the DMRG output file"""
        
        fname = self.node.process_class.OUTPUT_FILE

        try:
            out_folder = self.retrieved
            available_files = out_folder.base.repository.list_object_names()
            if fname not in out_folder.base.repository.list_object_names():
                print(f"Available files: {available_files}")
                return self.exit_codes.ERROR_OUTPUT_MISSING
            log_file_string = out_folder.base.repository.get_object_content(fname)
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER
        except OSError:
            return self.exit_codes.ERROR_OUTPUT_LOG_READ
        
        exit_code = self._parse_log(log_file_string)
        if exit_code is not None:
            return exit_code
        
        return ExitCode(0)

    def _parse_log(self, log_file_string):
        """Parse the DMRG output file content"""

        error_messages = {
            "Usage: julia DMRG_template_pll_Energyextrema.jl": self.exit_codes.ERROR_READING_INPUT_FILE,
            "Failed to read from stdin": self.exit_codes.ERROR_READING_INPUT_FILE,
            "Check s": self.exit_codes.ERROR_UNPHYISCAL_INPUT,
            "J matrix not properly closed with ']'.": self.exit_codes.ERROR_J_VALUE,
            "All rows in J matrix must have the same number of columns.": self.exit_codes.ERROR_J_VALUE,
            "Failed to parse J": self.exit_codes.ERROR_J_VALUE,
            "Sz must be provided when conserve_symmetry is true.": self.exit_codes.ERROR_UNPHYISCAL_INPUT,
            "J matrix dimensions": self.exit_codes.ERROR_J_VALUE,
            "J must either be a Float64 scalar or a": self.exit_codes.ERROR_J_VALUE,
        }

        # Check for error messages
        for message, exit_code in error_messages.items():
            if message in log_file_string:
                return exit_code
        
        if "Error" in log_file_string or "ERROR" in log_file_string:
            return self.exit_codes.ERROR_CALCULATION_FAILED

        try:
            # Parse the arrays
            energy_list = self._extract_array(log_file_string, "List of E:")
            s_squared_list = self._extract_array(log_file_string, "List of S²:")
            sz_list = self._extract_array(log_file_string, "List of Sz(i):")
            
            # Parse the total time
            time_match = re.search(r"total time = (.+?)$", log_file_string, re.MULTILINE)
            if time_match:
                total_time = time_match.group(1).strip()
            else:
                total_time = None
                return self.exit_codes.ERROR_OUTPUT_MISSING

            # Create output dictionary
            output_dict = {
                'energies': energy_list,
                'spin_squared': s_squared_list,
                'spin_z': sz_list,
                'total_time': total_time
            }

            # Store results in output nodes
            self.out('output_parameters', Dict(dict=output_dict))
            
            return None
        
        except Exception as exc:
            print(f"Error during parsing: {str(exc)}")
            return self.exit_codes.ERROR_INVALID_OUTPUT

    def _extract_array(self, content, marker):
        """Extract array data following a marker string"""
        try:
            # Find the marker line
            start_idx = content.find(marker)
            if start_idx == -1:
                return None
            
            # Get the line containing the array
            end_idx = content.find('\n\n', start_idx)
            if end_idx == -1:
                end_idx = content.find('----------', start_idx)
            if end_idx == -1:
                return None
                
            array_str = content[start_idx:end_idx].split('\n')[1].strip()
            
            # Convert string representation to Python list/array
            array_data = eval(array_str)
            return array_data

        except Exception as exc:
            print(f"Error extracting array data: {str(exc)}")
            return None

