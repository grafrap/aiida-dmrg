"""Base workchain for DMRG calculations."""

from sys import _ExitCode
from aiida.common import AttributeDict
from aiida.engine import (
    BaseRestartWorkChain,
    ProcessHandlerReport,
    process_handler,
    while_,
)
from aiida.orm import Dict
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
            while_(cls.should_run_dmrg)(
                cls.run_dmrg,
            ),
        )

        spec.outputs.dynamic = True

        spec.exit_code(
            399,
            "ERROR_UNRECOVERABLE_TERMINATION",
            message="The calculation failed with an unrecoverable error.",
        )

    def setup(self):
        """Call the `setup` and create the inputs dictionary in `self.ctx.inputs`.

        This `self.ctx.inputs` dictionary will be used by the `BaseRestartWorkChain` to
        submit the calculations in the internal loop.
        """
        super().setup()
        self.ctx.inputs = AttributeDict(
            self.exposed_inputs(DMRGCalculation, 'dmrg')
        )

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

        return _ExitCode(0)
    
    # TODO: implement handling of errors

    def results(self):
        """Overload the method such that each dynamic output of the DMRG calculation is set."""
        node = self.ctx.children[self.ctx.iteration - 1]

        # We check the `is_finished` attribute of the work chain and not the successfulness of the last process
        # because the error handlers in the last iteration can have qualified a "failed" process as satisfactory
        # for the outcome of the work chain and so have marked it as `is_finished=True`.
        max_iterations = self.inputs.max_iterations.value  # type: ignore[union-attr]
        if not self.ctx.is_finished and self.ctx.iteration >= max_iterations:
            self.report(
                f"reached the maximum number of iterations {max_iterations}: "
                f"last ran {self.ctx.process_name}<{node.pk}>"
            )
            return (
                self.exit_codes.ERROR_MAXIMUM_ITERATIONS_EXCEEDED
            )  # pylint: disable=no-member

        self.report(f"The work chain completed after {self.ctx.iteration} iterations")

        # self.out_many({key: node.outputs[key] for key in node.outputs})

        return None