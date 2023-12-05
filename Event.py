#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Import the packages
import pandas as pd
import glob
import os
import numpy as np
import scipy.stats as scs
from scipy.stats import pearson3, skew, norm
import matplotlib.pyplot as plt 
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

class EVENT:
    def __init__(self, file_path, datapath, state, event_type):
        self.file_path = file_path
        self.datapath = datapath
        self.state = state
        self.event_type = event_type
#         self.station_id = station_id
        
    def load_files(self):
        print('Loading files...')
        all_files = glob.glob(os.path.join(self.file_path , "*.csv"))
        return all_files
    
    def load_data(self, all_files):
        print('Loading data from files...')
        temp_files = []
        for filename in tqdm(all_files):
            data_files  = pd.read_csv(filename, index_col=None, header=0)
            temp_files.append(data_files)
            
        all_flow = pd.concat(temp_files, axis=0, ignore_index=True)
        all_flow = all_flow.dropna() # removing the missing values
        all_flow = all_flow[(all_flow['USGS_flow']>0)]
        np.min(all_flow['USGS_flow'])
        
        #Change the datetime in the dataframe
        all_flow['Datetime'] = pd.to_datetime(all_flow['Datetime'])
        all_flow.dtypes
        all_flow['USGS_flow']
        return all_flow
    
    def site_id(self, file_path, all_files):
        print('Getting site ids...')
        #Find the station ID
        site_id = []

        # Loop through the file paths and extract the site code
        for file_path in all_files:
            # Split the file path into directory path and filename
            dir_path, file_name = os.path.split(file_path)

            # Split the filename into the site code and the file extension
            site_id1, ext = os.path.splitext(file_name)

            # Extract the site code from the site code string
            site_id.append(site_id1.split("_")[0])
        return site_id
    
    def site_code(self, site_id):
        print('Fixing applicable site codes...')
        #Site_code = site_id (station id) without the unnecessary zeros at the beginning 
        #(select the meaning numbers only, e.g., 968674521 instead of 00968674521)
        site_code = []
        for i in range(len(site_id)):
            site  = str(site_id[i])
            if site[0] == '0':
                site_code.append(site[-7:]) #Change it with the following line depending on the station ID length
            else:
                site_code.append(site[-8:]) #Change it with the above line depending on the station ID length

        site = []
        for i in range(len(site_code)): 
            site.append(int(site_code[i]))
        site_code = site
        range(len(site_code))
        return site_code
    
#     def flood_values(self, all_flow, site_code):
#         print('Calculating flood values...')
#         #Select annual maximum streamflow from the entire dataset (all_flow) for each site_code, calculate exceedance probability,and
#         # Calculate return period
#         flood_values = {}

#         m= 0
#         # Subset the DataFrame based on the values in the 'city' column
#         for i in range(len(site_code)):
#             subset = all_flow.loc[all_flow['USGS_ID'] == site_code[i]]
#             subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce') #Uncomment this line if the following line fails
#             #     max_data = subset.groupby(subset.Datetime.dt.year)['USGS_flow'].max() # Selected by year
#             max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmax().values] # Selected by date of occurance
#             max_data = max_data[["Datetime", "USGS_flow"]]
#             max_data = max_data.reset_index(drop=True)
    
#             sort_data  = max_data.sort_values('USGS_flow', ascending = True)
#             sorted_data = sort_data['USGS_flow']

#             sorted_date = sort_data['Datetime']

#             #Calculate exceedance probability
#             Pr = []
#             Tp = []  
#             for j in range(1,len(sorted_data)+1):
#                 Pr.append((j/(len(sorted_data)+1))*100)
   
#             for n in range(len(Pr)):
#                 Tp.append(1/(Pr[n]/100))
    
#             #Save the above results as a dictionary 
#             dict_list = [{'Date': sorted_date}, {'Yearly max': sorted_data}, {'Exceedance probability': Pr}, {'Return periods': Tp}]
#             k = site_code[m]
#             key = f'dict_{k}'
#             flood_values[key] = dict_list
#             m +=1
#         return flood_values

    def flood_values(self, all_flow, site_code, event_type):
        print(f'Calculating {event_type} values...')
        # Select either annual maximum or minimum streamflow from the entire dataset (all_flow) for each site_code,
        # calculate exceedance probability, and calculate return period
        flood_values = {}

        m = 0
        # Subset the DataFrame based on the values in the 'city' column
        for i in range(len(site_code)):
