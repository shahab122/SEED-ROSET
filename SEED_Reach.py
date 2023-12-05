#!/usr/bin/env python
# coding: utf-8
#author: Ryan Johnson, PHD, Alabama Water Institute
#Date: 6-6-2022


'''
Run using the OWP_env: 
https://www.geeksforgeeks.org/using-jupyter-notebook-in-virtual-environment/
https://github.com/NOAA-OWP/hydrotools/tree/main/python/nwis_client

https://noaa-owp.github.io/hydrotools/hydrotools.nwm_client.utils.html#national-water-model-file-utilities
will be benefitical for finding NWM reachs between USGS sites
'''

# Import the NWIS IV Client to load USGS site data
from hydrotools.nwis_client.iv import IVDataService
from hydrotools.nwm_client import utils
import pandas as pd
import numpy as np
import data
import matplotlib.pyplot as plt
import mpl_toolkits
from mpl_toolkits.mplot3d import Axes3D
import sklearn
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import max_error
from sklearn.metrics import mean_absolute_percentage_error
import hydroeval as he
import dataretrieval.nwis as nwis
##https://streamstats-python.readthedocs.io/en/latest/gallery_vignettes/plot_get_characteristics.html
import streamstats
import geopandas as gpd
from IPython.display import display
import warnings
from progressbar import ProgressBar
from datetime import timedelta
import folium
import matplotlib
import mapclassify
import time
import jenkspy
import hvplot.pandas
import holoviews as hv
from holoviews import dim, opts, streams
from bokeh.models import HoverTool
import branca.colormap as cm
import vincent
from vincent import AxisProperties, PropertySet, ValueRef, Axis
import json
from folium import features
import proplot as pplt
pplt.rc["figure.facecolor"] = "w"
import pygeohydro as gh
import pygeoutils as geoutils
from pygeohydro import NID, NWIS
import pandas as pd
from folium.plugins import StripePattern
import io
import swifter
from geopy.geocoders import Nominatim
from multiprocessing import Process
import boto3
from botocore import UNSIGNED
from botocore.client import Config

geolocator = Nominatim(user_agent="geoapiExercises")
pd.options.plotting.backend = 'holoviews'
warnings.filterwarnings("ignore")


