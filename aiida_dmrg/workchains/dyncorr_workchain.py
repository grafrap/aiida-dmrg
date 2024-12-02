# DYNCORR_WORKCHAIN.PY
from aiida.engine import WorkChain, ToContext
from aiida.orm import Dict, RemoteData, Code
from aiida.plugins import CalculationFactory, WorkflowFactory

DMRGBaseWorkChain = WorkflowFactory('dmrg.base')
DynCorrCalculation = CalculationFactory('dyncorr')

class DynCorrWorkChain(WorkChain):
    """WorkChain that runs DMRG calculation followed by Dynamic Correlator calculation."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # codes
        spec.input("dmrg_code", valid_type=Code, help="The `dmrg` code.")
        spec.input("dyncorr_code", valid_type=Code, help="The `dyncorr` code.")

        # inputs
        spec.input("parent_calc_folder", valid_type=RemoteData, required=False, help="DMRG calculation folder")
        spec.input("dmrg_params", valid_type=Dict, help="DMRG parameters")
        spec.input("dyncorr_params", valid_type=Dict, help="Dynamic Correlator parameters")
        spec.input_namespace("options", valid_type=int, non_db=True, help="Define options for the calculation: walltime, memory, CPUs, etc.")
        # spec.expose_inputs(DMRGBaseWorkChain, namespace='dmrg')
        # spec.expose_inputs(DynCorrCalculation, namespace='dyncorr')

        spec.outline(
            # cls.setup,
            cls.run_dmrg,
            cls.run_dyncorr,
            cls.finalize
        )

        spec.output("time_measurement", valid_type=Dict)
        spec.output("output_matrix", valid_type=Dict)
        spec.outputs.dynamic = True

        spec.exit_code(400, "ERROR_DMRG_FAILED", message="DMRG calculation failed.")
        spec.exit_code(401, "ERROR_DYNCCORR_FAILED", message="Dynamic Correlator calculation failed.")

    def run_dmrg(self):
        self.report("Running DMRG calculation...")
        builder = DMRGBaseWorkChain.get_builder()
        builder.dmrg.code = self.inputs.dmrg_code
        builder.dmrg.metadata.options = self.inputs.options["dmrg"]
        builder.dmrg.parameters = self.inputs.dmrg_params
        
        if "parent_calc_folder" in self.inputs:
          builder.parent_calc_folder = self.inputs.parent_calc_folder

        dmrg_running = self.submit(builder)
        self.to_context(dmrg=dmrg_running)

    def run_dyncorr(self):
        self.report("Running Dynamic Correlator calculation...")

        # if not self.ctx.dmrg.is_finished_ok:
        #     self.report("DMRG calculation did not finish successfully.")
        #     return self.exit_codes.ERROR_DMRG_FAILED
        
        builder = DynCorrCalculation.get_builder()
        builder.parent_calc_folder = self.ctx.dmrg.outputs.remote_folder
        builder.code = self.inputs.dyncorr_code
        builder.parameters = self.inputs.dyncorr_params
        builder.options = self.inputs.options["dyncorr"]

        dyncorr_running = self.submit(builder)
        self.to_context(dyncorr=dyncorr_running)

    def finalize(self):
        ctx = self.ctx
        if not ctx.dyncorr.is_finished_ok:
            self.report("Dynamic Correlator calculation did not finish successfully.")
            return self.exit_codes.ERROR_DYNCCORR_FAILED

        self.out("time_measurement", ctx.dyncorr.outputs.time_measurement)
        self.out("output_matrix", ctx.dyncorr.outputs.output_matrix)