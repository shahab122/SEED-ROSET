#!/usr/bin/env python
# coding: utf-8

# Import necessary packages
import pandas as pd
import glob
import os
import numpy as np
import scipy.stats as scs
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

class EVENT:
    def __init__(self, NWIS_path, datapath, state, event_type, model_version):
        """
        Initialize the EVENT class for processing hydrological events.

        Parameters:
            NWIS_path (str): Path to NWIS data files.
            datapath (str): Path to general data directory.
            state (str): State code or "ALL" for NWM3.0.
            event_type (str): 'flood' or 'drought'.
            model_version (str): Either 'NWM2.1' or 'NWM3.0'.
        """
        self.NWIS_path = NWIS_path
        self.datapath = datapath
        self.state = state
        self.event_type = event_type.lower()
        self.model_version = model_version

    def load_files(self):
        """Load CSV files from NWIS directory."""
        files = glob.glob(os.path.join(self.NWIS_path, "*.csv"))
        if not files:
            print(f"⚠️ No CSV files found in {self.NWIS_path}. Check directory path.")
        return files

    def load_data(self, all_files):
        """Load and concatenate data from all NWIS files."""
        temp_files = []

        for filename in all_files:
            try:
                df = pd.read_csv(filename, index_col=None, header=0, low_memory=False)
                temp_files.append(df)
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")

        if not temp_files:
            print("⚠️ No valid data files loaded.")
            return pd.DataFrame()

        all_flow = pd.concat(temp_files, axis=0, ignore_index=True)
        all_flow.dropna(inplace=True)  # Remove missing values
        all_flow = all_flow[all_flow['USGS_flow'] > 0]  # Keep only positive values

        # Convert Datetime column to correct format
        if 'Datetime' in all_flow.columns:
            all_flow['Datetime'] = pd.to_datetime(all_flow['Datetime']).dt.strftime('%Y-%m-%d')

        return all_flow

    def site_code(self, all_files):
        """Extract site codes from file names for NWM3.0."""
        site_codes = []
        for file in all_files:
            base_name = os.path.basename(file).split("_")[0]  # Extract USGS_ID
            site_codes.append(base_name)

        return list(set(site_codes))  # Remove duplicates

    def flood_values(self, all_flow, site_codes):
        """
        Compute flood or drought values for each site.

        Parameters:
            all_flow (DataFrame): The combined NWIS data.
            site_codes (list): List of site codes.

        Returns:
            dict: Processed flood or drought values per site.
        """
        print(f'🔹 Calculating {self.event_type} values...')

        flood_values = {}

        for site in site_codes:
            # Filter data for the specific site
            subset = all_flow[all_flow['USGS_ID'].astype(str) == str(site)]

            if subset.empty:
                print(f"⚠️ No data found for site {site}, skipping...")
                continue

            subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce')

            if self.event_type == 'flood':
                max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmax().values]
            elif self.event_type == 'drought':
                max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmin().values]
            else:
                raise ValueError("Invalid event_type. Use 'flood' or 'drought'.")

            max_data = max_data[["Datetime", "USGS_flow"]].reset_index(drop=True)

            sort_data = max_data.sort_values('USGS_flow', ascending=True)
            sorted_data = sort_data['USGS_flow']
            sorted_date = sort_data['Datetime']

            # Calculate exceedance probability
            Pr = [(j / (len(sorted_data) + 1)) * 100 for j in range(1, len(sorted_data) + 1)]
            Tp = [1 / (pr / 100) for pr in Pr]

            # Save results
            flood_values[site] = {
                'Date': sorted_date.tolist(),
                'Yearly max': sorted_data.tolist(),
                'Exceedance probability': Pr,
                'Return periods': Tp
            }

        return flood_values

    def df_flood_events(self, flood_values):
        """
        Convert flood_values dictionary to a DataFrame.

        Parameters:
            flood_values (dict): Processed flood values.

        Returns:
            DataFrame: The structured flood event data.
        """
        all_data = []

        for site, values in flood_values.items():
            for i in range(len(values['Date'])):
                row = {
                    'Station': site,
                    'Date': values['Date'][i],
                    'Yearly max': values['Yearly max'][i],
                    'Exceedance probability': values['Exceedance probability'][i],
                    'Return periods': values['Return periods'][i]
                }
                all_data.append(row)

        df_flood_events = pd.DataFrame(all_data)
        return df_flood_events