class Reach_Eval():
    def __init__(self, model , modified_results, cwd):
        self = self
        #self.df =df
        self.modified_results = modified_results
        self.cwd = cwd
        self.cms_to_cfs = 35.314666212661
        self.model = model
        
        self.cfsday_AFday = 1.983
        self.freqkeys = {
                        'D': 'Daily',
                        'M': 'Monthly',
                        'Q': 'Quarterly',
                        'A': 'Annual'
                        }
        
        #get NWIS sites
        self.NWIS_list = []
        for site in np.arange(0,len(self.modified_results),1):
            self.NWIS_list.append(self.modified_results[site][0])
        
       #AWS bucket information
        bucket_name = 'streamflow-app-data'
        s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
        self.bucket = s3.Bucket(bucket_name)

   
    '''
    Get WBD HUC data
    '''
    def get_NHD_Model_info(self):
        try:
            print('Getting geospatial information for NHD reaches')
            csv_key = 'Streamstats/Streamstats.csv'
            obj = self.bucket.Object(csv_key)
            body = obj.get()['Body']
            self.Streamstats = pd.read_csv(body)
            self.Streamstats.pop('Unnamed: 0')
            self.Streamstats.drop_duplicates(subset = 'NWIS_site_id', inplace = True)
            self.Streamstats.reset_index(inplace = True, drop = True)

            #Convert to geodataframe
            self.StreamStats = gpd.GeoDataFrame(self.Streamstats, geometry=gpd.points_from_xy(self.Streamstats.dec_long_va, self.Streamstats.dec_lat_va))
            
            #the csv loses the 0 in front of USGS ids, fix
            NWIS = list(self.Streamstats['NWIS_site_id'].astype(str))
            self.Streamstats['NWIS_site_id'] = ["0"+str(i) if len(i) <8 else i for i in NWIS]            

            #Get streamstats information for each USGS location
            self.sites = pd.DataFrame()
            for site in self.NWIS_list:
                s = self.Streamstats[self.Streamstats['NWIS_site_id'] ==  site]
                
                NHD_NWIS_df = utils.crosswalk(usgs_site_codes=site)
                
                if NHD_NWIS_df.shape[0] == 0:
                    NHD_segment = np.NaN
                    print('No NHD reach for USGS site: ', site)
 
                else:
                    NHD_segment = NHD_NWIS_df.nwm_feature_id.values[0]
                    
                s['NHD_reachid'] = NHD_segment
                
                self.sites = self.sites.append(s)
            
            print('Dropping USGS sites with no NHD reach')
            self.sites = self.sites.dropna(subset = 'NHD_reachid')
            self.sites.NHD_reachid = self.sites.NHD_reachid.astype(int)

        except KeyError:
            print('No monitoring stations in this NWIS location')
            
    def date_range_list(self):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = {}
        for site in np.arange(0,len(self.modified_results),1):
            key = self.modified_results[site][0]
            #get date range
            date_list[key] = [self.modified_results[site][1],self.modified_results[site][2]]

        self.dates = date_list
        
        
    def prepare_comparison(self):

        #prepare the daterange
        self.date_range_list()

        self.comparison_reaches = list(self.sites.NHD_reachid)
        self.NWIS_sites = list(self.sites.NWIS_site_id)


        self.NWIS_data = pd.DataFrame(columns = self.NWIS_sites)
        self.Mod_data = pd.DataFrame(columns = self.comparison_reaches)

        self.sites.state_id = self.sites.state_id.str.lower()
        #create a key/dict of site/state id
        NWIS_state_key =  dict(zip(self.sites.NWIS_site_id, 
                                  self.sites.state_id))                           


        Mod_state_key =  dict(zip(self.sites.NHD_reachid, 
                              self.sites.state_id))
        
        self.NHD_NWIS_key = dict(zip(self.sites.NHD_reachid, 
                              self.sites.NWIS_site_id))
        
        self.NWIS_NHD_key = dict(zip(self.sites.NWIS_site_id,
                               self.sites.NHD_reachid))

        #for NWM, add similar workflow to get non-NWM data
        print('Getting ', self.model, ' data')
        pbar = ProgressBar()
        self.Mod_data = {}
       
        for site in pbar(self.comparison_reaches):
            startDT = self.dates[self.NHD_NWIS_key[site]][0]
            endDT = self.dates[self.NHD_NWIS_key[site]][-1]
            #print(site, startDT, endDT)

            try:
                #print('Getting data for NWM: ', site)
                state = Mod_state_key[site]
                format = '%Y-%m-%d %H:%M:%S'
                csv_key = f"{self.model}/NHD_segments_{state}.h5/NWM_{site}.csv"
                obj = self.bucket.Object(csv_key)
                body = obj.get()['Body']
                Mod_flow = pd.read_csv(body)
                Mod_flow.pop('Unnamed: 0')
                Mod_flow['time'] ='12:00:00' 
                Mod_flow['Datetime'] = pd.to_datetime(Mod_flow['Datetime']+ ' ' + Mod_flow['time'], format = format)
                Mod_flow.set_index('Datetime', inplace = True)
                Mod_flow = Mod_flow.loc[startDT:endDT]
                #display(Mod_flow)
                cols = Mod_flow.columns
                self.Mod_data[site] = pd.DataFrame(Mod_flow[cols[0]])
                self.Mod_data[site].rename(columns = {cols[0]:'Mod_flow'}, inplace = True)

            except:
                print('Site: ', site, ' not in database, skipping')
                #remove item from list
                self.comparison_reaches.remove(site)




        #Get NWIS data
        self.NWIS_data = {}
        print('Getting NWIS data')
        pbar = ProgressBar()
        for site in pbar(self.NWIS_sites):
            startDT = self.dates[site][0]
            endDT = self.dates[site][-1]
           
            
            try:
                state = NWIS_state_key[site]
                csv_key = f"NWIS/NWIS_sites_{state}.h5/NWIS_{site}.csv"
                obj = self.bucket.Object(csv_key)
                body = obj.get()['Body']
                NWIS_meanflow = pd.read_csv(body)
                format = '%Y-%m-%d %H:%M:%S'
                NWIS_meanflow.drop_duplicates(subset = 'Datetime', inplace = True)                
                NWIS_meanflow['time'] ='12:00:00' 
                NWIS_meanflow['Datetime'] = pd.to_datetime(NWIS_meanflow['Datetime']+ ' ' + NWIS_meanflow['time'], format = format)
                NWIS_meanflow.set_index('Datetime', inplace = True)
                NWIS_meanflow = NWIS_meanflow.loc[startDT:endDT]
                #change np.nan to -100, can separate values out later
                #NWIS_meanflow.fillna(-100, inplace = True)
                self.NWIS_data[site] = -100


                #Adjust for different time intervals here
                #Daily
                #if self.freq =='D':
                self.NWIS_data[site] = pd.DataFrame(NWIS_meanflow['USGS_flow'])

            except:
                    print('USGS site ', site, ' not in database, skipping')
                    #remove item from list
                    self.NWIS_sites.remove(site)
        
        #reset comparison reaches
        for i in self.NWIS_data:
            self.NWIS_data[i].fillna(-100, inplace = True)
            
        for i in self.Mod_data:
            self.Mod_data[i].dropna(axis = 1, inplace = True)
            
        self.comparison_reaches = self.Mod_data.keys
        self.sites.reset_index(drop = True, inplace = True)
        self.NWIS_sites = self.sites['NWIS_site_id']

        #need to get the date range of NWIS and adjust modeled flow
        for site in self.NWIS_sites:
            nhd_reach = self.NWIS_NHD_key[site]
            NWIS_dates = self.NWIS_data[site].index
            
            self.Mod_data[nhd_reach] = self.Mod_data[nhd_reach].loc[NWIS_dates[0]:NWIS_dates[-1]]

        self.NWIS_column = self.NWIS_data.copy()
        #self.NWIS_column = pd.DataFrame(self.NWIS_column.stack(), columns = ['NWIS_flow_cfs'])
        #self.NWIS_column = self.NWIS_column.reset_index().drop('level_1',1)

        self.Mod_column = self.Mod_data.copy()
        #col = self.model+'_flow_cfs'
        #self.Mod_column = pd.DataFrame(self.Mod_column.stack(), columns = [col])
        #self.Mod_column = self.Mod_column.reset_index().drop('level_1',1)
        
        
        
    def Map_Plot_Eval(self, freq, supply):
        self.freq = freq

        if self.freq == 'D':
            self.units = 'cfs'
        else:
            self.units = 'Acre-Feet'

        yaxis = 'Streamflow (' + self.units +')'

        #Adjust for different time intervals here
        #Daily
       # if self.freq == 'D':
        self.NWIS_data_resampled = self.NWIS_data.copy()
        self.Mod_data_resampled = self.Mod_data.copy()


        #Monthly, Quarterly, Annual
        if self.freq !='D':
            #NWIS
            for key in self.NWIS_data:
                self.NWIS_data_resampled[key] = self.NWIS_data_resampled[key]*self.cfsday_AFday
                self.NWIS_data_resampled[key] = self.NWIS_data_resampled[key].resample(self.freq).sum()
                #Modeled
                nhd_reach = self.NWIS_NHD_key[site]
                self.Mod_data_resampled[nhd_reach] = self.Mod_data_resampled[nhd_reach]*self.cfsday_AFday
                self.Mod_data_resampled[nhd_reach] = self.Mod_data_resampled[nhd_reach].resample(self.freq).sum()
            
        if supply == True:
            #NWIS
            #Get key names
            keys = self.NWIS_data_resampled.keys()

            #set up cumulative monthly values
            for key in keys:
                #self.NWIS_data_resampled[key]['Year'] = self.NWIS_data_resampled[key].index.year
                self.NWIS_CumSum = pd.DataFrame()
                self.NWIS_CumSum = self.NWIS_data_resampled[key].cumsum()
                self.NWIS_data_resampled[key] = self.NWIS_CumSum

                #Model
                #Get Columns names
            keys = self.Mod_data_resampled.keys()

            #set up cumulative monthly values
            for key in keys:
                #self.Mod_data_resampled['Year'] = self.Mod_data_resampled[key].index.year
                self.Mod_CumSum = pd.DataFrame()
                self.Mod_CumSum[key] = self.Mod_data_resampled[key].cumsum()
                self.Mod_data_resampled[key] =self.Mod_CumSum
            
        print('Plotting monitoring station locations')
        cols =  ['NWIS_site_id', 'NWIS_sitename', 'NHD_reachid', 'dec_lat_va', 'dec_long_va', 'geometry']

        self.df_map = self.sites[cols]
        self.df_map.reset_index(inplace = True, drop = True) 
        #Get Centroid of watershed
        self.df_map = gpd.GeoDataFrame(self.df_map, geometry=gpd.points_from_xy(self.df_map.dec_long_va, self.df_map.dec_lat_va))

        centeroid = self.df_map.dissolve().centroid

        # Create a Map instance
