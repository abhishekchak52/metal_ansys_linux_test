import traceback

from qiskit_metal import designs
from qiskit_metal import Dict

from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket
from qiskit_metal.qlibrary.tlines.meandered import RouteMeander

from qiskit_metal.analyses.quantization import EPRanalysis

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


epr1 = EPRanalysis(design, "hfss")

# example: update single setting
epr1.sim.setup.max_passes = 6
epr1.sim.setup.vars.Lj = "11 nH"
# example: update multiple settings
epr1.sim.setup_update(max_delta_f=0.4, min_freq_ghz=1.1)


try:
    epr1.sim.run(
        name="Qbit",
        components=["Q1"],
        open_terminations=[],
        box_plus_buffer=False,
    )
    epr1.setup.junctions.jj.rect = "JJ_rect_Lj_Q1_rect_jj"
    epr1.setup.junctions.jj.line = "JJ_Lj_Q1_rect_jj_"
    
    epr1.run_epr()
except Exception as e:
    traceback.print_exc()
finally:
    epr1.sim.close()
