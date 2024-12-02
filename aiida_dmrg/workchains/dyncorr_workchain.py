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
        spec.expose_inputs(DMRGBaseWorkChain, namespace='dmrg')
        spec.expose_inputs(DynCorrCalculation, namespace='dyncorr')

        spec.outline(
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
        inputs = {**self.exposed_inputs(DMRGBaseWorkChain, 'dmrg')}
        running = self.submit(DMRGBaseWorkChain, **inputs)
        return ToContext(dmrg=running)

    def run_dyncorr(self):
        self.report("Running Dynamic Correlator calculation...")
        ctx = self.ctx
        if not ctx.dmrg.is_finished_ok:
            self.report("DMRG calculation did not finish successfully.")
            return self.exit_codes.ERROR_DMRG_FAILED

        self.inputs.dyncorr.dmrg_folder = ctx.dmrg.outputs.remote_folder
        dyncorr_inputs = {
            'parameters': ctx.dmrg.inputs.parameters,
            'parent_calc_folder': dmrg_folder,
            **self.exposed_inputs(DynCorrCalculation, 'dyncorr')
        }

        running = self.submit(DynCorrCalculation, **dyncorr_inputs)
        return ToContext(dyncorr=running)

    def finalize(self):
        ctx = self.ctx
        if not ctx.dyncorr.is_finished_ok:
            self.report("Dynamic Correlator calculation did not finish successfully.")
            return self.exit_codes.ERROR_DYNCCORR_FAILED

        self.out("time_measurement", ctx.dyncorr.outputs.time_measurement)
        self.out("output_matrix", ctx.dyncorr.outputs.output_matrix)