import Event
import pandas as pd


def flood_events(state_codes, tqdm, datapath):
    #Identify the events for multiple states for HUC level analysis
    # Define a list of state codes
    #state_codes = ['al', 'fl', 'ga', 'tn']  # Add other state codes as needed - note, 3 states was the limit for me to do,
    # state_codes = ['al', 'az', 'ar', 'ca', 'co', 'ct', 'fl', 'ga', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md',
    #                'ma', 'mi', 'mo', 'mt', 'ne', 'nv', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri','sc', 'tn', 'tx',
    #                'ut', 'va', 'wa', 'wv','wi', 'wy'] 

    # state_codes = ['al', 'az', 'ar', 'ca', 'co', 'ct', 'fl', 'ga', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md',
    #                'ma', 'mi', 'mo', 'mt', 'ne', 'nv', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'ri','sc', 'tn', 'tx',
    #                'ut', 'wa', 'wv','wi', 'wy'] 

    # Initialize an empty list to store dataframes for each state
    state_dfs = []
    #Merge site_id and site_code as well
    site_id = []
    site_code = []
    event_type = input("Enter the event type as 'flood' or 'drought': ")
    # Loop through each state code - connect to box
    for state in tqdm(state_codes):
        print('Getting data for ', state)
        #file_path = "C:/Users/malam24/OneDrive - The University of Alabama/Shahab/Git/SEED_v1.0/Data_1980-2020/NWIS_sites/" + state
        NWIS_path  = f"{datapath}/Data_1980-2020/NWIS_sites/{state}"
        events_data = Event.EVENT(NWIS_path, datapath, state, event_type)
        files = events_data.load_files()
        data = events_data.load_data(files)
        site_ids = events_data.site_id(NWIS_path, files)
        site_codes = events_data.site_code(site_ids)
        flood_values = events_data.flood_values(data, site_codes, event_type)
        df_flood_events = events_data.df_flood_events(flood_values)

        # Append the DataFrame for the current state to the list
        state_dfs.append(df_flood_events)
        site_id.append(site_ids)
        site_code.append(site_codes)

    # Concatenate all the state DataFrames into a single DataFrame
    merged_df = pd.concat(state_dfs, ignore_index=True)
    # Create a new list to store the combined elements
    merged_site_id = []
    merged_site_code = []
    # Use the extend method to add all elements to the combined_list
    merged_site_id.extend(data for data_list in site_id for data in data_list)
    merged_site_code.extend(data for data_list in site_code for data in data_list)

    # Save the merged DataFrame as a CSV file
    merged_df.to_csv(f"{datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/merged_flood_events.csv", index=False)

    # Optionally, you can print a message to confirm that the data has been saved
    print("Merged data saved as merged_flood_events.csv")
    return merged_df, merged_site_id, merged_site_code