# SEED-ROSET
This repository hosts all Python scripts and data access information for the coupling of SEED and ROSET.

![GitHub Front Page2](https://github.com/shahab122/SEED-ROSET/assets/28275758/ef112be7-7995-4a35-a796-de06815c39d4)

# Streamflow Extreme Event Dataset Deeveloper (SEED)

Streamflow Extreme Event Dataset (SEED) is a dataset that includes both flood and drought extreme events for the USGS sites collocated with the NHDPlus stream reaches over the entire contiguous United States (CONUS). SEED includes the extreme flood and drought events during the period 1980-2020.   

The following steps were used to develop SEED for the extreme flood events: 
**Step 1:** Collect streamflow data for the USGS sites that are collocated with the NHDPlus stream reaches 
**Step 2:** Select annual maximum streamflow series for each site over the entire data period
**Step 3:** Fit Log Pearson Type III (LP3) probability distribution to the annual maximum series 
**Step 4:** Calculate return period for each annual maximum streamflow value in the annual maximum series
**Step 5:** Identify the date of occurrence for each annual maximum streamflow value  

Now, the following steps were used to develop SEED for the extreme hydrological drought events:  
**Step 1:** Collect streamflow data for the USGS sites that are collocated with the NHDPlus stream reaches 
**Step 2:** Select annual minimum streamflow series for each site over the entire data period
**Step 3:** Fit Log Pearson Type III (LP3) probability distribution to the annual minimum series 
**Step 4:** Calculate return period for each annual minimum streamflow value in the annual minimum series
**Step 5:** Identify the date of occurrence for each annual minimum streamflow value

Good news is that the above steps were implemented in the Python based SEED-ROSET Tool. The SEED-ROSET coupling tool can be used to evaluate any hydrological model (e.g., NWM v2.1) and present the evaluation results in maps and hydrograph plots including many other options. 

**Assumptions**
The SEED framework follows the assumptions recommended in USGS Bulletin 17C, namely: (1) the annual maximum and minimum series are assumed stationary within the analysis period; (2) flow data are log-transformed prior to fitting; and (3) the LP3 parameters—mean, standard deviation, and skew—are estimated using the method-of-moments approach with the skew bounded between –3 and +3 to avoid instability.


## Application of SEED

SEED can be used to develop our understanding of “appropriate model formulations” to address diversity of dominant hydrologic processes, select the best model structure and discretization to represent these dominant hydrological processes. Thus, SEED can help researchers of CIROH (as well as outside CIROH) to develop multi-model mosaic in the NextGen framework. So why are we evaluating the model performance? Because we need the appropriate model formulations that perform we in all hydroclimatic conditions over entire CONUS and other parts of North America as well. 

We also developed a Python-based tool for model evaluation and we call it the Research-Oriented Streamflow Evaluator Tool or ROSET. It is a Python-based, user-friendly, fast, and model agnostic streamflow evaluator tool. This tool can used for any model that uses NHDPlus dataset. It allows a user to evaluate the performance of the National Water Model as well as any other models. This Python-based tool helps visualize the results and investigate the model performance interactively. The current version of the tool is available on github.

[https://github.com/whitelightning450/Streamflow_Evaluator](https://github.com/whitelightning450/Research-Oriented-Streamflow-Evaluation-Tool)

A more advanced version of ROSET, which will be called Community Streamflow Evaluation System (CSES), is available on github as well:

https://github.com/whitelightning450/Community-Streamflow-Evaluation-System

The ROSET can be used to show the relationship between LULC and the model performance, thus efforts are being made towards connecting regionally specific hydrology to the model performance. It can be used to HUC-based and Reach-based evaluation of the hydrologic models as well. 

SEED supports repeatable and quantifiable hydrologic model evaluation, especially when coupled with the esearch-Oriented RStreamflow Evaluator Tool (ROSET). This workflow helps to better understand dominant hydrological processes as well as when, where, and why they occur and paves a way toward selecting the appropriate model mosaic. Coupled SEED and ROSET is a framework to develop understanding of performance of different models and configurations that lead towards selecting appropriate models for use in the NextGen framework. SEED can be applied in the event-based evaluation of hydrologic models and can tell us where model performance needs improvement.   

Once we get the start and end dates of a hydrological event, we can use the Tethys-CSES App to evaluate the performance of a hydrological model (e.g., NWM) in predicting this particular hydrological event. The GitHUb page for the app is avialble here which also inlcudes the link to the Tethys-CSES App:

https://github.com/AlabamaWaterInstitute/Tethys-CSES

### Data Access

The same data access process will be followed here as it is mentioned in the ROSET GitHub page. This is what mentioned there which is worth repeaating here: 

"Community-Streamflow-Evaluation-System leverages USGS/NWIS observations from 1980-2020 and colocated and while all data is publically available through the respective agencies, we found the download time to be preventative for a timely model evaluation. The Alabama Water Institute at the University of Alabama hosts NWM v2.1 retrospective for all colocated USGS monitoring stations at a daily temporal resolution and provides the data free of charge via access to Amazon AWS S3 cloud storage. Community-Streamflow-Evaluation-System can quickly access observed and predicted data supporting a fast and repeatable tool for evaluating modeled streamflow performance."

#### How to use SEED Coupled with ROSET? 

**First**, we will be asked to select the type of extreme events between 'flood' and 'drought':

![image](https://github.com/shahab122/SEED-ROSET/assets/28275758/c3efc920-47cc-475a-a2e0-180c85055a92)

**Second**, we will declare which State (e.g.,' al' for Alabama) and the HUC ids (e.g., '1601') of our interest. Then, initialize ROSET to get the USGS IDs located within the selected State (e.g., 'al') and HUC. We can select multiple States and HUCs for our analysis. 

![chrome_xxBef1HfdQ](https://github.com/shahab122/SEED-ROSET/assets/28275758/8ab9e5b8-155a-439f-afe8-094c3bf6d049)

**Third**, we have to select between State-level ('lulc') and HUC-level ('huc') analysis:

![chrome_WmLIkp7d8f](https://github.com/shahab122/SEED-ROSET/assets/28275758/e9840de1-813f-4e22-85b3-f98d3628055b)

**Fourth**, we will be asked to select a return interval (e.g., 50 years) for the extreme flood or drought events:

![chrome_JAZVHzRtvu](https://github.com/shahab122/SEED-ROSET/assets/28275758/97d41dae-e902-45cb-8b81-246418d8fcfe)

**Fifth**, Now we have to select the event type again to confirm that we are interested in flood or drought:

![chrome_Rz68Ro4ucr](https://github.com/shahab122/SEED-ROSET/assets/28275758/c12cb118-3ea4-4052-bf6d-25ec8308f019)

**Sixth**, here we will be asked to define the size of the window (number of days) that will be used in the model evaluation. THis step allows us to select a number of days before and after the occurence date of the extreme flood or drought event. 

![chrome_LUzJTTydU8](https://github.com/shahab122/SEED-ROSET/assets/28275758/39c8a2c2-b3b8-4be2-967b-5c4531fc9e99)

**Seventh**, we will be getting the NWIS and NWM data required for the model evaluation for the selected windows defined in the previous step:

![chrome_1jWZM1Nmhp](https://github.com/shahab122/SEED-ROSET/assets/28275758/1d6f15eb-25cb-484e-afb4-79e968c04e3b)

**Eighth**, the results from ROSET based on the events selected by SEED can be displayed in the map for the USGS sites under a State (e.g., 'al') or under a HUC (e.g., '1601') that were identified in the **Second** step.  

![image](https://github.com/shahab122/SEED-ROSET/assets/28275758/5ab1b170-e00e-4c73-843e-ef9c70b0439e)

Fianlly, the model performance metrics (e.g., KGE) can be displayed in a table and the observed and modelled hydrographs are also made available for any interactive evaluation of the model. 

![chrome_PRLhvtPdx8](https://github.com/shahab122/SEED-ROSET/assets/28275758/04598e84-7110-4a3b-ac30-4e96c5bebe18)

![chrome_942MOzcx18](https://github.com/shahab122/SEED-ROSET/assets/28275758/649ba9d8-760f-4b0f-8c04-0cbebee5455d)

##### NOTE: THIS TOOL IS UNDER DEVELOPMENT

###### Funding Acknowledgement 
This research was supported by the Cooperative Institute for Research to Operations in Hydrology (CIROH) with funding under award NA22NWS4320003 from the NOAA Cooperative Institute Program. The statements, findings, conclusions, and recommendations are those of the author(s) and do not necessarily reflect the opinions of NOAA.
