import SEED
import pandas as pd



def fitted_values(datapath, updated_target_ids, analysis_level):

    #Fit Log Pearson Type 3 (LP3) distribution to the annual maximum series (AMS) for each USGS site within a State or HUCids

    if analysis_level == 'huc':
        #file_path = f"C:/Users/malam24/Box/Evaluation/LULC_Streamflow_SA/ROSET-AWS/ROSET-AWS/merged_flood_events.csv"
        file_path = f"{datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/merged_flood_events.csv"

    elif analysis_level == 'lulc': 
        location_input = input("Enter the location code (e.g., 'al', 'id', 'co'): ")
        # Change the file_path as per the actual location of the file on your desktop/laptop
        #file_path = f"C:/Users/malam24/OneDrive - The University of Alabama/Shahab/Git/SEED_v1.0/Data/Flood/df_flood_events_{location_input}.csv"
        file_path = f"{datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/df_flood_events_{location_input}.csv"

    column_name = "Yearly max"  # Replace with the flow column name

    # Use the updated_target_ids list
#     target_ids = updated_target_ids  # Replace target_ids_str with updated_target_ids
# Convert the list updated_target_ids to a space-separated string
    target_ids_str = " ".join(updated_target_ids)
    target_ids = [int(id) for id in target_ids_str.split()]  # Convert to a list of integers
    return_interval = int(input("Enter the return interval (e.g., 100): "))  # Return interval in years

    fitted_values = {}
    event_type = input("Enter event type either 'flood' or 'drought': ")
    
    for target_id in target_ids:
        # print(target_id) #Commented
        lp_fitting = SEED.SEED(file_path, column_name, target_id, event_type)
        data = lp_fitting.load_data()
        numeric_data = lp_fitting.numeric_data(data)

        flow_value = lp_fitting.fit_lp(numeric_data, return_interval, event_type)
        # Store the flow value in the dictionary with target_id as the key
        fitted_values[target_id] = flow_value

    # Convert the dictionary to a list of tuples
    data_tuples = list(fitted_values.items())

    # Create a DataFrame from the list of tuples with column names
    lp3_values = pd.DataFrame(data_tuples, columns=['Station', 'Estimated streamflow'])

    lp3_values.to_csv(f"{datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/lp3_values.csv", index=False)
    # print("Fitted Values:") #Commented

    for target_id, flow_value in fitted_values.items():
        print(f"Target ID: {target_id}, Return Interval: {return_interval} years, Flow Value: {flow_value}") #Commented
            
    return lp3_values