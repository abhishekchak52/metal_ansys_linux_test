from squadds.simulations.objects import run_capn_LOM 
from qiskit_metal.qlibrary.couplers.cap_n_interdigital_tee import CapNInterdigitalTee
from qiskit_metal import designs, Dict, MetalGUI
import pandas as pd
import numpy as np
import traceback

## read in ML results
ML_results = pd.read_csv("scripts/data/NCap_cap_data.csv")

'''read in SQuADDS coupler-NCap-cap_matrix dataset'''
ncap_db = pd.read_json("scripts/data/coupler-NCap-cap_matrix.json")

''' design and simulation setup parameters from DB '''
sim_setup = ncap_db.sim_options.iloc[0]
SQuADDS_design_params = ncap_db.design.iloc[0]["design_options"] # substitute ML predicted design params into here 

results = pd.DataFrame({"Sample":[],
                   "ref_cap_matrix":[],
                   "pred_cap_matrix":[]})

um = 10**6 ## ML model is trained in SI units (m), convert back to µm  
samples_to_test = np.unique(ML_results.sample_idx)

try:
    for sample in samples_to_test[:5]:

        ''' current testing sample '''
        this_device = ML_results[ML_results.sample_idx == sample]

        ''' extract predicted design parameters '''
        for param in np.unique(this_device.param):
            param_key = param.split(".")[1]
            design_value = this_device[this_device.param == param].pred_unscaled.iloc[0]
            
            if param_key == 'finger_count':
                SQuADDS_design_params[param_key] = np.round(design_value,0) 
            else:
                SQuADDS_design_params[param_key] = str(design_value*um)+"um"
            
        ''' create ML predicted design in Quantum (Qiskit) Metal '''
        design = designs.DesignPlanar()
        cplr = CapNInterdigitalTee(design,"NCap_{}".format(sample),options = SQuADDS_design_params)
        design.rebuild()

        ''' simulate predicted design '''
        pred_ansys_results = run_capn_LOM(design,cplr.options,sim_setup)

        pred_cap_matrix = pred_ansys_results[0]["sim_results"]

        # rename the keys to match the sim results keys to simplify analysis later
        ref_cap_matrix = {'C_top2top': this_device.top_to_top.iloc[0],
                        'C_top2bottom': this_device.top_to_bottom.iloc[0],
                        'C_top2ground': this_device.top_to_ground.iloc[0],
                        'C_bottom2bottom': this_device.bottom_to_bottom.iloc[0],
                        'C_bottom2ground': this_device.bottom_to_ground.iloc[0],
                        'C_ground2ground': this_device.ground_to_ground.iloc[0]}
        
        ''' save results '''
        results.loc[len(results)] = [sample,
                                    ref_cap_matrix,
                                    pred_cap_matrix]

except Exception:
    traceback.print_exc()
finally:
    print(results) 