#         m = folium.Map(location=[centeroid.y[0], centeroid.x[0]], tiles = 'Stamen Terrain', zoom_start=8, 
#                        control_scale=True)
        m = folium.Map(location=[centeroid.y[0], centeroid.x[0]], zoom_start=8, control_scale=True) #Shahab changed zoom_start to 3 from 8
        #add legend to map
#         colormap = cm.StepColormap(colors = ['r', 'orange',  'y', 'g'], vmin = -1, vmax = 1, index = [-1,-0.4,0,0.3,1])
        colormap = cm.StepColormap(colors = ['r', 'orange',  'purple', 'b', 'g'], vmin = -1, vmax = 1, index = [-1,-0.41, 0.0, 0.50,0.75,1]) #Shahab added
        colormap.caption = 'Model Performance (KGE)'
        m.add_child(colormap)

        ax = AxisProperties(
        labels=PropertySet(
            angle=ValueRef(value=300),
            align=ValueRef(value='right')
                )
            )

        for i in np.arange(0, len(self.df_map),1):
            #get site information
            site = self.df_map['NWIS_site_id'][i]
            USGSsite = 'USGS station id: ' + site
            site_name = self.df_map['NWIS_sitename'][i]

            reach = self.df_map['NHD_reachid'][i]
            Modreach = self.model +' reach id: ' + str(reach)
            
 
            
            #get modeled and observed information for each site
            df = pd.DataFrame(self.NWIS_data_resampled[site])
            df = df.rename(columns = {'USGS_flow': USGSsite})
            df[Modreach] = pd.DataFrame(self.Mod_data_resampled[reach])
            
            #remove na values or 0, this evaluates the model only on NWIS observations
            df_narem = pd.DataFrame()
            df_narem[USGSsite] = self.NWIS_data_resampled[site].astype('float64')
            df_narem[Modreach] = self.Mod_data_resampled[reach].astype('float64')
            #df_narem['error'] = df_narem['obs'] - df_narem['mod']
            #df_narem['P_error'] = abs(df_narem['error']/df_narem['obs'])*100
            #drop inf values
            df_narem.replace([np.inf, -np.inf], -100, inplace = True)
            df_narem = df_narem[df_narem >=0]
            df_narem.dropna(inplace = True)
            
            #if len(df_narem)>=1:

            obs = df_narem[USGSsite]
            mod = df_narem[Modreach]

            title_size = 14

            #create graph and convert to json
            graph = vincent.Line(df_narem, height=300, width=500) 
            graph.axis_titles(x='Datetime', y=yaxis)
            graph.legend(title= site_name)
            graph.colors(brew='Set1')
            graph.x_axis_properties(title_size=title_size, title_offset=35,
                          label_angle=300, label_align='right', color=None)
            graph.y_axis_properties(title_size=title_size, title_offset=-30,
                          label_angle=None, label_align='right', color=None)

            data = json.loads(graph.to_json())

            #Add marker with point to map, https://fontawesome.com/v4/cheatsheet/
            lat = self.df_map['dec_lat_va'][i]
            long = self.df_map['dec_long_va'][i]

            #calculate scoring
            kge, r, alpha, beta = he.evaluator(he.kge, mod.astype('float32'), obs.astype('float32'))
            #display(obs)
            #display(mod)
            #set the color of marker by model performance

