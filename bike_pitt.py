'''
Theresa Hutchins
Assignmnent 1
Mon Oct 4
CS1656
Bike Database
'''

#import argparse
#import collections
#import csv
import json
#import glob
import math
import os
import pandas as pd
from pandas.io.json import json_normalize
#import re
from requests import get
import string
import sys
#import time
#import xml
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



class Bike():
    def __init__(self, baseURL, station_info, station_status):
    # initialize the instance
    #get df for station_info
        url = baseURL+station_info
        self.response = get(url, verify=False)
        self.info = json.loads(self.response.content)       
        self.df=pd.json_normalize(self.info,['data','stations'])
       
    #get df for station_status   
        url2 = baseURL+station_status
        self.response2 = get(url2, verify=False)
        self.status = json.loads(self.response2.content)       
        self.df2=pd.json_normalize(self.status,['data','stations'])

        dfs = [self.df.dropna(), self.df2.dropna()]
        self.merge = pd.concat(dfs)

        #station_status: ['station_id', 'num_bikes_available', 'num_docks_available', 'is_installed', 
        #'is_renting','is_returning', 'last_reported']
    
        #station_info: ['station_id', 'name', 'short_name', 'lat', 'lon', 'region_id', 'capacity'])
        
        
    def total_bikes(self):
        # return the total number of bikes available
        btot = self.df2['num_bikes_available'].sum()
        return btot

    def total_docks(self):
        # return the total number of docks available
        dtot = self.df2['num_docks_available'].sum()
        return dtot

    def percent_avail(self, station_id):
        # return the percentage of available docks

        if str(station_id) in self.df2.values:

            row = self.df2[self.df2["station_id"] == str(station_id)]
            nbikes = row.num_bikes_available.item()
            ndocks = row.num_docks_available.item()
            percent = ndocks/(nbikes+ndocks)

            return str(int(percent*100))+"%"
        else:
            return ''
      
      

    def closest_stations(self, latitude, longitude):
        # return the stations closest to the given coordinates
        self.df3 = pd.DataFrame()
        dict1={}

        for index, row in self.merge.iterrows():
            dist = self.distance(row['lat'],row['lon'],latitude,longitude)
            self.df3 = self.df3.append({'dist':dist, 'station_id':row['station_id'], 'name': row['name']},
                ignore_index=True)

        self.df3 = self.df3.sort_values(['dist'], ascending=True)
        self.df3=self.df3.iloc[:3]

        for index, row in self.df3.iterrows():
            dict1[row['station_id']]= row['name']

        return dict1


    def closest_bike(self, latitude, longitude):
        # return the station with available bikes closest to the given coordinates
        self.df4 = pd.DataFrame()
        dict4={}

        for index, row in self.merge.iterrows():
            dist = self.distance(row['lat'],row['lon'],latitude,longitude)
            self.df4 = self.df4.append({'dist':dist, 'station_id':row['station_id'], 'name': row['name']},
                ignore_index=True)

        self.df4 = self.df4.sort_values(['dist'], ascending=True)
        self.df4=self.df4.iloc[:1]

        for index, row in self.df4.iterrows():
            dict4[row['station_id']]= row['name']

        return dict4
        
    def station_bike_avail(self, latitude, longitude):
        # return the station id and available bikes that correspond to the station with the given coordinates
        if ((self.df['lat'] == latitude) & (self.df['lon'] == longitude)).any():
            dict5={}
            row = self.merge[(self.merge.lat == latitude)&(self.merge.lon == longitude)].index.item()
            df3 = self.merge.loc[row, ['station_id', 'num_bikes_available']] 
  
            for index, row in df3.iterrows():
                dict5[row['station_id']]= row['num_bikes_available']
        
            return dict5
        else:
            return {}

    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))


# testing and debugging the Bike class

if __name__ == '__main__':
    instance = Bike('https://api.nextbike.net/maps/gbfs/v1/nextbike_pp/en', '/station_information.json', '/station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342885) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(40.438761, -79.997436) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)
