import numpy as np
import pandas as pd

def well_tvds(reservoir):
    """
    :param well_depth_array: input depth array for well
    :return: top and bottom TVD to be used in SodM and economic calculations
    """
    well_names = []
    well_top_tvd = []
    well_bottom_tvd = []
    well_mid_tvd = []

    for well in reservoir.wells:
    #     if 'E' in well.name:
    #         pass
    #     else:
        well_names.append(well.name)
        perf_top = well.perforations[0]
        perf_bottom = well.perforations[-1]
        well_top_tvd.append(reservoir.mesh.depth[perf_top[1]])
        well_bottom_tvd.append(reservoir.mesh.depth[perf_bottom[1]])
        well_mid_tvd.append(reservoir.mesh.depth[perf_top[1]] + (reservoir.mesh.depth[perf_bottom[1]] - reservoir.mesh.depth[perf_top[1]])/2)

    return(well_names, well_top_tvd, well_mid_tvd, well_bottom_tvd)

def drillingcostnl(depth):
    """
    Calculate the cost of drilling as a function of depth
    Reference source:
        https://www.thermogis.nl/en/economic-model

    :param depth: float
        measured depth along hole in meters

    :return: float
        costs in euros
    """
    drilling_cost_nl = 375000 + 1150 * depth + 0.3 * depth ** 2

    return(drilling_cost_nl)