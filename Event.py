# #!/usr/bin/env python
# # coding: utf-8

# # In[ ]:


# #Import the packages
# import pandas as pd
# import glob
# import os
# import numpy as np
# import scipy.stats as scs
# from scipy.stats import pearson3, skew, norm
# import matplotlib.pyplot as plt 
# from tqdm import tqdm
# import warnings
# warnings.filterwarnings("ignore")

# class EVENT:
#     def __init__(self, file_path, datapath, state, event_type):
#         self.file_path = file_path
#         self.datapath = datapath
#         self.state = state
#         self.event_type = event_type
# #         self.station_id = station_id
        
#     def load_files(self):
#         print('Loading files...')
#         all_files = glob.glob(os.path.join(self.file_path , "*.csv"))
#         return all_files
    
#     def load_data(self, all_files):
#         print('Loading data from files...')
#         temp_files = []
#         for filename in tqdm(all_files):
#             data_files  = pd.read_csv(filename, index_col=None, header=0)
#             temp_files.append(data_files)
            
#         all_flow = pd.concat(temp_files, axis=0, ignore_index=True)
#         all_flow = all_flow.dropna() # removing the missing values
#         all_flow = all_flow[(all_flow['USGS_flow']>0)]
#         np.min(all_flow['USGS_flow'])
        
#         #Change the datetime in the dataframe
#         all_flow['Datetime'] = pd.to_datetime(all_flow['Datetime'])
#         all_flow.dtypes
#         all_flow['USGS_flow']
#         return all_flow
    
#     def site_id(self, file_path, all_files):
#         print('Getting site ids...')
#         #Find the station ID
#         site_id = []

#         # Loop through the file paths and extract the site code
#         for file_path in all_files:
#             # Split the file path into directory path and filename
#             dir_path, file_name = os.path.split(file_path)

#             # Split the filename into the site code and the file extension
#             site_id1, ext = os.path.splitext(file_name)

#             # Extract the site code from the site code string
#             site_id.append(site_id1.split("_")[0])
#         return site_id
    
#     def site_code(self, site_id):
#         print('Fixing applicable site codes...')
#         #Site_code = site_id (station id) without the unnecessary zeros at the beginning 
#         #(select the meaning numbers only, e.g., 968674521 instead of 00968674521)
#         site_code = []
#         for i in range(len(site_id)):
#             site  = str(site_id[i])
#             if site[0] == '0':
#                 site_code.append(site[-7:]) #Change it with the following line depending on the station ID length
#             else:
#                 site_code.append(site[-8:]) #Change it with the above line depending on the station ID length

#         site = []
#         for i in range(len(site_code)): 
#             site.append(int(site_code[i]))
#         site_code = site
#         range(len(site_code))
#         return site_code
    
# #     def flood_values(self, all_flow, site_code):
# #         print('Calculating flood values...')
# #         #Select annual maximum streamflow from the entire dataset (all_flow) for each site_code, calculate exceedance probability,and
# #         # Calculate return period
# #         flood_values = {}

# #         m= 0
# #         # Subset the DataFrame based on the values in the 'city' column
# #         for i in range(len(site_code)):
# #             subset = all_flow.loc[all_flow['USGS_ID'] == site_code[i]]
# #             subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce') #Uncomment this line if the following line fails
# #             #     max_data = subset.groupby(subset.Datetime.dt.year)['USGS_flow'].max() # Selected by year
# #             max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmax().values] # Selected by date of occurance
# #             max_data = max_data[["Datetime", "USGS_flow"]]
# #             max_data = max_data.reset_index(drop=True)
    
# #             sort_data  = max_data.sort_values('USGS_flow', ascending = True)
# #             sorted_data = sort_data['USGS_flow']

# #             sorted_date = sort_data['Datetime']

# #             #Calculate exceedance probability
# #             Pr = []
# #             Tp = []  
# #             for j in range(1,len(sorted_data)+1):
# #                 Pr.append((j/(len(sorted_data)+1))*100)
   
# #             for n in range(len(Pr)):
# #                 Tp.append(1/(Pr[n]/100))
    
# #             #Save the above results as a dictionary 
# #             dict_list = [{'Date': sorted_date}, {'Yearly max': sorted_data}, {'Exceedance probability': Pr}, {'Return periods': Tp}]
# #             k = site_code[m]
# #             key = f'dict_{k}'
# #             flood_values[key] = dict_list
# #             m +=1
# #         return flood_values

#     def flood_values(self, all_flow, site_code, event_type):
#         print(f'Calculating {event_type} values...')
#         # Select either annual maximum or minimum streamflow from the entire dataset (all_flow) for each site_code,
#         # calculate exceedance probability, and calculate return period
#         flood_values = {}

#         m = 0
#         # Subset the DataFrame based on the values in the 'city' column
#         for i in range(len(site_code)):
# #             subset = all_flow.loc[all_flow['USGS_ID'] == site_code[i]
# #             subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce')
#             subset = all_flow.loc[all_flow['USGS_ID'] == site_code[i]]