#             if kge[0] > 0.30:
#                 color = 'green'

#             elif kge[0] > 0.0:
#                 color = 'yellow'

#             elif kge[0] > -0.40:
#                 color = 'orange'

#             else:
#                 color = 'red'

            #Shahab added 10 lines below
            if kge[0] > 0.75:
                color = 'green'

            elif kge[0] > 0.50:
                color = 'blue'

            elif kge[0] > 0.0:
                color = 'purple' #Shahab changed from 'yellow' to 'cyan'
            
            elif kge[0] > -0.41:
                color = 'orange'

            else:
                color = 'red'

            #print(site,kge[0], color)

            mk = features.Marker([lat, long], icon=folium.Icon(color=color, icon = 'fa-navicon', prefix = 'fa'))
            p = folium.Popup("Hello")
            v = features.Vega(data, width="100%", height="100%")

            mk.add_child(p)
            p.add_child(v)
            m.add_child(mk)


        display(m)
        m.save(f"{self.cwd}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/Eval_map.html") #Shahab added this
#         m.save("AL_0314.html")
        
        
    def Interactive_Model_Eval(self, freq, supply):
        self.freq = freq

        if self.freq == 'D':
            self.units = 'cfs'
        else:
            self.units = 'Acre-Feet'

        yaxis = 'Streamflow (' + self.units +')'

        #Adjust for different time intervals here
        #Daily
       # if self.freq == 'D':
        self.NWIS_data_resampled = self.NWIS_data.copy()
        self.Mod_data_resampled = self.Mod_data.copy()


        #Monthly, Quarterly, Annual
        if self.freq !='D':
            #NWIS
            for key in self.NWIS_data:
                self.NWIS_data_resampled[key] = self.NWIS_data_resampled[key]*self.cfsday_AFday
                self.NWIS_data_resampled[key] = self.NWIS_data_resampled[key].resample(self.freq).sum()
                #Modeled
                nhd_reach = self.NWIS_NHD_key[site]
                self.Mod_data_resampled[nhd_reach] = self.Mod_data_resampled[nhd_reach]*self.cfsday_AFday
                self.Mod_data_resampled[nhd_reach] = self.Mod_data_resampled[nhd_reach].resample(self.freq).sum()
            
        if supply == True:
            #NWIS
            #Get key names
            keys = self.NWIS_data_resampled.keys()

            #set up cumulative monthly values
            for key in keys:
                #self.NWIS_data_resampled[key]['Year'] = self.NWIS_data_resampled[key].index.year
                self.NWIS_CumSum = pd.DataFrame()
                self.NWIS_CumSum = self.NWIS_data_resampled[key].cumsum()
                self.NWIS_data_resampled[key] = self.NWIS_CumSum

                #Model
                #Get Columns names
            keys = self.Mod_data_resampled.keys()

            #set up cumulative monthly values
            for key in keys:
                #self.Mod_data_resampled['Year'] = self.Mod_data_resampled[key].index.year
                self.Mod_CumSum = pd.DataFrame()
                self.Mod_CumSum[key] = self.Mod_data_resampled[key].cumsum()
                self.Mod_data_resampled[key] =self.Mod_CumSum
            
            
        RMSE = []
        MAXERROR = []
        MAPE = []
        KGE = []

        for row in np.arange(0,len(self.sites),1):
            #Get NWIS id
            NWISid = self.sites['NWIS_site_id'][row]
            #Get Model reach id
            reachid = 'NHD_reachid'
            modid = self.sites[reachid][row]
               
            #get observed and prediction data
            obs = self.NWIS_data_resampled[NWISid]
            mod = self.Mod_data_resampled[modid]
            
            #remove na values 
            df = pd.DataFrame()
            df['obs'] = obs
            df['mod'] = mod.astype('float64')
            df = df[df>=0]
            df.dropna(inplace =True)
                      
            

            if len(df)>=1:
                df[df<0.01] = 0.01
                df['error'] = df['obs'] - df['mod']
                df['P_error'] = abs(df['error']/df['obs'])*100
                #drop inf values
                df.replace([np.inf, -np.inf], np.nan, inplace = True)
                df.dropna(inplace = True)
                

                obs = df['obs']
                mod = df['mod']



                #calculate scoring
                rmse = round(mean_squared_error(obs, mod, squared=False))
                maxerror = round(max_error(obs, mod))
                mape = df.P_error.mean()
                kge, r, alpha, beta = he.evaluator(he.kge, mod.astype('float32'), obs.astype('float32'))

                RMSE.append(rmse)
                MAXERROR.append(maxerror)
                MAPE.append(mape)
                KGE.append(kge[0])
                
            else:
                #calculate scoring
                rmse = 0
                maxerror = 0
                mape = 0
                kge = -10000
                
                RMSE.append(rmse)
                MAXERROR.append(maxerror)
                MAPE.append(mape)
                KGE.append(kge)

        #Connect model evaluation to a DF, add in relevant information concerning LULC
        Eval = pd.DataFrame()
        Eval['NWIS_site_id'] = self.sites['NWIS_site_id']
        Eval[reachid] = self.sites[reachid]
        Eval['Location'] = self.sites['NWIS_sitename']
        Eval['RMSE'] = RMSE
        Eval['MaxError'] = MAXERROR
        Eval['MAPE'] = MAPE
        Eval['KGE'] = KGE
        Eval['Drainage_area_mi2'] = self.sites['Drainage_area_mi2']
        Eval['Mean_Basin_Elev_ft'] = self.sites['Mean_Basin_Elev_ft']
        Eval['Perc_Forest'] = self.sites['Perc_Forest']
        Eval['Perc_Imperv'] = self.sites['Perc_Imperv']
        Eval['Perc_Herbace'] = self.sites['Perc_Herbace']
        Eval['Mean_Ann_Precip_in'] = self.sites['Mean_Ann_Precip_in']
        Eval['Ann_low_cfs'] = self.sites['Ann_low_cfs']
        Eval['Ann_mean_cfs'] = self.sites['Ann_mean_cfs']
        Eval['Ann_hi_cfs'] = self.sites['Ann_hi_cfs']
        Eval['Location'] = self.sites.NWIS_sitename

        #remove locations from Eval that do not have usgs values
        Eval = Eval[Eval['KGE'] > -1000]
        
        #sort dataframe and reindex
        self.Eval = Eval.sort_values('KGE', ascending = False).reset_index(drop = True)    
        #display evaluation DF
        display(self.Eval)
        
        #plot the model performance vs LULC to identify any relationships indicating where/why model performance
        #does well or poor
        #make all very negative KGE values -1
        self.Eval['KGE'][self.Eval['KGE'] < -1] = -1

        fig, ax = plt.subplots(3, 3, figsize = (11,11))
        fig.suptitle('Watershed Charcteristics vs. Model Performance', fontsize = 16)

        ax1 = ['Drainage_area_mi2', 'Mean_Basin_Elev_ft', 'Perc_Forest']
        for var in np.arange(0,len(ax1),1):
            variable = ax1[var]
            
            #remove na values for variables to make trendline
            cols = ['KGE', variable]
            df = self.Eval[cols]
            df.dropna(axis = 0, inplace = True)
            x = df['KGE']
            y = df[variable]
            ax[0,var].scatter(x = x, y = y)
            ax[0,var].set_ylabel(ax1[var])
            #add trendline
            #calculate equation for trendline
            try:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                #add trendline to plot
                ax[0,var].plot(x, p(x), color = 'r', linestyle = '--')
            except:
                pass

        ax2 = ['Perc_Imperv', 'Perc_Herbace', 'Mean_Ann_Precip_in']
        for var in np.arange(0,len(ax2),1):
            variable = ax2[var]
             #remove na values for variables to make trendline
            cols = ['KGE', variable]
            df = self.Eval[cols]
            df.dropna(axis = 0, inplace = True)
            x = df['KGE']
            y = df[variable]
            ax[1,var].scatter(x = x, y = y)
            ax[1,var].set_ylabel(ax2[var])
            #add trendline
            try:
                #calculate equation for trendline
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                #add trendline to plot
                ax[1,var].plot(x, p(x), color = 'r', linestyle = '--')
            except:
                pass

        ax3 = ['Ann_low_cfs', 'Ann_mean_cfs', 'Ann_hi_cfs']
        for var in np.arange(0,len(ax3),1):
            variable = ax3[var]
             #remove na values for variables to make trendline
            cols = ['KGE', variable]
            df = self.Eval[cols]
            df.dropna(axis = 0, inplace = True)
            x = df['KGE']
            y = df[variable]
            ax[2,var].scatter(x = x, y = y)
            ax[2,var].set_xlabel('Model Performance (KGE)')
            ax[2,var].set_ylabel(ax3[var])
            #add trendline
            #calculate equation for trendline
            try:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                #add trendline to plot
                ax[2,var].plot(x, p(x), color = 'r', linestyle = '--')
            except:
                pass


        plt.tight_layout()
        plt.show()
        
        num_figs = len(self.Eval)
        self.sites.reset_index(inplace = True, drop = True)
        for i in np.arange(0,num_figs,1):

            reach = self.Eval[reachid][i]
            site = self.Eval['NWIS_site_id'][i]
            #print(site, reach)
            sitename = self.Eval.Location[i]
            print(sitename)

            plot_title = self.freqkeys[self.freq]+ ' (' + self.units +') \n Performance of ' + self.model +' predictions, reach: ' + str(reach) + '\n USGS:' + str(site) +' ' + str(sitename)
            NWIS_site_lab = 'USGS: ' + str(site)
            Mod_reach_lab = self.model + ': ' + str(reach)

            Eval_cols = [NWIS_site_lab, Mod_reach_lab]

            #Adjust for different time intervals here
            #Daily

            Eval_df = pd.DataFrame(index = self.NWIS_data_resampled[site].index, columns = Eval_cols)
            Eval_df[Mod_reach_lab] = self.Mod_data_resampled[reach]
            Eval_df[NWIS_site_lab] = self.NWIS_data_resampled[site]

            Eval_df = Eval_df[Eval_df>0] 
            Eval_df = Eval_df.dropna()

            if Eval_df.shape[0] >= 1:
                #display(Eval_df)
                #need to have datetime fixed
                Eval_df = Eval_df.reset_index()
                Eval_df['Datetime'] = pd.to_datetime(Eval_df['Datetime'])
                Eval_df.set_index('Datetime', inplace = True, drop = True)
                
                #get observed and prediction data
                obs = Eval_df[NWIS_site_lab]
                mod = Eval_df[Mod_reach_lab]

                #remove na values or 0
                df = pd.DataFrame()
                df['obs'] = obs
                df['mod'] = mod.astype('float64')
                df = df[df>0]
                df.dropna(inplace=True)
                
                if len(df) >=1:
                    df['error'] = df['obs'] - df['mod']
                    df['P_error'] = abs(df['error']/df['obs'])*100
                    #drop inf values
                    df.replace([np.inf, -np.inf], np.nan, inplace = True)
                    df.dropna(inplace = True)

                    obs = df['obs']
                    mod = df['mod']

                    #calculate scoring
                    rmse = round(mean_squared_error(obs, mod, squared=False))
                    maxerror = round(max_error(obs, mod))
                    MAPE = round(mean_absolute_percentage_error(obs, mod)*100)
                    kge, r, alpha, beta = he.evaluator(he.kge, mod.astype('float32'), obs.astype('float32'))

                    #set limit to MAPE error
                    if MAPE > 1000:
                        MAPE ='> 1000'

                    rmse_phrase = 'RMSE: ' + str(rmse) +' ' +  self.units
                    error_phrase = 'Max Error: ' + str(maxerror) +' ' + self.units
                    mape_phrase = 'MAPE: ' + str(MAPE) + '%'
                    kge_phrase = 'kge: ' + str(round(kge[0],2))

                    max_flow = max(max(Eval_df[NWIS_site_lab]), max(Eval_df[Mod_reach_lab]))
                    min_flow = min(min(Eval_df[NWIS_site_lab]), min(Eval_df[Mod_reach_lab]))

                    flow_range = np.arange(min_flow, max_flow, (max_flow-min_flow)/100)

                    if self.freq == 'A':
                        bbox_L = -int(round((len(Eval_df)*.32),0))
                        text_bbox_L = -int(round((len(Eval_df)*.18),0))

                    else:
                        bbox_L = -int(round((len(Eval_df)*.32),0))
                        text_bbox_L = -int(round((len(Eval_df)*.16),0))

                    Discharge_lab = 'Discharge (' +self.units +')'
                    Obs_Discharge_lab = ' Observed Discharge (' +self.units +')'
                    Mod_Discharge_lab = self.model +' Discharge (' +self.units +')'


                    NWIS_hydrograph = hv.Curve((Eval_df.index, Eval_df[NWIS_site_lab]), 'DateTime', Discharge_lab, label = NWIS_site_lab).opts(title = plot_title, tools = ['hover'], color = 'orange')
                    Mod_hydrograph = hv.Curve((Eval_df.index, Eval_df[Mod_reach_lab]), 'DateTime', Discharge_lab, label = Mod_reach_lab).opts(tools = ['hover'], color = 'blue')
                    RMSE_hv = hv.Text(Eval_df.index[text_bbox_L],max_flow*.93, rmse_phrase, fontsize = 8)
                    Error_hv = hv.Text(Eval_df.index[text_bbox_L],max_flow*.83, error_phrase, fontsize = 8)
                    MAPE_hv = hv.Text(Eval_df.index[text_bbox_L],max_flow*.73, mape_phrase, fontsize = 8)
                    KGE_hv = hv.Text(Eval_df.index[text_bbox_L],max_flow*.63, kge_phrase, fontsize = 8)
                    textbox_hv = hv.Rectangles([(Eval_df.index[bbox_L], max_flow*.56, Eval_df.index[-1], max_flow*.99)]).opts(color = 'white')

                    Mod_NWIS_Scatter = hv.Scatter((Eval_df[NWIS_site_lab], Eval_df[Mod_reach_lab]), Obs_Discharge_lab, Mod_Discharge_lab).opts(tools = ['hover'], color = 'blue', xrotation=45)
                    Mod_NWIS_one2one = hv.Curve((flow_range, flow_range)).opts(color = 'red', line_dash='dashed')

                    display((NWIS_hydrograph * Mod_hydrograph*textbox_hv*RMSE_hv*Error_hv*MAPE_hv*KGE_hv).opts(width=600, legend_position='top_left', tools=['hover']) + (Mod_NWIS_Scatter*Mod_NWIS_one2one).opts(shared_axes = False))

            else:
                print('No data for NWIS site: ', str(NWIS_site_lab), ' skipping.')

            result_reach =self.Eval #Shahab added this on 09.22.2023
            #return result_reach     #Shahab added this on 09.22.2023
            result_reach.to_csv(f"{self.cwd}/LULC_Streamflow_SA/ROSET-AWS/SEED-ROSET/SEED_data/result_reach.csv", index=False) #Shahab added this
            
            
            