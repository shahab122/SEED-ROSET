#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# analysis_tool.py

# Define a function to remove leading zeros and single quotes from a list of target IDs
def remove_leading_zeros(target_ids):
    return [target_id.lstrip('0').strip("'") for target_id in target_ids]

# Define a function to perform the analysis based on the selected level
def perform_analysis(analysis_level, target_ids):
    if analysis_level == 'lulc':
        # Perform analysis for 'lulc' level
        updated_target_ids = remove_leading_zeros(target_ids)
        return updated_target_ids
    elif analysis_level == 'huc':
        # Perform analysis for 'huc' level
        updated_target_ids = remove_leading_zeros(target_ids)
        return updated_target_ids
    else:
        return None  # Invalid analysis level

