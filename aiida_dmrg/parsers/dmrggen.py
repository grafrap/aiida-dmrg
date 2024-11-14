"""AiiDA-DMRG output parser"""

import datetime
import re
import io

import cclib
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

      """Parse DMRG output log"""

      property_dict = self._parse_log_cclib(log_file_string)

      if property_dict is None:
          return self.exit_codes.ERROR_OUTPUT_PARSING
      
      # Set the output nodes
      self._set_output_structure(inputs, Dict(dict=property_dict))

      exit_code = self._final_checks_on_log(log_file_string, property_dict)
      if exit_code is not None:
          return exit_code
      return None
  
  def _parse_log_cclib(self, log_file_string):

      data = cclib.io.ccread(io.StringIO(log_file_string))

      if data is None:
          return None

      property_dict = data.getattributes()

      def make_serializeable(data):
          """Recursively go through the dictionary and convert unserializeable values in-place:

          1) In numpy arrays:
              * ``nan`` -> ``0.0``
              * ``inf`` -> large number
          2) datetime.timedelta (introduced in cclib v1.8) -> convert to seconds

          :param data: A mapping of data.
          """
          if isinstance(data, dict):
              for key, value in data.items():
                  data[key] = make_serializeable(value)
          elif isinstance(data, list):
              for index, item in enumerate(data):
                  data[index] = make_serializeable(item)
          elif isinstance(data, np.ndarray):
              np.nan_to_num(data, copy=False)
          elif isinstance(data, datetime.timedelta):
              data = data.total_seconds()
          return data

      make_serializeable(property_dict)

      return property_dict
  
  def _set_output_structure(self, inputs, property_dict):
      """Set the output nodes"""
      # TODO: add here the output nodes
      return None  
  
  def _final_checks_on_log(self, log_file_string, property_dict):
      """Perform final checks on the log file"""
      # TODO: add here all exit codes

      if "Error termination" in log_file_string:
          return self.exit_codes.ERROR_TERMINATION
      
      
      
      return None
  
