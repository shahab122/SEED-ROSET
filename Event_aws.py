import pandas as pd

class EVENT:
    def __init__(self, datapath, state, event_type):
        self.datapath = datapath
        self.state = state
        self.event_type = event_type
        
    def site_id(self, data):
        print('Getting site ids...')
        site_id = data['USGS_ID'].unique().tolist()
        return site_id
    
    def site_code(self, site_id):
        print('Fixing applicable site codes...')
        site_code = [str(site)[-8:] for site in site_id]
        return site_code
    
    def flood_values(self, data, site_code, event_type):
        print(f'Calculating {event_type} values...')
        flood_values = {}
        
        for code in site_code:
            subset = data[data['USGS_ID'] == int(code)]
            if event_type == 'flood':
                max_data = subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].max().reset_index()
            elif event_type == 'drought':
                max_data = subset.groupby(subset['Datetime'].dt.year)['USGS_flow'].min().reset_index()
            else:
                raise ValueError("Invalid event type. Use 'flood' or 'drought'.")
            
            max_data.rename(columns={'Datetime': 'Date', 'USGS_flow': 'Yearly max'}, inplace=True)
            max_data['Exceedance probability'] = (max_data.index + 1) / (len(max_data) + 1) * 100
            max_data['Return periods'] = 1 / (max_data['Exceedance probability'] / 100)
            
            flood_values[code] = max_data.to_dict(orient='list')
        
        return flood_values
    
    def df_flood_events(self, flood_values):
        print('Getting flood events...')
        dfs = []
        
        for code, data in flood_values.items():
            df = pd.DataFrame(data)
            df['Station'] = code
            dfs.append(df)
        
        result_df = pd.concat(dfs, ignore_index=True)
        result_df.to_csv(f"{self.datapath}/LULC_Streamflow_SA/Community-Streamflow-Evaluation-System/SEED-ROSET/SEED_data/df_{self.event_type}_events_{self.state}.csv", index=False)
        
        return result_df
