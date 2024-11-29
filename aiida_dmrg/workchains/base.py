"""Base workchain for DMRG calculations."""

from aiida.common import AttributeDict
from aiida.engine import (
    BaseRestartWorkChain,
    ProcessHandlerReport,
    process_handler,
    while_,
)
from aiida.orm import Dict, RemoteData
from aiida.plugins import CalculationFactory, DataFactory

DMRGCalculation = CalculationFactory('dmrg')


class DMRGBaseWorkChain(BaseRestartWorkChain):
    """Base workchain for DMRG calculations."""

    _process_class = DMRGCalculation

    @classmethod
    def define(cls, spec):
        
        super().define(spec)
        spec.expose_inputs(DMRGCalculation, namespace='dmrg')

        spec.outline(
            cls.setup,
            cls.run_dmrg,
            cls.store_remote_folder,
        )
        

        spec.output('remote_folder', valid_type=RemoteData, required=True)

        spec.outputs.dynamic = True


    def setup(self):
        """Call the `setup` and create the inputs dictionary in `self.ctx.inputs`.

        This `self.ctx.inputs` dictionary will be used by the `BaseRestartWorkChain` to
        submit the calculations in the internal loop.
        """
        super().setup()
        self.ctx.inputs = self.exposed_inputs(DMRGCalculation, 'dmrg')
        self.ctx.remote_folder = None

    @process_handler(priority=400, exit_codes=[
        DMRGCalculation.exit_codes.ERROR_UNPHYISCAL_INPUT,
        DMRGCalculation.exit_codes.ERROR_TERMINATION,
    ])
    def inspect_dmrg(self, node):
        """Verify that the DMRG calculation finished successfully."""
        
        try:
            if not node.is_finished_ok:
                self.report(f"calculation failed with exit status {node.exit_status}")
                return self.exit_codes.ERROR_TERMINATION
        except Exception as e:
            self.report(f"calculation failed with exception: {e}")
            return self.exit_codes.ERROR_UNPHYISCAL_INPUT

        return ProcessHandlerReport(True)
    
    def run_dmrg(self):
        """Run the DMRG calculation."""
        inputs = self.ctx.inputs
        return self.submit(DMRGCalculation, **inputs)
    
    def store_remote_folder(self):
        """Store the remote folder output."""
        if self.ctx.dmrg and self.ctx.dmrg.outputs.remote_folder:
            self.out('remote_folder', self.ctx.dmrg.outputs.remote_folder)
        else:
            self.report('DMRG workchain did not provide a remote_folder.')
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER
