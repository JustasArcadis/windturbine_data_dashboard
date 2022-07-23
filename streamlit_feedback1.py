import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

st.sidebar.title("Please upload csv file before continuing")
# uploaded_file = st.sidebar.file_uploader('Choose a csv file', type = 'csv', key = 'uploaded_file')
uploaded_file = 'all_df_v2.csv'
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
     
     
     ICON_URL = 'data:image/png;base64,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'


     icon_data = {
     # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
     # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
     "url": ICON_URL,
     "width": 342,
     "height": 1542,
     "anchorY": 742,
     }

     data = pd.read_csv('eeker_gps.csv')
     data["icon_data"] = None
     for i in data.index:
          data["icon_data"][i] = icon_data


     icon_layer = pdk.Layer(
     type="IconLayer",
     data=data,
     get_icon="icon_data",
     get_size=4,
     size_scale=15,
     get_position=["Longitude", "Latitude"],
     pickable=True,
     )



     view_state = pdk.ViewState(latitude=avg_lat, longitude=avg_lon, zoom=11, bearing=0, pitch=45)
     
     r = pdk.Deck(layers=[layer, icon_layer], initial_view_state=view_state, tooltip= {"text": "{position}\nCount: {count}\nFeedback: {Feedback}"}, map_style=pdk.map_styles.ROAD)
     map = st.pydeck_chart(pydeck_obj=r, use_container_width=False)
     






     weather_df = all_df[['ws_HH', 'wd_HH', 'turb', 'gust', 'shear', 'pasquil', 'ws_diff', 'time']]
     weather_lst =st.multiselect(
                    'weather variable',
                    list(weather_df.columns), key = 'weather_multiselect')
     st.write('You selected:', weather_lst)
     weather_time = px.scatter(weather_df, x="time", y=weather_lst,  render_mode="webgl")
     st.plotly_chart(weather_time, use_container_width=True)   


