from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import Dict, RemoteData
from aiida.plugins import DataFactory

class DynCorrCalculation(CalcJob):
    """
    AiiDA calculation plugin for Dynamic Correlator calculations.
    """

    INPUT_FILE = "dyncorr.inp"
    OUTPUT_FILE = "dyncorr.out"
    DEFAULT_PARSER = "dyncorr"

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("parameters", valid_type=Dict, required=True, help="Input parameters for DynCorr calculation")
        spec.input("dmrg_folder", valid_type=RemoteData, required=True, help="Folder of the completed DMRG calculation")
        spec.input("metadata.options.parser_name", valid_type=str, default=cls.DEFAULT_PARSER, non_db=True)

        spec.output("output_matrix", valid_type=Dict, required=True, help="Dynamic correlator matrix")
        spec.output("time_measurement", valid_type=Dict, required=True, help="Time measurements")

        spec.exit_code(300, "ERROR_NO_RETRIEVED_FOLDER", message="Retrieved folder could not be accessed.")
        spec.exit_code(301, "ERROR_PARSING_OUTPUT", message="Error parsing the output file.")

    def prepare_for_submission(self, folder):
        input_params = self.inputs.parameters.get_dict()

        input_string = self._render_input(input_params)
        folder.write_file(self.INPUT_FILE, input_string)

        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.cmdline_params = settings.pop('cmdline', [])
        codeinfo.stdin_name = self.INPUT_FILE
        codeinfo.stdout_name = self.OUTPUT_FILE
        codeinfo.stderr_name = self.OUTPUT_FILE
        codeinfo.withmpi = False

        calcinfo = CalcInfo()
        calcinfo.local_copy_list = [(self.inputs.dmrg_folder.uuid,)]
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.stdin_name = self.INPUT_FILE
        calcinfo.stdout_name = self.OUTPUT_FILE
        calcinfo.stderr_name = self.OUTPUT_FILE
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [self.OUTPUT_FILE]

        calcinfo.remote_symlink_list = []
        calcinfo.remote_copy_list = []
        if "parent_folder" in self.inputs:
            calcinfo.remote_copy_list.append(
                (
                    self.inputs.parent_folder.computer.uuid,
                    self.inputs.parent_folder.get_remote_path(),
                    self.PARENT_FOLDER_NAME,
                )
            )

        return calcinfo
    
    def _render_input(self, input_params):
        """Render the input file."""
        param_order = [
            "N_max",
            "cutoff"
        ]
        ordered_params = []
        for key in param_order:
            if key in input_params:
                ordered_params.append(key)

        return " ".join(ordered_params)