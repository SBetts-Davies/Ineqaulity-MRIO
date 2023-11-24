# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 11:16:00 2023

@author: unisbet
"""

import pandas as pd
import numpy as np
import io_functions as io
import LCF_functions_2022 as lcf
import pickle

from RE_functions import linear_interpolation, logistic_interpolation, reform_Y, \
alter_U, alter_Y, calc_new_outputs, set_Y_from_growth, calc_L_A, project_Z_X, sector_split, \
run_strategies, driver_override, project_Z_X_dom_prop, strategies_check, save_intermediate_results, save_intermediate_results_individual, \
footprints

years = np.arange(2020, 2021)

print('Readings MRIO data...')
    
MRIO_input_filepath = 'C:/Users/sambe/Downloads/OneDrive - University of Leeds/2022_inputs/' # means we dont have to type out the file path every time
#MRIO_result_filepath = 'C:/Users/unisbet/OneDrive - University of Leeds/mrio_modelling/' 
# stored truncated versions of MRIO data with only 2019 so loads faster - not actually sure this is doing that tho. Do i need to make new seperate variables for these that only includes 2019 data. 
S, U, Y_base, ghg, ghg_direct, nrg, nrg_direct = {}, {}, {}, {}, {}, {}, {}
S = pd.read_pickle(MRIO_input_filepath+'S.p')
U = pd.read_pickle(MRIO_input_filepath+'U.p')
Y_base = pd.read_pickle(MRIO_input_filepath+'Y.p')
ghg = pd.read_pickle(MRIO_input_filepath+'ghg.p')
ghg_direct= pd.read_pickle(MRIO_input_filepath+'uk_ghg_direct.p')
nrg = pd.read_pickle(MRIO_input_filepath+'nrg.p')
nrg_direct = pd.read_pickle(MRIO_input_filepath+'uk_nrg_direct.p')
concs_dict = pd.read_excel(MRIO_input_filepath + 'ONS_to_COICOP_LCF_concs.xlsx', sheet_name=None, index_col=0)
meta = pickle.load( open(MRIO_input_filepath + "meta.p", "rb" ) )
hhspenddata = pickle.load( open(MRIO_input_filepath + "hhspenddata.p", "rb" ) )

print('Processing MRIO data...')

ind_prod_list = list(U[2019].columns)+list(U[2019].index) # cant get this to load currently - get error "AttributeError: 'dict' object has no attribute 'columns'"

# reassign Y to basic COICOP and split to detailed COICOP - think these need to be changed to account for 112 sectors - couldnt find new in LCF
Y = lcf.convert43to41(Y_base,concs_dict,[2019])  # changed this from 43to40 to 43to41 because that was the file in 
total_Yhh_112 = lcf.make_y_hh_112(Y,coicop_exp_tot3,years,concs_dict,meta)
coicop_exp_tot = lcf.make_totals(hhspenddata,[2019])
coicop_exp_tot2 = lcf.make_balanced_totals(coicop_exp_tot,total_Yhh_112,concs_dict,[2019])
yhh_wide = lcf.make_y_hh_307(Y,coicop_exp_tot2,[2019],concs_dict,meta)
Y_COICOP = lcf.make_new_Y(Y,yhh_wide,meta,[2019])

temp_UKghgfoot = {}

Z = io.make_Z_from_S_U(S[2019],U[2019])
bigY = io.make_bigY(Y_base[2019],S[2019],U[2019])
x = io.make_x(Z,bigY)
L = io.make_L(Z,x)
bigstressor = io.make_bigstressor(ghg[2019],S[2019],U[2019])
e = io.make_e(bigstressor,x) 
temp_UKghgfoot = np.dot(np.dot(e,L),np.sum(bigY[:,0:42],1))+ghg_direct.loc['Consumer expenditure - not travel',2019]+ghg_direct.loc['Consumer expenditure - travel',2019]
