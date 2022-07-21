from tabnanny import check
import pandas as pd
import numpy as np
import streamlit as st
import datetime
import leafmap.kepler as leafmap
import geopandas
import pydeck as pdk
import plotly.express as px
import pydeck as pdk
import random
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

st.sidebar.title("Please upload csv file before continuing")
uploaded_file = st.sidebar.file_uploader('Choose a csv file', type = 'csv', key = 'uploaded_file')
# uploaded_file = 'all_df_v2.csv'
if uploaded_file is not None:
     
     all_df = pd.read_csv(uploaded_file)
     all_df['Time'] = pd.to_datetime(all_df['Time'])
     all_df['time'] = pd.to_datetime(all_df['time'])
     all_df['date'] = pd.to_datetime(all_df['Time']).dt.date
     all_df = all_df.set_index('Time')


     first_day = all_df['date'].iloc[0]
     last_day = all_df['date'].iloc[-1]
     start_date = st.sidebar.date_input('Start date', first_day)
     end_date = st.sidebar.date_input('End date', last_day)
     error_lst = []
     if start_date > end_date:
          error_txt_1 = 'Error: End date must fall after start date.'
          error_lst.append(error_txt_1)
     elif start_date < first_day:
          error_txt_2 = f'Error: Start date must be after {first_day}'
          error_lst.append(error_txt_2)
     elif end_date > last_day:
          error_txt_3 = f'Error: End date must be before {last_day}'
          error_lst.append(error_txt_3)
     if len(error_lst) == 0:
          st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
     else:
          error_str = " ".join(error_lst)
          st.sidebar.error(error_str)
          

     def get_night(all_df):
          Endcurtailment='2021-10-11 09:59:00'
          startcurtailment='2021-10-04 22:00:00'

          # array full of false, except true when time is 22:00:00
          tienuur=all_df.tienuur
          starttijd=all_df[tienuur].index


          zevenuur=all_df.zevenuur
          eindtijd=all_df[zevenuur].index


          starttijden=[]
          eindtijden=[]

          for x in starttijd:
               if x.date() <= pd.to_datetime(Endcurtailment).date() and x.date() >= pd.to_datetime(startcurtailment).date():
                    starttijden.append(x)

          for x in eindtijd:
               if x.date() <= pd.to_datetime(Endcurtailment).date() and x.date() >= pd.to_datetime(startcurtailment).date():
                    eindtijden.append(x)
          
          return starttijden, eindtijden

     starttijden, eindtijden = get_night(all_df)



     mask = (all_df['date'] >= start_date) & (all_df['date'] <= end_date)
     all_df = all_df.loc[mask]
     
     
     def plotly_2_axis_freq_vs_time(chart_data, freq_lst, checkbox_key):
     
          subfig = make_subplots(specs=[[{"secondary_y": True}]])

          # create two independent figures with px.line each containing data from multiple columns
          fig = px.scatter(chart_data, x="time", y=freq_lst,  render_mode="webgl")
          fig2 = px.scatter()
          
          show_feedback = st.checkbox('Show feedback', key = checkbox_key)
          if show_feedback:
               fig2 = px.scatter(all_df, x="time", y="Feedback",  color_discrete_sequence=['lime'],  render_mode="webgl")

          fig.update_traces(marker=dict(size=4))
          fig2.update_traces(marker=dict(size=12))
          fig2.update_traces(yaxis="y2")

          subfig.add_traces(fig.data + fig2.data)
          subfig.layout.xaxis.title="time"
          subfig.layout.yaxis.title="Tonal indication [dB]"
          subfig.layout.yaxis2.title="Feedback"
          subfig.add_hrect(y0=20, y1=chart_data[freq_lst].to_numpy().max() +10, line_width=0, fillcolor="red", opacity=0.4)

          for i in range(len(starttijden)):
               subfig.add_vrect(x0=starttijden[i], x1=eindtijden[i],
                              fillcolor="black", opacity=0.3, line_width=0, annotation_text="Night", annotation_position="top left")
          
          return subfig
     

               


     with st.expander("SWISS method"):
          swiss_freq_lst =st.multiselect(
               'choose swiss method frequency',
               [swiss_f.strip('SwissDiff') for swiss_f in list(all_df.columns) if 'Swiss' in swiss_f], key = 'selectbox_swiss_frequency')
          st.write('You selected swiss frequency of:', swiss_freq_lst)
          swiss_freq = ['SwissDiff'+swiss_freq if swiss_freq !='MaxValue' else 'Swiss' + swiss_freq for swiss_freq in swiss_freq_lst]
          
          chart_data_swiss = pd.concat([all_df['time'], all_df[swiss_freq]], axis=1)
          # fig = px.scatter(chart_data, x="Time", y=swiss_freq)
          # Create figure with secondary y-axis

          # subfig.show()
          if len(swiss_freq) != 0:
               subfig_swiss = plotly_2_axis_freq_vs_time(chart_data_swiss, swiss_freq, checkbox_key = 'swiss')
               st.plotly_chart(subfig_swiss, use_container_width=True)
                    
     with st.expander("ANSI method"):
          ANSI_freq_lst =st.multiselect(
               'choose ANSI method frequency',
               [ANSI_f.strip('ANSI_Diff') for ANSI_f in list(all_df.columns) if 'ANSI' in ANSI_f], key = 'selectbox_ANSI_frequency')
          st.write('You selected ANSI frequency of:', ANSI_freq_lst)
          
          ANSI_freq = ['ANSI_Diff'+ANSI_freq if ANSI_freq !='MaxValue' else 'ANSI' + ANSI_freq for ANSI_freq in ANSI_freq_lst]

          chart_data_ansi = pd.concat([all_df['time'], all_df[ANSI_freq]], axis=1)
          
          if len(ANSI_freq) != 0:
               subfig_ansi = plotly_2_axis_freq_vs_time(chart_data_ansi, ANSI_freq, checkbox_key= 'ANSI')
               st.plotly_chart(subfig_ansi, use_container_width=True)         
               
               
     
     with st.expander('ISO method'):
          ISO_freq_lst =st.multiselect(
               'choose ISO method frequency',
               [ISO_f.strip('ISO_Diff') for ISO_f in list(all_df.columns) if 'ISO' in ISO_f], key = 'selectbox_ISO_frequency')
          st.write('You selected ISO frequency of:', ISO_freq_lst)
          
          ISO_freq = ['ISO_Diff'+ISO_freq if ISO_freq !='MaxValue' else 'ISO' + ISO_freq for ISO_freq in ISO_freq_lst]

          chart_data_iso = pd.concat([all_df['time'], all_df[ISO_freq]], axis=1)
          # st.line_chart(chart_data.rename(columns={'time':'index'}).set_index('index'))
          
          if len(ISO_freq) != 0:
               subfig_iso = plotly_2_axis_freq_vs_time(chart_data_iso, ISO_freq, checkbox_key = 'ISO')
               st.plotly_chart(subfig_iso, use_container_width=True)                  


     map_df = all_df.copy()
     map_df = map_df.loc[map_df['Feedback'].notnull(), ['time', 'Feedback', 'location.1', 'location.2', 'Postcode', 'location.4', 'distance', 'orientation', 'survey_date', 'Longitude_corr', 'Latitude_corr']]
     map_df['location.12'] = map_df['location.1'] + map_df['location.2'].astype(str)
     # map_df.rename(columns={'Longitude_corr': 'longitude', 'Latitude_corr': 'latitude'}, inplace=True)



     map_df['COORDINATES'] = map_df[['Longitude_corr', 'Latitude_corr']].values.tolist()
     
     feedback_range = st.slider('Selected Feedback Range', value = [1, 7], min_value = int(min(map_df.Feedback)), max_value = int(max(map_df.Feedback)))

     # feedback_range = [1, 7]

     map_df = map_df.loc[(map_df['Feedback'] >= feedback_range[0]) & (map_df['Feedback'] <= feedback_range[1])]
     
     avg_lat = map_df['Latitude_corr'].mean()
     avg_lon = map_df['Longitude_corr'].mean()

     layer = pdk.Layer(
     "GridLayer", map_df, pickable=True, extruded=True, cell_size=80, elevation_scale=3, get_position="COORDINATES",
     )



     view_state = pdk.ViewState(latitude=avg_lat, longitude=avg_lon, zoom=11, bearing=0, pitch=45)
     r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip= {"text": "{position}\nCount: {count}\nFeedback: {Feedback}"}, map_style=pdk.map_styles.ROAD)
     map = st.pydeck_chart(pydeck_obj=r, use_container_width=False)
     






     weather_df = all_df[['ws_HH', 'wd_HH', 'turb', 'gust', 'shear', 'pasquil', 'ws_diff', 'time']]
     weather_lst =st.multiselect(
                    'weather variable',
                    list(weather_df.columns), key = 'weather_multiselect')
     st.write('You selected:', weather_lst)
     weather_time = px.scatter(weather_df, x="time", y=weather_lst,  render_mode="webgl")
     st.plotly_chart(weather_time, use_container_width=True)   


