import numpy as np

class DMRG:
    def __init__(
            self,
            title=None,
            comment=None,
            S=1,
            N_sites=None,
            J=None,
            Sz=0,
            n_excitations=0,
            conserve_symmetry=False,
            print_HDF5=False,
    ):
        self.title = title
        self.comment = comment
        self.S = S
        self.N_sites = N_sites
        self.J = J
        self.Sz = Sz
        self.n_excitations = n_excitations
        self.conserve_symmetry = conserve_symmetry
        self.print_HDF5 = print_HDF5

    @classmethod
    def from_file_handle(cls, file_handle, read_data=True):
        f = file_handle
        c = cls()
        c.title = f.readline().rstrip()
        c.comment = f.readline().rstrip()

        line = f.readline().split()
        c.S = float(line[0])
        c.N_sites = int(line[1])

        line = f.readline()
        c.J = np.zeros((c.N_sites, c.N_sites)) # TODO: distinguish between one J value and a matrix from input file

        line = f.readline().split()
        c.Sz = float(line[0])
        c.n_excitations = int(line[1])
        c.conserve_symmetry = bool(int(line[2]))
        c.print_HDF5 = bool(int(line[3]))

        return c
    
    @classmethod
    def from_file(cls, filepath):
        with open(filepath) as f:
            return cls.from_file_handle(f)
        
        
        

