from squadds import SQuADDS_DB
import pandas as pd
from squadds import Analyzer
import matplotlib.pyplot as plt
from squadds import AnsysSimulator


db = SQuADDS_DB()
db.select_system("qubit")
db.select_qubit("TransmonCross")
df = db.create_system_df()

analyzer = Analyzer(db)

# we are not actually looking for these Hamiltonian parameters... 
target_params={"qubit_frequency_GHz": 4, "anharmonicity_MHz": -200}

pred_df = analyzer.find_closest(target_params=target_params,
                                       num_top=1,
                                       metric="Euclidean",
                                       display=True)

ML_results = pd.read_csv("predictions_and_errors_unscaled_one_hot.csv") # real in ML test results

sample = 0 # choose testing device from ML results
this_device = ML_results[ML_results.sample_idx == sample]

um = 10**6

# reference/truth device parameters
ref_claw_length = str(this_device.ref_unscaled.iloc[0] * um)+'um' # grab device params, convert back to microns, and add unit labels
ref_ground_spacing = str(this_device.ref_unscaled.iloc[1] * um)+'um'
ref_cross_length = str(this_device.ref_unscaled.iloc[2] * um)+'um'

## reference/truth Hamiltonian parameters
ref_Hamiltonian_params = {"qubit_frequency_GHz":this_device.qubit_frequency_GHz.iloc[0],"anharmonicity_MHz":this_device.anharmonicity_MHz.iloc[0]}

# predicted device parameters
pred_claw_length = str(this_device.pred_unscaled.iloc[0] * um)+'um'
pred_ground_spacing = str(this_device.pred_unscaled.iloc[1] * um)+'um'
pred_cross_length = str(this_device.pred_unscaled.iloc[2] * um)+'um'

pred_df.design_options.iloc[0]["connection_pads"]["readout"]["claw_length"] = pred_claw_length
pred_df.design_options.iloc[0]["connection_pads"]["readout"]["ground_spacing"] = pred_ground_spacing
pred_df.design_options.iloc[0]["cross_length"] = pred_cross_length
pred_device = pred_df.iloc[0]

pred_ansys_simulator = AnsysSimulator(analyzer, pred_device)

pred_ansys_results = pred_ansys_simulator.simulate(pred_device)
pred_Hamiltonian_params = pred_ansys_simulator.get_xmon_info(pred_ansys_results)