# ########################### EVENT_NWM3.py ####################
# import pandas as pd
# import glob
# import os
# import numpy as np
# from tqdm import tqdm

# class EVENT:
#     def __init__(self, NWIS_path, datapath, state, event_type, model_version):
#         self.NWIS_path = NWIS_path
#         self.datapath = datapath
#         self.state = state
#         self.event_type = event_type
#         self.model_version = model_version  # Track which model version is used

#     def load_files(self):
#         """
#         Load CSV files from the specified NWIS_path.
#         - For NWM2.1: Reads from state-specific subfolders.
#         - For NWM3.0: Reads all CSV files from the NWIS directory.
#         """
#         print(f'Loading files from: {self.NWIS_path}')
#         all_files = glob.glob(os.path.join(self.NWIS_path, "*.csv"))

#         if not all_files:
#             print(f"⚠️ No CSV files found in: {self.NWIS_path}")

#         return all_files

#     def load_data(self, all_files):
#         print('Loading data from files...')

#         if not all_files:
#             raise ValueError(f"🚨 No CSV files found in {self.NWIS_path}. Check the path and file availability.")

#         temp_files = []
#         for filename in tqdm(all_files):
#             data_files = pd.read_csv(filename, index_col=None, header=0)
#             temp_files.append(data_files)

#         all_flow = pd.concat(temp_files, axis=0, ignore_index=True)
#         all_flow = all_flow.dropna()  # Removing missing values
#         all_flow = all_flow[all_flow['USGS_flow'] > 0]

#         # Convert Datetime column
#         all_flow['Datetime'] = pd.to_datetime(all_flow['Datetime'])

#         return all_flow

#     def site_code(self, all_files):
#         print('Extracting site codes...')

#         site_codes = []
#         for file_path in all_files:
#             _, file_name = os.path.split(file_path)
#             site_code = file_name.split("_")[0]  # Extract the first part of filename
#             site_codes.append(int(site_code))  # Convert to integer

#         return site_codes

#     def flood_values(self, all_flow, site_codes):
#         print(f'Calculating {self.event_type} values...')

#         flood_values = {}

#         for site in site_codes:
#             # If using NWM2.1, filter by `USGS_ID`
#             if self.model_version == "NWM2.1" and "USGS_ID" in all_flow.columns:
#                 subset = all_flow.loc[all_flow['USGS_ID'] == site]
#             else:
#                 subset = all_flow  # NWM3.0: Use all data since there’s no USGS_ID column

#             subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce')

#             if self.event_type == 'flood':
#                 max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmax().values]
#             elif self.event_type == 'drought':
#                 max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmin().values]
#             else:
#                 raise ValueError("Invalid event_type. Use 'flood' or 'drought'.")

#             max_data = max_data[["Datetime", "USGS_flow"]].reset_index(drop=True)

#             sort_data = max_data.sort_values('USGS_flow', ascending=True)
#             sorted_data = sort_data['USGS_flow']
#             sorted_date = sort_data['Datetime']

#             # Calculate exceedance probability
#             Pr = [(j / (len(sorted_data) + 1)) * 100 for j in range(1, len(sorted_data) + 1)]
#             Tp = [1 / (pr / 100) for pr in Pr]

#             # Save results as a dictionary
#             flood_values[f'dict_{site}'] = [
#                 {'Date': sorted_date}, 
#                 {'Yearly max': sorted_data}, 
#                 {'Exceedance probability': Pr}, 
#                 {'Return periods': Tp}
#             ]

#         return flood_values

#     def df_flood_events(self, flood_values):
#         print('Compiling flood event data...')

#         df = pd.DataFrame(columns=['Station', 'Date', 'Yearly max', 'Exceedance probability', 'Return periods'])

#         for station, data in flood_values.items():
#             yearly_max = data[1]['Yearly max']
#             df_new = pd.DataFrame({'Yearly max': yearly_max[::-1]})

#             # Extract numeric site code
#             site = ''.join(filter(str.isdigit, station))
#             new_station = site if len(site) == 7 else site[-8:]

#             df_new['Station'] = new_station
#             df_new['Exceedance probability'] = data[2]['Exceedance probability']
#             df_new['Return periods'] = data[3]['Return periods']
#             df_new['Date'] = data[0]['Date']

#             df = df.append(df_new, ignore_index=True)

#         df.to_csv(f"{self.datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/df_flood_events_{self.state}.csv", index=False)
#         return df