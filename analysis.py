import glob
import os
import subprocess

import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import shapely
import numpy as np
import imageio


# Get data and save on disk ---------------------------------------------------
# Source: https://github.com/CSSEGISandData/COVID-19.git
if not os.path.exists('COVID-19/'):
    os.mkdir('COVID-19/')
    subprocess.call("git -C COVID-19/ clone https://github.com/CSSEGISandData/COVID-19.git")
else:
    subprocess.call("git -C COVID-19/ pull https://github.com/CSSEGISandData/COVID-19.git")


# Read data into dataframe ----------------------------------------------------
base_path = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"
files = glob.glob(base_path+"/*.csv")
df = pd.DataFrame()

for file in files:
    loc_df = pd.read_csv(file)
    
    df = df.append(loc_df, sort=False)
    
df.reset_index(drop=True, inplace=True)

# Merge Country/Region and Country columns
for idx in df.index:
    if str(df.at[idx, 'Country/Region']) == 'nan':
        df.loc[idx, 'Country/Region'] = df.loc[idx,'Country']
                
df['Last Update'] = pd.to_datetime(df['Last Update'])
      
df = df.fillna(0)

# Replace country names to match with geo data
df['Country/Region'] = df['Country/Region'].str.strip()
df['Country/Region'] = df['Country/Region'].replace('Bosnia and Herzegovina', "Bosnia and Herz.")
df['Country/Region'] = df['Country/Region'].replace('Czech Republic', "Czechia")
df['Country/Region'] = df['Country/Region'].replace('Dominican Republic', "Dominican Rep.")
df['Country/Region'] = df['Country/Region'].replace('Hong Kong SAR', "Hong Kong")
df['Country/Region'] = df['Country/Region'].replace('Iran (Islamic Republic of)', "Iran")
df['Country/Region'] = df['Country/Region'].replace('Ivory Coast', "Côte d'Ivoire")
df['Country/Region'] = df['Country/Region'].replace('Macao SAR', "Macau")
df['Country/Region'] = df['Country/Region'].replace('Mainland China', 'China')
df['Country/Region'] = df['Country/Region'].replace('North Macedonia', 'Macedonia')
df['Country/Region'] = df['Country/Region'].replace('North Ireland', 'N. Ireland')
df['Country/Region'] = df['Country/Region'].replace('Republic of Ireland', 'Ireland')
df['Country/Region'] = df['Country/Region'].replace('Republic of Korea', 'South Korea')
df['Country/Region'] = df['Country/Region'].replace('Republic of Moldova', 'Moldova')
df['Country/Region'] = df['Country/Region'].replace('Russian Federation', 'Russia')
df['Country/Region'] = df['Country/Region'].replace('UK', 'United Kingdom')
df['Country/Region'] = df['Country/Region'].replace('US', 'United States of America')
df['Country/Region'] = df['Country/Region'].replace('United States', 'United States of America')
df['Country/Region'] = df['Country/Region'].replace('Viet Nam', 'Vietnam')

df = df.drop_duplicates()


# Read geo data ---------------------------------------------------------------
# Source: https://www.naturalearthdata.com/
path_geo_110 = "data_maps/mapunits110m/ne_110m_admin_0_map_units.shp"
df_geo_110 = geopandas.read_file(path_geo_110)


# Functions --------------------------------------------------------------
def plot_world(land_color, water_color, alpha):
    fig, ax = plt.subplots(figsize=(15.5, 8))
    
    # And then there was water
    ax.set_facecolor(water_color)
    
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Set borders of the world
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    
    for idx in df_geo_110.index:
        loc_geometry = df_geo_110.loc[idx, 'geometry']
        
        # Single polygon
        if type(loc_geometry) is shapely.geometry.polygon.Polygon:
            ax.plot(*loc_geometry.exterior.xy, 'k', zorder=100)
        else:
            # Multi polygon        
            for i in range(len(loc_geometry)):
                ax.plot(*loc_geometry[i].exterior.xy, 'k', zorder=100)
           
        plot_fill(ax, df_geo_110.at[idx, 'NAME'], 'white', df_geo_110, 1)
        plot_fill(ax, df_geo_110.at[idx, 'NAME'], land_color, df_geo_110, alpha, zorder=10)
            
    return fig, ax
            

def plot_fill(ax, country, color, df_geo_110, alpha=1, zorder=1, verbosity=0):
    loc_df = df_geo_110[df_geo_110['NAME']==country]
    if len(loc_df)==0 and verbosity==1:
        print(f'Country name {country} not found')
        return
    
    loc_geometry = loc_df['geometry']
    
    # Single polygon
    if len(loc_geometry) == 1:
        loc_geometry.plot(color=color, ax=ax, alpha=alpha, zorder=zorder)
    else:
        # Multi polygon        
        for i in range(len(loc_geometry)):
            loc_geometry[i].plot(color=color, ax=ax, alpha=alpha, zorder=zorder)
            
            
