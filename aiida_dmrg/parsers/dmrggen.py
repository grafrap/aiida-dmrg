"""AiiDA-DMRG output parser"""

import re
import io
import numpy as np
from aiida.common import NotExistent
from aiida.engine import ExitCode
from aiida.orm import Dict, Float, StructureData
from aiida.parsers import Parser

class DMRGBaseParser(Parser):
  """
  Basic AiiDA parser for the output of DMRG calculations
  """

  def parse(self, **kwargs):
    """"Receives in input a dictionary of retrieved nodes. Does all the logic here."""

    fname = self.node.process_class.OUTPUT_FILE

    try:
      out_folder = self.retrieved
      if fname not in out_folder.base.repository.list_object_names():
        return self.exit_codes.ERROR_OUTPUT_MISSING
      log_file_string = out_folder.base.repository.get_object_content(fname)
    except NotExistent:
      return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER
    except OSError:
      return self.exit_codes.ERROR_OUTPUT_LOG_READ
    
    exit_code = self._parse_log(log_file_string, self.node.inputs)

    if exit_code is not None:
      return exit_code
    
    return ExitCode(0)
  
  def _parse_log(self, log_file_string, inputs):

    # TODO: Implement the parsing logic here