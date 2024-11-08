"""DMRG input plugin."""
from aiida.common import CalcInfo, CodeInfo

# from aiida.cmdline.utils import echo
from aiida.engine import CalcJob
from aiida.engine.processes.process_spec import CalcJobProcessSpec
from aiida.orm import Dict, Float, RemoteData
from aiida.plugins import DataFactory


class DMRGCalculation(CalcJob):
    """
    AiiDA calculation plugin for the DMRG code.

    Template: 
    TODO
    """

    INPUT_FILE = "aiida.inp"
    OUTPUT_FILE = "aiida.out"
    PARENT_FOLDER_NAME = "parent_calc"
    DEFAULT_PARSER = "dmrggen.base"

    @classmethod
    def define(cls, spec: CalcJobProcessSpec):
        super().define(spec)

        # Input parameters
        spec.input(
            "parameters",
            valid_type=Dict,
            required=True,
            help="Input parameters for the DMRG calculation",
        )

        spec.input(
            "parent_calc_folder",
            valid_type=RemoteData,
            required=False,
            help="the folder of a completed dmrg calculation",
        )

        spec.input("metadata.options.withmpi", valid_type=bool, default=True)

        spec.input(
            "metadata.options.parser_name",
            valid_type=str,
            default=cls.DEFAULT_PARSER,
            non_db=True,
        )

        # Outputs
        spec.output(
            "output_parameters",
            valid_type=Dict,
            required=True,
            help="The results of the calculation",
        )

        spec.output(
            "Hamiltonian_sites",
            valid_type=Dict, # TODO: we want to have HDF5Data here
            required=False,
            help="Sites and Hamiltonian of the system for dynamical correlator",
        )

        spec.default_output_node = "output_parameters"
        spec.outputs.dynamic = True

        # Exit codes
        spec.exit_code(
            200,
            "ERROR_NO_RETRIEVED_FOLDER",
            message="The retrieved folder data node could not be accessed.",
        )
        spec.exit_code(
            210,
            "ERROR_OUTPUT_MISSING",
            message="The retrieved folder did not contain the output file.",
        )
        spec.exit_code(
            211,
            "ERROR_OUTPUT_LOG_READ",
            message="The retrieved output log could not be read.",
        )
        spec.exit_code(
            220,
            "ERROR_OUTPUT_PARSING",
            message="The output file could not be parsed.",
        )
        spec.exit_code(
            301,
            "ERROR_SCF_FAILURE",
            message="The SCF did not converge and the calculation was terminated.",
        )
        spec.exit_code(
            302,
            "ERROR_ASYTOP",
            message="The calculation was terminated due to a logic error in ASyTop.",
        )
        spec.exit_code(
            303,
            "ERROR_INACCURATE_QUADRATURE_CALDSU",
            message="The calculation was terminated due to an inaccurate quadrature in CalDSu.",
        )
        spec.exit_code(
            390,
            "ERROR_TERMINATION",
            message="The calculation was terminated due to an error.",
        )
        spec.exit_code(
            391,
            "ERROR_NO_NORMAL_TERMINATION",
            message="The log did not contain 'Normal termination' (probably out of time).",
        )

    def prepare_for_submission(self, folder):
        """
        This is the routine to be called when you want to create
        the input files and related stuff with a plugin.

        :param folder: a aiida.common.folders.Folder subclass where
                        the plugin should put all its files.
        """
        
        # Generate the input file
        input_string = DMRGCalculation._render_input_string_from_params(
            self.inputs.parameters.get_dict()
        )

        # TODO

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = settings.pop("cmdline", [])
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdin_name = self.INPUT_FILE
        codeinfo.stdout_name = self.OUTPUT_FILE
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        # create calculation info
        calcinfo = CalcInfo()
        calcinfo.remote_copy_list = []
        calcinfo.local_copy_list = []
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.stdin_name = self.INPUT_FILE
        calcinfo.stdout_name = self.OUTPUT_FILE
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [self.OUTPUT_FILE]

        #symlink or copy to parent calculation
        calcinfo.remote_symlink_list = []
        calcinfo.remote_copy_list = []
        if "parent_calc_folder" in self.inputs:
            comp_uuid = self.inputs.parent_calc_folder.computer.uuid
            remote_path = self.inputs.parent_calc_folder.get_remote_path()
            copy_info = (comp_uuid, remote_path, self.PARENT_FOLDER_NAME)
            if self.inputs.code.computer.uuid == comp_uuid:
                calcinfo.remote_symlink_list.append(copy_info)
            else:
                calcinfo.remote_copy_list.append(copy_info)

        return calcinfo
        
    @classmethod
    def _render_input_string_from_params(cls, parameters):
        """
        Render the input string for the DMRG calculation from the input parameters.
        """
        # TODO
        return ""    
        
        
        
    