#             subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce') #Uncomment this line if the following line fails

#             if event_type == 'flood':
#                 max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmax().values]  # Selected by date of occurrence
#             elif event_type == 'drought':
#                 max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmin().values]  # Selected by date of occurrence
#             else:
#                 raise ValueError("Invalid value_type. Use 'flood' or 'drought'.")

#             max_data = max_data[["Datetime", "USGS_flow"]]
#             max_data = max_data.reset_index(drop=True)
            
#             if event_type == 'flood':
#                 sort_data = max_data.sort_values('USGS_flow', ascending=True)
#             elif event_type == 'drought':
#                 sort_data = max_data.sort_values('USGS_flow', ascending=True)
                
#             sorted_data = sort_data['USGS_flow']
#             sorted_date = sort_data['Datetime']

#             # Calculate exceedance probability
#             Pr = []
#             Tp = []
#             for j in range(1, len(sorted_data) + 1):
#                 Pr.append((j / (len(sorted_data) + 1)) * 100)

#             for n in range(len(Pr)):
#                 Tp.append(1 / (Pr[n] / 100))

#             # Save the above results as a dictionary
#             dict_list = [{'Date': sorted_date}, {'Yearly max': sorted_data}, {'Exceedance probability': Pr}, {'Return periods': Tp}]
#             k = site_code[m]
#             key = f'dict_{k}'
#             flood_values[key] = dict_list
#             m += 1

#         return flood_values

#     def df_flood_events(self, flood_values):
#         print('Getting flood events...')
#         #Prepare the dataframe from the above huge dictionary to save as a csv file for each state containing all stations (site_id)
#         # create an empty dataframe
#         df = pd.DataFrame(columns=['Station', 'Date', 'Yearly max', 'Exceedance probability', 'Return periods'])

#         # iterate over the keys and values of the dictionary
#         for station, data in flood_values.items():
#             # get the yearly max data from the dictionary
#             yearly_max = data[1]['Yearly max']
    
#             # create a new dataframe with the yearly max data
#             df_new = pd.DataFrame({'Yearly max': yearly_max[::-1]})
#             #     df_new = pd.DataFrame({'Yearly max': yearly_max})
    
#             # add the station name to the dataframe
#             site  = str(station)
#             numeric_site = ''.join(filter(str.isdigit, site))  # Filter out non-numeric characters
#             if len(numeric_site) == 7:
#                 new_station = numeric_site #Change it with the following line depending on the station ID length
#             else: 
#                 new_station = numeric_site[-8:] #Change it with the above line depending on the station ID length
#             df_new['Station'] = new_station

#             # get the other data from the dictionary
#             exceedance_prob = data[2]['Exceedance probability']
#             return_periods = data[3]['Return periods']
#             date = data[0]['Date']
    
#             # add the other data to the dataframe
#             df_new['Exceedance probability'] = exceedance_prob
#             df_new['Return periods'] = return_periods
#             df_new['Date'] = date
    
#             # append the new dataframe to the main dataframe
#             # df = df.append(df_new, ignore_index=True)  
#             df = pd.concat([df, df_new], ignore_index=True)
        
#         df_flood_events = df
#         df_flood_events.to_csv(f"{self.datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/df_flood_events_{self.state}.csv", index=False)
#         return df_flood_events
    
#     def station_data(self, site_code):
#         print('Loading station data...')
#         #Read the csv just constructed using above command 
#         df = pd.read_csv(f"{self.datapath}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/df_flood_events.csv")
#         #Select rows from the imported csv file corresponding to the station id
#         station_rows = df[df['Station'] == site_code[1]]
#         station_data = station_rows['Yearly max']
#         return station_data
    
 
 
###########################
#######################################
######### Modified ################## 
######## 10/11/2025 ###################

#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import glob
import os
import numpy as np
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")


