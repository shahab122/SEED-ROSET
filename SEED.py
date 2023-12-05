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

class SEED:
    def __init__(self, file_path, column_name, target_id, event_type):
        self.file_path = file_path
        self.column_name = column_name
        self.target_id = target_id
        self.event_type = event_type

    def load_data(self):
        data = pd.read_csv(self.file_path)
        return data[data['Station'] == self.target_id][self.column_name]
    
    def numeric_data(self, data):
        numeric_data = pd.to_numeric(data, errors='coerce')  # Convert to numeric, ignoring non-numeric values
        return numeric_data

#     def fit_lp(self, data, return_interval):
#         # Calculate skewness coefficient (P) for the data
#         log_data = np.log10(data)  # Apply log10 to each data value individually
#         skewness_coefficient = skew(log_data, nan_policy='omit')
#         mean_data = np.mean(log_data)
#         sd_data = np.std(log_data)
#         print(skewness_coefficient, mean_data, sd_data)

#         # Calculate probability of exceedance (D) for each data value
#         sorted_data = np.sort(data)[::-1]  # Sort data in descending order
#         prob_exceedance = np.arange(1, len(sorted_data) + 1) / (len(sorted_data) + 1) * 100
#         print(prob_exceedance)

#         # Initialize an empty list to store fitted data values
#         fitted_data_values = []

#         # Iterate through each data value and calculate fitted data
# #         for i in range(len(data)):
# #             P = prob_exceedance[i]
# #             z_value = norm.ppf(1 - (1/return_interval*100)/100, 0, 1)
# #             K = 2/skewness_coefficient * (((z_value - skewness_coefficient/6) * (skewness_coefficient/6) + 1)**3 - 1)
# #             print(K)
# #             fitted_data = mean_data + K * sd_data
# #             data_lp = 10**fitted_data
# #             fitted_data_values.append(data_lp)
#         return_interval = int(return_interval)
#         z_value = norm.ppf(1 - (1/return_interval*100)/100, 0, 1)
#         K = 2/skewness_coefficient * (((z_value - skewness_coefficient/6) * (skewness_coefficient/6) + 1)**3 - 1)
#         print(K)
#         fitted_data = mean_data + K * sd_data
#         data_lp = 10**fitted_data
#         fitted_data_values.append(data_lp)

#         return fitted_data_values

    def fit_lp(self, data, return_interval, event_type):
        # Calculate skewness coefficient (P) for the data
        log_data = np.log10(data)  # Apply log10 to each data value individually
        skewness_coefficient = skew(log_data, nan_policy='omit')
        mean_data = np.mean(log_data)
        sd_data = np.std(log_data)
        print(skewness_coefficient, mean_data, sd_data)

        # Calculate probability of exceedance (D) for each data value
        if event_type == 'flood':
            sorted_data = np.sort(data)[::-1]  # Sort data in descending order
        elif event_type == 'drought':
            sorted_data = np.sort(data)  # Sort data in ascending order for drought/low values
        else:
            raise ValueError("Invalid event_type. Use 'flood' or 'drought'.")

        prob_exceedance = np.arange(1, len(sorted_data) + 1) / (len(sorted_data) + 1) * 100
        print(prob_exceedance)

        # Initialize an empty list to store fitted data values
        fitted_data_values = []
        return_interval = int(return_interval)
        
        if event_type == 'flood':
            z_value = norm.ppf(1 - (1/return_interval*100)/100, 0, 1) #For non-exceedance probability
        if event_type == 'drought':
            z_value = norm.ppf((1/return_interval*100)/100, 0, 1) #For exceedance probability
            
        K = 2/skewness_coefficient * (((z_value - skewness_coefficient/6) * (skewness_coefficient/6) + 1)**3 - 1)
        print(K)
        fitted_data = mean_data + K * sd_data
        data_lp = 10**fitted_data
        fitted_data_values.append(data_lp)

        return fitted_data_values


