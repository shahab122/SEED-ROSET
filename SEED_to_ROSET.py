import pandas as pd

def seed_output(datapath, analysis_level, merged_site_id, merged_site_code, target_usgs_ids):
   
    #1. Create the LP3 datafrane
    #For multiple USGS sites
    lp3_values = pd.read_csv(f"{datapath}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/lp3_values.csv")
    #     # Remove square brackets from the "Estimated streamflow" column
    lp3_values['Estimated streamflow'] = lp3_values['Estimated streamflow'].str.strip('[]')

    #     # Convert the "Estimated streamflow" column to numeric
    # lp3_values['Estimated streamflow'] = pd.to_numeric(lp3_values['Estimated streamflow'], errors='coerce')
    lp3_values

    #I have some concerns about the nan values - please address - RYAN
    #Need to have flexible state filepath. nans occur when hucs go accross state boundaries!!!!!!!!!!! - RYAN
    #2. Pull the dataframe of historical flood events and corresponding dates of occurence
    #For smultiple USGS sites
    file_path = f"{datapath}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/merged_flood_events.csv"
    data = pd.read_csv(file_path)
    station_rows = data
    #Select rows from the imported csv file corresponding to the station id

    # # station = int(input("Enter the USGS gauge ID (e.g., 7256897): "))
    # station_rows = data[data['Station'] == target_id]
    station_rows

    #3. Compare the LP3 estimated flood values with the historical events and find which historical values are the closest and the 
    #corresponding dates of occurence and create a dataframe 
    df1 = lp3_values
    df2 = station_rows

    # Convert the "Yearly max" column in df2 to the same data type as "Estimated streamflow" in df1
    df2['Yearly max'] = df2['Yearly max'].astype(float)

    # Convert the "Estimated streamflow" column in df1 to float
    df1['Estimated streamflow'] = df1['Estimated streamflow'].astype(float)

    # Convert the "Date" column to datetime
    df2['Date'] = pd.to_datetime(df2['Date'])

    # Initialize an empty DataFrame to store the result
    result_df = pd.DataFrame(columns=['Station', 'Estimated streamflow', 'Yearly max', 'Date'])

    # Iterate over unique "Station" values in df1
    for station in df1['Station'].unique():
        # Filter df2 for rows with the same "Station"
        station_df2 = df2[df2['Station'] == station]

        # Initialize variables to track the closest "Yearly max" and its associated "Date"
        closest_yearly_max = None
        closest_date = None
        min_difference = float('inf')

        # Iterate through rows in station_df2
        for index, row in station_df2.iterrows():
            # Calculate the absolute difference between "Estimated streamflow" and "Yearly max"
            difference = abs(df1[df1['Station'] == station]['Estimated streamflow'].values[0] - row['Yearly max'])

            # Check if the current difference is smaller than the minimum difference
            if difference < min_difference:
                min_difference = difference
                closest_yearly_max = row['Yearly max']
                closest_date = row['Date']

        # Append the closest values to the result DataFrame
        result_df = result_df.append({'Station': station, 'Estimated streamflow': df1[df1['Station'] == station]['Estimated streamflow'].values[0], 'Yearly max': closest_yearly_max, 'Date': closest_date}, ignore_index=True)

    # Print the resulting DataFrame
    display(result_df)
    
    #4. Format the dates of occurence found from the historical events
    from datetime import datetime
    # Initialize empty list to store the new formatted 
    formatted_dates = []

    # Iterate through the DataFrame rows using a for loop
    for index, row in result_df.iterrows():
        
        # Extract the "Date" column as a Timestamp object
        date_obj = row['Date']
        
        # Extract the year, month, and day from the "Date" column
#         year = row['Date'].year
#         month = row['Date'].month
#         day = row['Date'].day
        # Assuming 'Date' is the column containing the date
        if pd.notna(row['Date']):
            year = row['Date'].year
            month = row['Date'].month
            day = row['Date'].day