class EVENT:
    def __init__(self, file_path, datapath, state, event_type):
        self.file_path = file_path
        self.datapath = datapath
        self.state = state
        self.event_type = event_type.lower().strip()  # ensure lowercase
        if self.event_type not in ["flood", "drought"]:
            raise ValueError("❌ event_type must be 'flood' or 'drought'")

    # ============================================================
    # === LOAD FILES AND DATA ===
    # ============================================================
    def load_files(self):
        print(f"📂 Loading files from {self.file_path} ...")
        all_files = glob.glob(os.path.join(self.file_path, "*.csv"))
        if not all_files:
            print(f"⚠️ No CSV files found in {self.file_path}")
        return all_files

    def load_data(self, all_files):
        print("📘 Loading data from files...")
        temp_files = []
        for filename in tqdm(all_files, desc=f"Reading {self.state} files"):
            try:
                df = pd.read_csv(filename)
                if "Datetime" not in df.columns or "USGS_flow" not in df.columns:
                    print(f"⚠️ Skipped malformed file: {filename}")
                    continue
                df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
                df = df.dropna(subset=["Datetime", "USGS_flow"])
                df = df[df["USGS_flow"] > 0]
                temp_files.append(df)
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
                continue

        if not temp_files:
            print(f"⚠️ No valid flow data loaded for {self.state}")
            return pd.DataFrame()

        all_flow = pd.concat(temp_files, axis=0, ignore_index=True)
        print(f"✅ Loaded {len(all_flow)} rows for {self.state}")
        return all_flow

    # ============================================================
    # === SITE IDS AND FORMATTING ===
    # ============================================================
    def site_id(self, file_path, all_files):
        print("🔹 Extracting site IDs from filenames...")
        site_id = []
        for path in all_files:
            _, file_name = os.path.split(path)
            site_id1, _ = os.path.splitext(file_name)
            site_id.append(site_id1.split("_")[0])
        return site_id

    def site_code(self, site_id):
        """Ensure all site codes are 8-digit zero-padded strings."""
        print("🔹 Formatting site codes (ensuring 8 digits)...")
        site_code = []
        for sid in site_id:
            sid = str(sid).strip().split("_")[0]
            sid = sid.zfill(8)  # always 8 digits
            site_code.append(sid)
        return site_code

    # ============================================================
    # === COMPUTE FLOOD / DROUGHT EVENTS ===
    # ============================================================
    def flood_values(self, all_flow, site_code, event_type):
        print(f"💧 Calculating {event_type} event statistics...")
        if all_flow.empty:
            print("⚠️ No flow data available — skipping event computation.")
            return {}

        flood_values = {}
        m = 0

        # Standardize ID column for matching
        all_flow["USGS_ID"] = all_flow["USGS_ID"].astype(str).str.zfill(8)

        for i in range(len(site_code)):
            sid = site_code[i]
            subset = all_flow.loc[all_flow["USGS_ID"] == sid].copy()
            if subset.empty:
                continue

            subset["USGS_flow"] = pd.to_numeric(subset["USGS_flow"], errors="coerce")
            subset = subset.dropna(subset=["USGS_flow"])

            # Group by year and pick annual max (flood) or min (drought)
            if event_type == "flood":
                sel = subset.loc[subset.groupby(subset["Datetime"].dt.year)["USGS_flow"].idxmax().values]
            else:
                sel = subset.loc[subset.groupby(subset["Datetime"].dt.year)["USGS_flow"].idxmin().values]

            sel = sel[["Datetime", "USGS_flow"]].reset_index(drop=True)
            sel = sel.sort_values("USGS_flow", ascending=True)

            sorted_data = sel["USGS_flow"].values
            sorted_date = sel["Datetime"].values

            # --- Exceedance Probability and Return Period ---
            Pr = [(j / (len(sorted_data) + 1)) * 100 for j in range(1, len(sorted_data) + 1)]
            Tp = [1 / (p / 100) for p in Pr]

            flood_values[f"dict_{sid}"] = [
                {"Date": sorted_date},
                {"Yearly max": sorted_data},
                {"Exceedance probability": Pr},
                {"Return periods": Tp},
            ]
            m += 1

        print(f"✅ Processed {m} station(s) for {event_type} events.")
        return flood_values

    # ============================================================
    # === CONVERT TO DATAFRAME AND SAVE ===
    # ============================================================
    def df_flood_events(self, flood_values):
        print("🧮 Building event DataFrame...")
        if not flood_values:
            print("⚠️ No flood/drought data to convert — skipping.")
            return pd.DataFrame()

        df = pd.DataFrame(columns=["Station", "Date", "Yearly max", "Exceedance probability", "Return periods"])

        for station, data in flood_values.items():
            # Convert to DataFrame
            yearly_max = data[1]["Yearly max"]
            df_new = pd.DataFrame({"Yearly max": yearly_max[::-1]})
            numeric_site = "".join(filter(str.isdigit, station))
            numeric_site = numeric_site.zfill(8)
            df_new["Station"] = numeric_site
            df_new["Exceedance probability"] = data[2]["Exceedance probability"]
            df_new["Return periods"] = data[3]["Return periods"]
            df_new["Date"] = data[0]["Date"]
            df = pd.concat([df, df_new], ignore_index=True)

        output_file = f"{self.datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/df_{self.event_type}_events_{self.state}.csv"
        df.to_csv(output_file, index=False)
        print(f"💾 Saved {self.event_type} events to: {output_file}")
        return df

    # ============================================================
    # === LOAD SINGLE STATION DATA (OPTIONAL) ===
    # ============================================================
    def station_data(self, site_code):
        print("📈 Loading single-station data...")
        path = f"{self.datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/df_{self.event_type}_events_{self.state}.csv"
        if not os.path.exists(path):
            print(f"⚠️ File not found: {path}")
            return pd.Series(dtype=float)

        df = pd.read_csv(path)
        df["Station"] = df["Station"].astype(str).str.zfill(8)
        sc = str(site_code[0]).zfill(8)
        station_rows = df[df["Station"] == sc]
        if station_rows.empty:
            print(f"⚠️ No data found for site {sc}")
        return station_rows["Yearly max"]

