import traceback

from qiskit_metal import designs
from qiskit_metal import Dict

from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket
from qiskit_metal.qlibrary.tlines.meandered import RouteMeander
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround

from qiskit_metal.analyses.quantization import EPRanalysis

"""
Create a design with a transmon and a readout resonator.
The readout resonator is connected to the transmon and the other end is connected to an open to ground termination.
"""

design = designs.DesignPlanar({}, True)
design.chips.main.size["size_x"] = "2mm"
design.chips.main.size["size_y"] = "2mm"


q1 = TransmonPocket(
    design,
    "Q1",
    options=dict(
        pad_width="425 um",
        pocket_height="650um",
        connection_pads=dict(readout=dict(loc_W=+1, loc_H=+1, pad_width="200um")),
    ),
)



otg = OpenToGround(design, 'open_to_ground', options=dict(pos_x='1.75mm',  pos_y='0um', orientation='0'))
RouteMeander(design, 'readout',  Dict(
        total_length='6 mm',
        hfss_wire_bonds = True,
        fillet='90 um',
        lead = dict(start_straight='100um'),
        pin_inputs=Dict(
            start_pin=Dict(component='Q1', pin='readout'),
            end_pin=Dict(component='open_to_ground', pin='open')), ))


"""
Run the EPR analysis on the design.
"""

epr1 = EPRanalysis(design, "hfss")

# example: update single setting
epr1.sim.setup.n_modes = 2
epr1.sim.setup.max_passes = 25
epr1.sim.setup.vars.Lj = "11 nH"
print(epr1.sim.setup)
# example: update multiple settings
epr1.sim.setup_update(max_delta_f=0.4, min_freq_ghz=1.1)


try:
    epr1.sim.run(name="TransmonResonator",
                 components=['Q1', 'readout', 'open_to_ground'],
                 open_terminations=[('readout', 'end')])
    
    epr1.setup.junctions.jj.rect = "JJ_rect_Lj_Q1_rect_jj"
    epr1.setup.junctions.jj.line = "JJ_Lj_Q1_rect_jj_"
    print(epr1.setup)
    
    epr1.run_epr()
except Exception as e:
    traceback.print_exc()
finally:
    epr1.sim.close()
