from squadds import SQuADDS_DB
import pandas as pd
from squadds import Analyzer
from squadds import AnsysSimulator
import numpy as np
import traceback
from tqdm import tqdm
from comparison_df_utils import create_comparison_dataframe

''' grab SQuADDS entry as a template for ML predicted designs ''' 
db = SQuADDS_DB()
db.select_system(["qubit","cavity_claw"])
db.select_qubit("TransmonCross")
db.select_cavity_claw("RouteMeander")
db.select_resonator_type("quarter")
df = db.create_system_df()
analyzer = Analyzer(db)

# we are not actually looking for these Hamiltonian parameters... 
target_params={"qubit_frequency_GHz": 4,"anharmonicity_MHz": -200,"cavity_frequency_GHz":6.2,"kappa_kHz":20,"g_MHz":70}

pred_df = analyzer.find_closest(target_params=target_params,
                                       num_top=1,
                                       metric="Euclidean",
                                       display=True)

''' read in ML results ''' 
ML_results_total = pd.read_csv("scripts/data/RouteMeander_eigenmode_data.csv") # real in ML test results


''' for now we only want to consider predicted quarter wavelength resonators ''' 
ML_results = ML_results_total.iloc[0:0].copy()
for i in np.unique(ML_results_total.sample_idx):
    temp_df = ML_results_total[ML_results_total.sample_idx == i]

    if temp_df[temp_df.param == 'resonator_type_half'].ref_unscaled.iloc[0] == 1: # do not keep half wavelength resonators
        continue
    else:
        ML_results = pd.concat([ML_results, temp_df])

# dictionary to save results in 
results = pd.DataFrame({"Sample":[],
                   "ref_H_params":[],
                   "pred_H_params":[]})

um = 10**6 ## ML model is trained in SI units (m), convert back to µm  

unique_sample_idx = np.unique(ML_results.sample_idx)
if len(unique_sample_idx) > 3:
    samples_to_test = np.sort(unique_sample_idx)[:3]
else: 
    samples_to_test = np.sort(unique_sample_idx)


try: 
    for sample in tqdm(samples_to_test):
            
        ''' current testing sample '''
        this_device = ML_results[ML_results.sample_idx == sample]

        ''' create our predicted design option for Qiskit Metal '''
        for param in np.unique(this_device.param):

            if int(this_device[this_device.param == param].exists_pred_mask) == 1:

                param_keys = param.split(".")[1:]
                param_value = str(float((this_device[this_device.param == param].pred_unscaled))*um)+"um"

                if len(param_keys) == 2:
                    pred_df.design_options_cavity_claw.iloc[0][param_keys[0]][param_keys[1]] = param_value
                elif len(param_keys) == 3:
                    pred_df.design_options_cavity_claw.iloc[0][param_keys[0]][param_keys[1]][param_keys[2]] = param_value
                elif len(param_keys) == 4:
                    pred_df.design_options_cavity_claw.iloc[0][param_keys[0]][param_keys[1]][param_keys[2]][param_keys[3]] = param_value

        ''' simulate predicted design '''
        pred_ansys_simulator = AnsysSimulator(analyzer, pred_df.iloc[0])
        pred_ansys_results = pred_ansys_simulator.simulate(pred_df.iloc[0])

        pred_Hamiltonian_params = {'cavity_frequency_GHz':pred_ansys_results["sim_results"]["cavity_frequency_GHz"],
                                'kappa_kHz':pred_ansys_results["sim_results"]['kappa_kHz']}
        ref_Hamiltonian_params = {'cavity_frequency_GHz':this_device.cavity_frequency.iloc[0],
                                'kappa_kHz':this_device.kappa.iloc[0]}
        
        ''' save results '''
        results.loc[len(results)] = [sample,
                                    ref_Hamiltonian_params,
                                    pred_Hamiltonian_params]

except Exception:
    traceback.print_exc()
finally:
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(create_comparison_dataframe(results))