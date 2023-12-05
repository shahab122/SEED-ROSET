import ROSET_AWS
import os
import warnings
warnings.filterwarnings("ignore")
#set path directory
cwd = os.getcwd()

def roset_setup(state, classification, HUCids):
    
    #Streamflow evaluator: State Class
    #Set desired start and end date, state, model for comparision, and LULC class
    startDT ='2019-5-24'
    endDT ='2019-8-24' #last day of data is 2020-09-28
#     state = 'ut'
    #the model name must match with the folder name in which model predictions are in.
    #model = 'NWM'
    model = 'NWM_v2.1'
#     classification = 'Drainage_area_mi2' #Change it to dictate the model what type of classication it should consider (see your choice in the previous cell)
    # classification = 'Perc_Forest'
    #Inititate Streamflow Evaluator
    State_Eval = ROSET_AWS.LULC_Eval(model, state, startDT, endDT, cwd)

    #get state specific NWIS locations
    State_Eval.get_NWIS()
    State_Eval.get_NHD_Model_info()
    State_Eval.class_eval_state(classification)

    # Interactive Streamflow plotting on map
        #Input temporal frequency, DF size, and DF size term -- make site name appear with mouse hover
    State_Eval.Map_Plot_Eval('D', State_Eval.df_small, 'small', supply = False)
    #Select your choice from the options given in the previous cell

    # Interactive Plotting
    State_Eval.Interactive_Model_Eval('D', supply = False)

    #Find the usgs ids within a State based on your choices (e.g., types of classification, categorical break, frequency) 
    lulc_usgs_ids = State_Eval.Eval.NWIS_site_id
    # HUC_Eval.Eval.NWIS_site_id
    lulc_usgs_ids

    #Streamflow evaluator: HUC Class
    #Enter a starting date, model for evaluation, and the respectrive HUC id(s)

    startDT ='2015-4-01'
    endDT ='2015-10-31'
    model = 'NWM_v2.1'
    # HUCids = ['1601', '1602'] #must be in brackets, add multiple HUCs to complete a watershed (e.g. GSL basin), East vs. West. etc
    # HUCids = ['1804', '1805', '1806']
#     HUCids = ['0314'] #, '0315']  Thwere w
    #0802 causing issues, is the state there?
    #Initiate function
    HUC_Eval = ROSET_AWS.HUC_Eval(model, HUCids, startDT, endDT, cwd)

    #Match NWIS locations within HUC watershed
    HUC_Eval.Join_WBD_StreamStats()

    #Get NWM reaches for each NWIS monitoring station
    HUC_Eval.get_NHD_Model_info()

    #Get NWM and NWIS data to compare
    HUC_Eval.prepare_comparison() # run the apply function to not have to run it during evaluation

    #Interactive plotting on map
    #Run Map function
    HUC_Eval.Map_Plot_Eval('D', supply = False)

    #Interactive time series plotting
    #Plot evaluation
    HUC_Eval.Interactive_Model_Eval('D', supply = False)

    #Find the usgs ids within a State based on your choices (e.g., HUCids) 
    huc_usgs_ids = HUC_Eval.Eval.NWIS_site_id
    huc_usgs_ids
    
    return lulc_usgs_ids, huc_usgs_ids

