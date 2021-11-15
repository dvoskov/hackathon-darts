from darts.models.reservoirs.struct_reservoir import StructReservoir
from darts.models.physics.geothermal import Geothermal
from darts.models.darts_model import DartsModel, sim_params
import numpy as np

from darts.engines import value_vector, redirect_darts_output


class Model(DartsModel):
    def __init__(self, n_points=128):
        # call base class constructor
        super().__init__()

        redirect_darts_output('log.txt')
        self.timer.node["initialization"].start()

        self.perm = 200
        self.poro = 0.2
        self.reservoir = StructReservoir(self.timer, nx=60, ny=40, nz=42, dx=30, dy=30, dz=2.5,
                                         permx=self.perm, permy=self.perm, permz=self.perm*0.1, poro=self.poro,
                                         depth=2150)
        hcap = np.array(self.reservoir.mesh.heat_capacity, copy=False)
        rcond = np.array(self.reservoir.mesh.rock_cond, copy=False)

        hcap.fill(2200)
        rcond.fill(181.44)

        self.reservoir.set_boundary_volume(xy_minus=30*30*400, xy_plus=30*30*400, yz_minus=8e9, yz_plus=8e9)

        self.physics = Geothermal(self.timer, n_points, 1, 351, 1000, 10000)

        self.params.first_ts = 1e-4
        self.params.mult_ts = 8
        self.params.max_ts = 365

        # Newton tolerance is relatively high because of L2-norm for residual and well segments
        self.params.tolerance_newton = 1e-2
        self.params.tolerance_linear = 1e-6
        self.params.max_i_newton = 20
        self.params.max_i_linear = 40

        self.params.newton_type = sim_params.newton_global_chop
        self.params.newton_params = value_vector([1])

        self.runtime = 0
        # self.physics.engine.silent_mode = 0
        self.timer.node["initialization"].stop()

    def set_initial_conditions(self):
        self.physics.set_uniform_initial_conditions(self.reservoir.mesh, uniform_pressure=200,
                                                    uniform_temperature=348.15)

    def set_boundary_conditions(self):
        for i, w in enumerate(self.reservoir.wells):
            if 'I' in w.name :
                w.control = self.physics.new_rate_water_inj(0, 348)
            else:
                w.control = self.physics.new_rate_water_prod(0)


    def set_op_list(self):
        self.op_list = [self.physics.acc_flux_itor, self.physics.acc_flux_itor_well]
        op_num = np.array(self.reservoir.mesh.op_num, copy=False)
        op_num[self.reservoir.mesh.n_res_blocks:] = 1

    def add_well(self, name, i_coord, j_coord):
        for w in self.reservoir.wells:
            if name == w.name:
                print("Warning! Well %s already exist." % name)
        self.reservoir.add_well(name)
        for n in range(5, 25):
            self.reservoir.add_perforation(well=self.reservoir.wells[-1], i=i_coord, j=j_coord, k=n+1,
                                           well_index=-1, multi_segment=False, verbose=False)

    def set_well_control(self, w, q_wat, p_bhp_min=50, p_bhp_max=450):
        if q_wat < 0.0:
            w.control = self.physics.new_rate_water_inj(-q_wat, [0.99])
            w.constraint = self.physics.new_bhp_water_inj(p_bhp_max, [0.99])
        else:
            w.control = self.physics.new_rate_water_prod(q_wat)
            w.constraint = self.physics.new_bhp_prod(p_bhp_min)

