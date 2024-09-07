from flask import Flask, redirect, request, url_for
import requests

import time
import pickle
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
from stravalib.client import Client
client = Client()
# 設定 OAuth 參數
client_id = '128950'
client_secret = 'ab1832a30f475a93bd2292bf54576c1fb06be3bd'
redirect_uri = 'http://127.0.0.1:5000/authorization'

authorization_base_url = 'https://www.strava.com/oauth/authorize'
token_url = 'https://www.strava.com/oauth/token'
athlete_url = 'https://www.strava.com/api/v3/athlete'

# log config
TOKEN_PATH = "./access_token.pickle"
# Choose some fields of interest from this data in order to read into a DataFrame
my_cols =['name',
          'start_date_local',
          'type',
          'distance',
          'moving_time',
          'elapsed_time',
          'total_elevation_gain',
          'elev_high',
          'elev_low',
          'average_speed',
          'max_speed',
          'average_heartrate',
          'max_heartrate',
          'start_latlng']

@app.route('/')
def index():
    print(f"root")
    return '''
    <a href="/login">Connect with Strava</a>
    '''

@app.route('/login')
def login():
    scope = 'activity:read_all'
    authorization_url = f"{authorization_base_url}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    return redirect(authorization_url)

@app.route('/authorization')
def callback():
    print(f"authorization")
    code = request.args.get('code')
    access_token = []
    if code:
        try:
            if not os.path.isfile(TOKEN_PATH):
                access_token = client.exchange_code_for_token(client_id={client_id}, client_secret={client_secret}, code=code)
                with open(TOKEN_PATH, 'wb') as f:
                    pickle.dump(access_token, f)
            else:
                with open(TOKEN_PATH, 'rb') as f:
                    access_token = pickle.load(f)
    
            print('Latest access token read from file:',TOKEN_PATH )
            if time.time() > access_token['expires_at']:
                print('Token has expired, will refresh')
                refresh_response = client.refresh_access_token(client_id=MY_STRAVA_CLIENT_ID, 
                                                        client_secret=MY_STRAVA_CLIENT_SECRET, 
                                                        refresh_token=access_token['refresh_token'])
                access_token = refresh_response
                with open(TOKEN_PATH, 'wb') as f:
                    pickle.dump(refresh_response, f)
                print('Refreshed token saved to file')

                client.access_token = refresh_response['access_token']
                client.refresh_token = refresh_response['refresh_token']
                client.token_expires_at = refresh_response['expires_at']
                    
            else:
                print('Token still valid, expires at {}'
                    .format(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(access_token['expires_at']))))

                client.access_token = access_token['access_token']
                client.refresh_token = access_token['refresh_token']
                client.token_expires_at = access_token['expires_at']
                athlete = client.get_athlete()
                
                
                print("Athlete's name is {} {}, based in {}, {}"
                    .format(athlete.firstname, athlete.lastname, athlete.city, athlete.country))
                # info = athlete.to_dict()
                activities = client.get_activities(limit=1000)
                
                # list(activities)[0:10]
                data = []
                for activity in activities:
                    my_dict = activity.to_dict()
                    data.append([activity.id]+[my_dict.get(x) for x in my_cols])

                # Add id to the beginning of the columns, used when selecting a specific activity
                my_cols.insert(0,'id')
                df = pd.DataFrame(data, columns=my_cols)
                # Make all walks into hikes for consistency
                df['type'] = df['type'].replace('Walk','Hike')
                # Create a distance in km column
                df['distance_km'] = df['distance']/1e3
                # Convert dates to datetime type
                df['start_date_local'] = pd.to_datetime(df['start_date_local'])
                # Create a day of the week and month of the year columns
                df['day_of_week'] = df['start_date_local'].dt.day_name()
                df['month_of_year'] = df['start_date_local'].dt.month
                # Convert times to timedeltas
                df['moving_time'] = pd.to_timedelta(df['moving_time'])
                df['elapsed_time'] = pd.to_timedelta(df['elapsed_time'])
                # Convert timings to hours for plotting
                df['elapsed_time_hr'] = df['elapsed_time'].astype(int)/3600e9
                df['moving_time_hr'] = df['moving_time'].astype(int)/3600e9
                df.to_csv('./activities.csv')
            return "done"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {str(e)}"
    else:
        return 'Error: No code provided'



if __name__ == '__main__':
    app.run(debug=True)
