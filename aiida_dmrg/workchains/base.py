"""Base workchain for DMRG calculations."""

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
                cls.inspect_dmrg,
            ),
            cls.results,
        )

        spec.outputs.dynamic = True

        spec.exit_code(
            350,
            "ERROR_UNRECOVERABLE_SCF_FAILURE",
            message="The calculation failed with an unrecoverable SCF convergence error.",
        )

        spec.exit_code(
            399,
            "ERROR_UNRECOVERABLE_TERMINATION",
            message="The calculation failed with an unrecoverable error.",
        )