#         else:
#         # Handle NaN case, for example, assigning a default value or skipping the row
#             year = 2016  # Replace None with the default value or any other handling you prefer
#             month = 10
#             day = 15
        # Create a new date using the extracted components
            new_date = datetime(year, month, day)

        # Format the date as "day-month-year" and append to the list
    #     formatted_date = date_obj.strftime('%d-%m-%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            formatted_dates.append(formatted_date)
        else:
            formatted_dates.append('2015-10-15')

    # Print the formatted dates
    print("Formatted Dates:", formatted_dates)

    #5 
    Station = result_df['Station'].tolist()

    #Find the days around the date of occurence of the event for each usgs site to be included in the analysis 
    from datetime import datetime, timedelta

    # Define your Station and Dates lists
    # Station = [2339495, 2342500, 2361000]
    # formatted_dates = ['06-02-2010', '18-06-2018', '19-03-1996']

    # Number of days to expand backward and forward
    # analysis_level = input("Enter 'lulc' or 'huc' for analysis level: ")
    num_days = int(input("Enter number of days around the event to be included in the analysis: "))  # You can change this number as needed

    # Convert the date strings to datetime objects
    date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in formatted_dates]

    # Create a dictionary to store expanded dates for all stations
    expanded_dates = {}

    # Loop through each station and corresponding date
    for station, date in zip(Station, date_objects):
        # Initialize lists to store expanded dates
        startDT = []
        endDT = []

        # Generate backward and forward dates
        for i in range(-num_days, num_days + 1):
            new_date = date + timedelta(days=i)
            if i < 0:
                startDT.append(new_date.strftime('%Y-%m-%d'))
            elif i > 0:
                endDT.append(new_date.strftime('%Y-%m-%d'))

        # Store the expanded dates in the dictionary
        expanded_dates[station] = {
            'startDT': startDT,
            'endDT': endDT
        }

    # Access expanded dates for all stations
    for station, dates in expanded_dates.items():
        print(f"Station {station} formatted_dates ({num_days} days back):", dates['startDT'])
        print(f"Station {station} formatted_dates ({num_days} days forward):", dates['endDT'])

    #6
    if analysis_level == 'huc':
        site_id = merged_site_id
        site_code = merged_site_code
    elif analysis_level == 'lulc':
        site_id = site_id
        site_code = site_code

    #Location of each usgs site (selected by the user) in the site_id list (with all the usgs sites in a State)
    # List of usgs_id values you want to find 
    usgs_ids_to_find = target_usgs_ids  # Add all the IDs you want to find

    # Initialize a list to store the locations of usgs_id values
    locations_list = []

    # Iterate through the usgs_id values
    for usgs_id in usgs_ids_to_find:
        if usgs_id in site_id:
            location = site_id.index(usgs_id)
            locations_list.append(location)
        else:
            locations_list.append(None)  # None if usgs_id is not found in b

    # Print the locations
    for usgs_id, location in zip(usgs_ids_to_find, locations_list):
        if location is not None:
            print(f"Location of {usgs_id} in list target_usgs_ids is {location}")
        else:
            print(f"{usgs_id} not found in list target_usgs_ids")
    # Filter out None values from the locations_list
    locations_list_filtered = [location for location in locations_list if location is not None]

    # You can also access the locations using the locations_list
    print("Locations List:", locations_list_filtered)

    location = locations_list_filtered
    location

    #7. Find the start date and end date for each usgs site from the extended dates around the event
    # Initialize a list to store the results for each location
    results = []

    # Iterate through the locations in the location list
    for loc in location:
        # Specify the station ID you want to retrieve startDT and endDT for
        target_station = site_code[loc]  # Change this to the desired station ID

        # Check if the target station exists in the dictionary
        if target_station in expanded_dates:
            station_dates = expanded_dates[target_station]
            startDT = station_dates['startDT'][0] if station_dates['startDT'] else None
            endDT = station_dates['endDT'][-1] if station_dates['endDT'] else None

            results.append((target_station, startDT, endDT))
        else:
            results.append((target_station, None, None))

    # Print the results
    for target_station, startDT, endDT in results:
        if startDT:
            print(f"Station {target_station} Start Date ({num_days} days back): '{startDT}'")
        else:
            print(f"No start date available for Station {target_station}")

        if endDT:
            print(f"Station {target_station} End Date ({num_days} days forward): '{endDT}'")
        else:
            print(f"No end date available for Station {target_station}")
    results

    #8. Assuming 'results' and 'b' have been defined as you mentioned

    # Create a new list to store the modified results
    modified_results = []

    # Iterate through both 'results' and 'b' and replace the first column of 'results' with the first column of 'b'
    for (station, start_date, end_date), usgs_id in zip(results, target_usgs_ids):
        # Append the modified row to 'modified_results'
        modified_results.append((usgs_id, start_date, end_date))

    # 'modified_results' now contains the desired modification
    print(modified_results)

    for row in modified_results:
        # 'row' contains a tuple (station, start_date, end_date)
        station, start_date, end_date = row

        # Access individual elements within the row
        print(f"Station: {station}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}\n")
    return modified_results