#             subset = all_flow.loc[all_flow['USGS_ID'] == site_code[i]
#             subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce')
            subset = all_flow.loc[all_flow['USGS_ID'] == site_code[i]]

            subset['USGS_flow'] = pd.to_numeric(subset['USGS_flow'], errors='coerce') #Uncomment this line if the following line fails

            if event_type == 'flood':
                max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmax().values]  # Selected by date of occurrence
            elif event_type == 'drought':
                max_data = subset.loc[subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].idxmin().values]  # Selected by date of occurrence
            else:
                raise ValueError("Invalid value_type. Use 'flood' or 'drought'.")

            max_data = max_data[["Datetime", "USGS_flow"]]
            max_data = max_data.reset_index(drop=True)
            
            if event_type == 'flood':
                sort_data = max_data.sort_values('USGS_flow', ascending=True)
            elif event_type == 'drought':
                sort_data = max_data.sort_values('USGS_flow', ascending=True)
                
            sorted_data = sort_data['USGS_flow']
            sorted_date = sort_data['Datetime']

            # Calculate exceedance probability
            Pr = []
            Tp = []
            for j in range(1, len(sorted_data) + 1):
                Pr.append((j / (len(sorted_data) + 1)) * 100)

            for n in range(len(Pr)):
                Tp.append(1 / (Pr[n] / 100))

            # Save the above results as a dictionary
            dict_list = [{'Date': sorted_date}, {'Yearly max': sorted_data}, {'Exceedance probability': Pr}, {'Return periods': Tp}]
            k = site_code[m]
            key = f'dict_{k}'
            flood_values[key] = dict_list
            m += 1

        return flood_values

    def df_flood_events(self, flood_values):
        print('Getting flood events...')
        #Prepare the dataframe from the above huge dictionary to save as a csv file for each state containing all stations (site_id)
        # create an empty dataframe
        df = pd.DataFrame(columns=['Station', 'Date', 'Yearly max', 'Exceedance probability', 'Return periods'])

        # iterate over the keys and values of the dictionary
        for station, data in flood_values.items():
            # get the yearly max data from the dictionary
            yearly_max = data[1]['Yearly max']
    
            # create a new dataframe with the yearly max data
            df_new = pd.DataFrame({'Yearly max': yearly_max[::-1]})
            #     df_new = pd.DataFrame({'Yearly max': yearly_max})
    
            # add the station name to the dataframe
            site  = str(station)
            numeric_site = ''.join(filter(str.isdigit, site))  # Filter out non-numeric characters
            if len(numeric_site) == 7:
                new_station = numeric_site #Change it with the following line depending on the station ID length
            else: 
                new_station = numeric_site[-8:] #Change it with the above line depending on the station ID length
            df_new['Station'] = new_station

            # get the other data from the dictionary
            exceedance_prob = data[2]['Exceedance probability']
            return_periods = data[3]['Return periods']
            date = data[0]['Date']
    
            # add the other data to the dataframe
            df_new['Exceedance probability'] = exceedance_prob
            df_new['Return periods'] = return_periods
            df_new['Date'] = date
    
            # append the new dataframe to the main dataframe
            df = df.append(df_new, ignore_index=True)   
        df_flood_events = df
        df_flood_events.to_csv(f"{self.datapath}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/df_flood_events_{self.state}.csv", index=False)
        return df_flood_events
    
    def station_data(self, site_code):
        print('Loading station data...')
        #Read the csv just constructed using above command 
        df = pd.read_csv(f"{self.datapath}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/df_flood_events.csv")
        #Select rows from the imported csv file corresponding to the station id
        station_rows = df[df['Station'] == site_code[1]]
        station_data = station_rows['Yearly max']
        return station_data
    
 
 

