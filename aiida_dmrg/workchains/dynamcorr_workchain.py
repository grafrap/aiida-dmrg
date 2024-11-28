# dyncorr_workchain.py
from aiida.engine import WorkChain, append_
from aiida.orm import Dict, RemoteData
from aiida.plugins import WorkflowFactory

DMRGBaseWorkChain = WorkflowFactory('dmrg.base')
DynCorrBaseWorkChain = WorkflowFactory('dyncorr.base')

class DynCorrWorkChain(WorkChain):
    """Workchain to run dynamic correlator calculations using DMRG results."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Expose all DMRG inputs
        spec.expose_inputs(
            DMRGBaseWorkChain, 
            namespace='dmrg',
            exclude=['max_iterations']
        )
        
        # Expose dynamic correlator inputs
        spec.expose_inputs(
            DynCorrBaseWorkChain,
            namespace='dyncorr',
            exclude=['parent_calc_folder']  # We'll get this from DMRG
        )

        spec.outline(
            cls.run_dmrg,
            cls.run_dyncorr,
            cls.results,
        )

        spec.outputs.dynamic = True


    def run_dmrg(self):
        """Run the DMRG calculation."""
        inputs = self.exposed_inputs(DMRGBaseWorkChain, namespace='dmrg')
        running = self.submit(DMRGBaseWorkChain, **inputs)
        return self.to_context(dmrg=running)

    def run_dyncorr(self):
        """Run the dynamic correlator calculation using DMRG results."""
        inputs = self.exposed_inputs(DynCorrBaseWorkChain, namespace='dyncorr')
        
        # Get remote folder from completed DMRG calculation
        inputs['parent_calc_folder'] = self.ctx.dmrg.outputs.remote_folder
        
        running = self.submit(DynCorrBaseWorkChain, **inputs)
        return self.to_context(dyncorr=running)

    def results(self):
        """Collect results from both calculations."""
        # Output DMRG results
        self.out_many(
            {f'dmrg_{key}': value 
             for key, value in self.ctx.dmrg.outputs.items()}
        )
        
        # Output dynamic correlator results
        self.out_many(
            {f'dyncorr_{key}': value 
             for key, value in self.ctx.dyncorr.outputs.items()}
        )