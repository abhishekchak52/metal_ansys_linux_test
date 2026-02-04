from squadds import SQuADDS_DB
import pandas as pd
from squadds import Analyzer
from squadds import AnsysSimulator
import numpy as np
import traceback

''' grab SQuADDS entry as a template for ML predicted designs ''' 
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

''' read in ML results ''' 
ML_results = pd.read_csv("scripts/data/TransmonCross_cap_data.csv") # real in ML test results

# dictionary to save results in 
results = pd.DataFrame({"Sample":[],
                        "ref_design":[],
                        "pred_design":[],
                        "ref_H_params":[],
                        "ref_cap_matrix":[],
                        "pred_H_params":[],
                        "pred_cap_matrix":[]})

um = 10**6 ## ML model is trained in SI units (m), convert back to µm  
samples_to_test = np.arange(0,50)


try: 
    for sample in samples_to_test:

        ''' current testing sample '''
        this_device = ML_results[ML_results.sample_idx == sample]

        ''' get ML predicted design parameters '''
        # reference/truth device parameters
        ref_claw_length = str(this_device.ref_unscaled.iloc[0] * um)+'um' # grab device params, convert back to microns, and add unit labels
        ref_ground_spacing = str(this_device.ref_unscaled.iloc[1] * um)+'um'
        ref_cross_length = str(this_device.ref_unscaled.iloc[2] * um)+'um'
        
        # predicted device parameters
        pred_claw_length = str(this_device.pred_unscaled.iloc[0] * um)+'um'
        pred_ground_spacing = str(this_device.pred_unscaled.iloc[1] * um)+'um'
        pred_cross_length = str(this_device.pred_unscaled.iloc[2] * um)+'um'

        ''' create our predicted design option for Qiskit Metal '''
        pred_df.design_options.iloc[0]["connection_pads"]["readout"]["claw_length"] = pred_claw_length
        pred_df.design_options.iloc[0]["connection_pads"]["readout"]["ground_spacing"] = pred_ground_spacing
        pred_df.design_options.iloc[0]["cross_length"] = pred_cross_length
        pred_device = pred_df.iloc[0]

        ''' simulate predicted design '''
        pred_ansys_simulator = AnsysSimulator(analyzer, pred_device)
        pred_ansys_results = pred_ansys_simulator.simulate(pred_device)
        pred_capacitance_matrix = pred_ansys_results["sim_results"]
        
        print("Predicted Hamiltonian parameters:")
        pred_Hamiltonian_params = pred_ansys_simulator.get_xmon_info(pred_ansys_results) # get Hamiltonian parameters

        ''' save results '''
        ref_design = {"claw_length":ref_claw_length,"ground_spacing":ref_ground_spacing,"cross_length":ref_cross_length}
        pred_design = {"claw_length":pred_claw_length,"ground_spacing":pred_ground_spacing,"cross_length":pred_cross_length}

        # reference/truth capacitance parameters
        ref_capacitance_matrix = {"cross_to_ground":this_device.cross_to_ground.iloc[0],
                                "claw_to_ground":this_device.claw_to_ground.iloc[0],
                                "cross_to_claw":this_device.cross_to_claw.iloc[0],
                                "cross_to_cross":this_device.cross_to_cross.iloc[0],
                                "claw_to_claw":this_device.claw_to_claw.iloc[0],
                                "ground_to_ground":this_device.ground_to_ground.iloc[0],
                                "units":"fF"}
        
        # we don't want to use compute to simulate the pre-simulated design from SQuADDS, instead we make faux results to back out the Hamiltonian
        ref_ansys_simulator = AnsysSimulator(analyzer,None)
        ref_ansys_results = {"design": pred_ansys_results["design"], # only extracts Lj, doesn't change from pred & ref
                            "sim_options": pred_ansys_results["sim_options"], # only extracts Lj, doesn't change from pred & ref
                            "sim_results": ref_capacitance_matrix}
        
        print("Reference Hamiltonian parameters:")
        ref_Hamiltonian_params = ref_ansys_simulator.get_xmon_info(ref_ansys_results)
        
        results.loc[len(results)] = [sample,
                                    ref_design,
                                    pred_design,
                                    ref_Hamiltonian_params,
                                    ref_capacitance_matrix,
                                    pred_Hamiltonian_params,
                                    pred_capacitance_matrix]

except Exception:
    traceback.print_exc()
finally:
    print(results)