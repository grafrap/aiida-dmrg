# dyncorr_base.py
from aiida.engine import BaseRestartWorkChain
from aiida.orm import Dict
from aiida.plugins import CalculationFactory

DynCorrCalculation = CalculationFactory('dyncorr')

class DynCorrBaseWorkChain(BaseRestartWorkChain):
    """Base workchain for dynamic correlator calculations."""

    _process_class = DynCorrCalculation

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(DynCorrCalculation)
        
        spec.outline(
            cls.setup,
            cls.run_calculation,
            cls.inspect_calculation,
            cls.results,
        )

        spec.outputs.dynamic = True

    def setup(self):
        """Initialize the workchain."""
        super().setup()
        self.ctx.restart_calc = None

    def run_calculation(self):
        """Run the calculation."""
        return super()._run_process_with_handlers(DynCorrCalculation)

    def inspect_calculation(self):
        """Check calculation results."""
        return self.ctx.children[self.ctx.iteration - 1]

    def results(self):
        """Set the workchain outputs."""
        calculation = self.ctx.children[self.ctx.iteration - 1]
        self.out_many(calculation.outputs)