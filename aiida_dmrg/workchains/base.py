"""Base workchain for DMRG calculations."""

from aiida.engine import (  # noqa: E501
    BaseRestartWorkChain,
    ProcessHandlerReport,
    process_handler,
)
from aiida.orm import RemoteData
from aiida.plugins import CalculationFactory

DMRGCalculation = CalculationFactory("dmrg")


class DMRGBaseWorkChain(BaseRestartWorkChain):
    """Base workchain for DMRG calculations."""

    _process_class = DMRGCalculation

    @classmethod
    def define(cls, spec):

        super().define(spec)
        spec.expose_inputs(DMRGCalculation, namespace="dmrg")

        spec.outline(
            cls.setup,
            cls.run_dmrg,
            cls.finalize,
        )

        spec.output("remote_folder", valid_type=RemoteData, required=True)

        spec.outputs.dynamic = True

    def setup(self):
        """Call the `setup` and create the inputs dictionary
        in `self.ctx.inputs`.

        This `self.ctx.inputs` dictionary will be used by
        the `BaseRestartWorkChain` to submit the calculations
        in the internal loop.
        """
        super().setup()
        self.ctx.inputs = self.exposed_inputs(DMRGCalculation, "dmrg")
        self.ctx.remote_folder = None

    @process_handler(
        priority=400,
        exit_codes=[
            DMRGCalculation.exit_codes.ERROR_UNPHYISCAL_INPUT,
            DMRGCalculation.exit_codes.ERROR_TERMINATION,
        ],
    )
    def inspect_dmrg(self, node):
        """Verify that the DMRG calculation finished successfully."""
        node = self.ctx.dmrg
        try:
            if not node.is_finished_ok:
                self.report(
                    f"""calculation failed with
                             exit status {node.exit_status}"""
                )
                return self.exit_codes.ERROR_TERMINATION
        except Exception as e:
            self.report(f"calculation failed with exception: {e}")
            return self.exit_codes.ERROR_UNPHYISCAL_INPUT

        return ProcessHandlerReport(True)

    def run_dmrg(self):
        """Run the DMRG calculation."""
        builder = DMRGCalculation.get_builder()

        builder.code = self.inputs.dmrg.code
        builder.parameters = self.inputs.dmrg.parameters
        if self.ctx.remote_folder is not None:
            builder.parent_calc_folder = self.ctx.remote_folder
        builder.metadata.options = self.ctx.inputs.metadata.options
        self.report("Submitting DMRG calculation.")
        self.to_context(dmrg=self.submit(builder))

    def finalize(self):
        """Finalize the workchain."""
        self.ctx.remote_folder = self.ctx.dmrg.outputs.remote_folder
        self.out("remote_folder", self.ctx.remote_folder)

        self.report("DMRG workchain completed successfully")