def plot_graph(ax, history, x0, x1, y0, y1):
    x = np.linspace(x0, x1, len(history))
    y = y0 + (y1-y0)*np.array(history)/max(history)
    
    ax.plot(x, y, 'r')
    ax.scatter(x[-1], y[-1], color='r')
    
    ax.text(x1+5, y[-1], f'{int(history[-1]):,d}')
    

def process_data(df, col, dates, title, savename, t_total=10, t_last=2):
    path = f'output/{savename}/'
    
    # Create output dir if it does not exist
    if not os.path.exists('output'):
        os.mkdir('output')
    if not os.path.exists(path):
        os.mkdir(path)
    
    # Load history if file exists
    if os.path.exists('df_history.csv'):
        df_history = pd.read_csv('df_history.csv', index_col=0)
        df_history.index = pd.to_datetime(df_history.index).date
    else:
        df_history = pd.DataFrame()
    
    print(f'\nProcessing {col}')
    for i, date in enumerate(dates):
        output_path = path+date.strftime('img%Y%m%d.png')
        
        if col in df_history.columns \
            and date in df_history[col].index \
            and not np.isnan(df_history.loc[date, col]):
            print(f'{date} already in history')
            continue
                
        print(f'{date}')
        loc_df = df_maxday[df_maxday['Date']<=date]
        
        # Find latest info  
        max_date = loc_df.groupby(by=['Country/Region', 'Province/State'])['Date'].max()
        max_date = max_date.reset_index()
        
        # Set values in dict
        loc_df.set_index(['Country/Region', 'Province/State', 'Date'], inplace=True)
        
        dict_data = {} 
        df_history.at[date, col] = 0
        for idx in max_date.index:
            country = max_date.at[idx, 'Country/Region']
            province = max_date.at[idx, 'Province/State']
            loc_date = max_date.at[idx, 'Date']
            value = loc_df.at[(country, province, loc_date), col]
            df_history.at[date, col] += value
            
            if country not in dict_data:
                dict_data[country] = value
            else:
                dict_data[country] += value
    
    
        fig, ax = plot_world(land_color='lightgreen', water_color=[172/255, 223/255, 255/255], alpha=0.3)
        ax.set_title(f'{date} - COVID-19 - {title}')
        
        # Plot dict countries
        for country in dict_data:
            if dict_data[country]==0:
                continue
            
            alpha = (np.log10(dict_data[country])/6)+0.02
            
            if alpha<=0:
                continue
            
            if country=='United Kingdom':
                for subcountry in ['England', 'Wales', 'Scotland']:
                    # Fill white then red
                    plot_fill(ax, subcountry, 
                              color='w', df_geo_110=df_geo_110, 
                              alpha=1)
                    plot_fill(ax, subcountry, 
                              color='r', df_geo_110=df_geo_110, 
                              alpha=alpha)
            else:
                # Fill white then red
                plot_fill(ax, country, 
                          color='w', df_geo_110=df_geo_110, 
                          alpha=1)
                plot_fill(ax, country, 
                          color='r', df_geo_110=df_geo_110, 
                          alpha=alpha, verbosity=1)
          
        
        # Sort and save history
        df_history.sort_index(inplace=True)
        df_history.to_csv('df_history.csv')
        history = df_history[df_history.index<=date][col].values
            
        # Plot graph
        plot_graph(ax, history, x0=-160, x1=-110, y0=-60, y1=-20)
        
        plt.savefig(output_path)
        plt.close()
        
        
    # Make GIF
    files = os.listdir(path)   
    t_frame = (t_total-t_last)/(len(files)+1)
    
    images = []
    for file in files:
        images.append(imageio.imread(f'{path}{file}'))
        
    # Show last frame for t_last seconds
    for i in range(int(np.ceil(t_last/t_frame))):
        images.append(imageio.imread(f'{path}{file}'))
        
        
    # Insert white frame at the end
    images.append(0*imageio.imread(f'{path}/{file}')+255)
    
    imageio.mimsave(f'{savename}.gif', images, duration=t_frame)
    

# Main code -------------------------------------------------------------------
# Add column active cases
df['Active'] = df['Confirmed']-df['Deaths']-df['Recovered']

# Scale df by max infected
df['Date'] = df['Last Update'].dt.date

# Filter data to have max per day
df_maxday = df.groupby(by=['Country/Region', 'Province/State', 'Date']).max()
df_maxday = df_maxday[['Confirmed', 'Deaths', 'Active']]
df_maxday.reset_index(inplace=True)
       
dates = sorted(df['Date'].unique())


# Plotting - Confirmed
col = 'Confirmed'
title = 'Confirmed infections'
savename = 'confirmed'

process_data(df, col, dates, title, savename)


# Plotting - Deaths
col = 'Deaths'
title = 'Deaths'
savename = 'deaths'

process_data(df, col, dates, title, savename)


# Plotting - Active cases
col = 'Active'
title = 'Active cases'
savename = 'active'

process_data(df, col, dates, title, savename)
