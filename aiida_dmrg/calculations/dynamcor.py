from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import Dict, RemoteData

class DynCorrCalculation(CalcJob):
    """Dynamic correlator calculation using DMRG results."""

    INPUT_FILE = "dyncorr.inp"
    OUTPUT_FILE = "dyncorr.out"
    PARENT_FOLDER_NAME = "parent_dmrg"
    DEFAULT_PARSER = "dyncorr.base"

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Only need parent calculation folder as input
        spec.input(
            "parent_calc_folder",
            valid_type=RemoteData,
            required=True,
            help="Remote folder containing DMRG results"
        )

        spec.input("metadata.options.withmpi", valid_type=bool, default=True)
        spec.input(
            "metadata.options.parser_name",
            valid_type=str,
            default=cls.DEFAULT_PARSER,
            non_db=True,
        )

        spec.output(
            "output_parameters",
            valid_type=Dict,
            required=True,
            help="Dynamic correlator results"
        )

        spec.exit_code(
            200,
            "ERROR_NO_RETRIEVED_FOLDER",
            message="The retrieved folder could not be accessed."
        )
        spec.exit_code(
            300,
            "ERROR_PARSING_FAILED",
            message="Failed to parse the output file."
        )
        spec.exit_code(
            301,
            "ERROR_INVALID_OUTPUT", 
            message="Output file has invalid format."
        )

    def prepare_for_submission(self, folder):
        """Prepare calculation files."""
        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.withmpi = self.inputs.metadata.options.withmpi
        codeinfo.stdout_name = self.OUTPUT_FILE

        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [self.OUTPUT_FILE]

        # Link parent DMRG folder
        comp_uuid = self.inputs.parent_calc_folder.computer.uuid
        remote_path = self.inputs.parent_calc_folder.get_remote_path()
        copy_info = (comp_uuid, remote_path, self.PARENT_FOLDER_NAME)
        
        if self.inputs.code.computer.uuid == comp_uuid:
            calcinfo.remote_symlink_list = [copy_info]
        else:
            calcinfo.remote_copy_list = [copy_info]

        return calcinfo