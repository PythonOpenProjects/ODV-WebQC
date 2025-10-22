# -*- coding: utf-8 -*-
'''
cd my/path/to/script/
streamlit run webqc-odv.py

numpy==1.23.5
python=3.11.5
pandas==2.0.3
altair==5.2.0
streamlit_extras==0.4.2
'''
import streamlit as st
import pandas as pd
#import numpy as np
import altair as alt
import math
import os, sys
import numpy
import uuid
import time
import shutil
from streamlit_extras.dataframe_explorer import dataframe_explorer
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="WebQC-ODV",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

#START HIDE the TOP an burger menu!
st.markdown("""
<style>
	[data-testid="stDecoration"] {
		display: none;
	}
    .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}

</style>""",
unsafe_allow_html=True)

ms = st.session_state
if "themes" not in ms: 
  ms.themes = {"current_theme": "dark",
                    "refreshed": True,
                    
                    "light": {"theme.base": "dark",
                              "button_face": "🌜"},

                    "dark":  {"theme.base": "light",
                              "button_face": "🌞"},
                    }


if ms.themes["current_theme"]=="dark":
    hide_streamlit_style = """
        <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0.5rem;}
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                    background-color: Chocolate;
                    border-color: #ff0000;
                }
            body
        </style>
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    
        """
else:
    hide_streamlit_style = """
        <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0.5rem;}
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                    background-color: gray;
                    border-color: #000000;
                }
            body
        </style>
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    
        """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
#STOP HIDE the TOP an burger menu!

def ChangeTheme():
  previous_theme = ms.themes["current_theme"]
  tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
  for vkey, vval in tdict.items(): 
    if vkey.startswith("theme"): st._config.set_option(vkey, vval)

  ms.themes["refreshed"] = False
  if previous_theme == "dark": ms.themes["current_theme"] = "light"
  elif previous_theme == "light": ms.themes["current_theme"] = "dark"
  
st.sidebar.title("ODV Web QC")
st.sidebar.title("Navigation Options")
default_value = 0
# Display different functionalities
choice = st.sidebar.selectbox('Select....', options=["HOME - Clear Data", "Edit Dataframe", "ODVs Quality Control", "ODVs Merge and plot"], index=default_value)
btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.sidebar.write (':blue[\nChange Theme:]')
st.sidebar.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
  ms.themes["refreshed"] = True
  st.rerun()


def function_cleaner(x):
   x = x.replace(' ', '_')
   x = x.replace(':', '_')
   x = x.replace('[', '_')
   x = x.replace(']', '_')
   x = x.replace('.', '_')
   x = x.replace('/', '_')
   x = x.replace('#', '_')
   x = x.replace(',', '_')
   x = x.replace(';', '_')
   x = x.replace(':', '_')
   x = x.replace('^', '_')
   x = x.replace('\'', '_')
   x = x.replace('"', '_')
   x = x.replace('(', '_')
   x = x.replace(')', '_')
   x = x.replace('&', '_')
   x = x.replace('.', '_')
   #print('change '+str(x))
   return x


def load_data_2_dataframe(file,separaval):
    if 'df' not in st.session_state:
        df = pd.read_csv(file,sep=separaval)
              
        for tmpcol in df.columns:
            cleanCol=function_cleaner(tmpcol)
            df.rename(columns={tmpcol: cleanCol}, inplace=True)      
        st.session_state['df'] = df
        st.data_editor(df)
    else:
        st.data_editor(st.session_state['df'])
        
    return st.session_state['df']

def reset_data():
    st.title(':blue[HOME PAGE] 🏠')
    st.write("Welcome to the home page")
    if 'dirname' not in st.session_state:
        st.write('')
        st.write('The cache is clear')
    else:
        import shutil
        shutil.rmtree(st.session_state['dirname'])
        st.write('')
        st.write('Deleted '+st.session_state['dirname'])
        del st.session_state['dirname']
    if 'df' in st.session_state:    
        del st.session_state['df']
    if 'dfodvmerge' in st.session_state:
        del st.session_state['dfodvmerge']
    #load_data()    

def reset_dataOdv():
    if 'dfodvmerge' not in st.session_state:
        print('Dataframe not found')
    else:
        del st.session_state['dfodvmerge']   
    load_Odvs()

def load_Odvs():
    '''
    loads the selected file into a dataframe
    stores the selected file and dataframe in st.session_state
    '''
    st.title(':blue[Merge ODVs in a dataset] 📒')
    st.write("You can load several ODVs to merge in a single dataframe")
    files = st.file_uploader("Upload ODV files", type=['txt'], accept_multiple_files=True)
    if 'dfodvmerge' in st.session_state and st.session_state['dfodvmerge'] is not None:
        st.write('Working...')      
    else:
        counterDummy=1
        idrnd = uuid.uuid4()
        dirname=str(time.strftime("%Y%m%d%H%M%S")+'-'+str(idrnd))
        os.mkdir(dirname)
        actualDir=os.getcwd()
        for uploaded_file in files:
            with open(os.path.join(dirname,uploaded_file.name),"wb") as f:
                f.write(uploaded_file.getbuffer())
        counterDummy=1
        li=[]
        for u in os.listdir(dirname):
            data=fromfileMerge(u,dirname)
            li.append(data)
            counterDummy += 1
        if counterDummy >1:
            dfodvmerge = pd.concat(li)         
            st.session_state['dfodvmerge'] = dfodvmerge
            st.dataframe(dfodvmerge)
        shutil.rmtree(dirname)
        
    '''
     Display different graphs to understand the data
    '''
    if 'dfodvmerge' in st.session_state and st.session_state['dfodvmerge'] is  not None:
        #st.title('PLOT Service')
        st.title(':blue[PLOT Service] 📊')
        dfodvmerge= st.session_state['dfodvmerge']
        CorrGraph = st.toggle('Correlation graph')
        
        if CorrGraph:
            fig, ax = plt.subplots(figsize=(10,10))
            # Create the heatmap
            sns.heatmap(dfodvmerge.corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)
            # Add a legend
            ax.legend()
            # Display the plot
            st.pyplot(fig)

        st.write("🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩")
        selected_columns = st.multiselect('Select columns to plot:', dfodvmerge.columns)
        plotstyle = st.selectbox(
                                'Select PLOT STYLE (only for line charts)',
                                ("default",
                        		"classic",
                        		"Solarize_Light2",
                        		"bmh",
                        		"dark_background",
                        		"ggplot",
                        		"grayscale",
                        		"seaborn-v0_8",
                        		"seaborn-v0_8-bright",
                        		"seaborn-v0_8-pastel"),
                                key="placeholder",
                                )

        plotLineChart = st.toggle('PLOT ALL PARAMS IN A SINGLE LINE CHART')
        ScatterGraph = st.toggle('PLOT ALL PARAMS IN a Scatter graph')
        AreaGraph = st.toggle('PLOT ALL PARAMS IN an Area graph')
        BarGraph = st.toggle('PLOT ALL PARAMS IN a Bar graph')
        singleplotLineChart = st.toggle('FOR EACH PARAM A SINGLE LINE CHART PLOT')
            
        if selected_columns is not None:
            if plotstyle=='':
                plt.style.use("default")
            else:
                plt.style.use(plotstyle)
            if plotLineChart:
                fig, ax = plt.subplots() 
                
                # Plot the data
                for column in selected_columns:
                    ax.plot(dfodvmerge[column], label=column)   
                # Set the axis labels
                ax.set_xlabel('X Axis')
                ax.set_ylabel('Y Axis')    
                # Set the title
                ax.set_title('Line Chart')    
                # Add a legend
                ax.legend()    
                # Display the plot
                st.pyplot(fig)
            
            if ScatterGraph:
                dftemp = pd.DataFrame()
                dftemp=pd.concat([dfodvmerge[selected_columns]])
                st.scatter_chart(dftemp)
            if AreaGraph:
                dftemp = pd.DataFrame()
                dftemp=pd.concat([dfodvmerge[selected_columns]])
                st.area_chart(dftemp)
            if BarGraph:
                dftemp = pd.DataFrame()
                dftemp=pd.concat([dfodvmerge[selected_columns]])
                st.bar_chart(dftemp)
                
            if singleplotLineChart:
                  
                # Plot the data
                for column in selected_columns:
                    fig, ax = plt.subplots()  
                    ax.plot(dfodvmerge[column], label=column)    
                    # Set the axis labels
                    ax.set_xlabel('X Axis')
                    ax.set_ylabel('Y Axis')    
                    # Set the title
                    ax.set_title('Line Chart')    
                    # Add a legend
                    ax.legend()    
                    # Display the plot
                    st.pyplot(fig)
    else:
        st.write('Please LOAD DATA')

def fromfileprecols(fn,dirname):
    """load 1 ODV file entirely into Odv object: dataframe + metadata fields for columns"""
    counterHeader = 1
    headODV=[]   
    try:
        f = open(dirname+'/'+fn,'r')
        while True:
            l=f.readline()
            if l.find('//')==-1:
                break
                       
            counterHeader += 1
    except IOError:
        sys.exit(-1)

    try:
        data = pd.read_csv(dirname+'/'+fn,sep='\t',index_col=False, na_values=numpy.nan, skiprows = counterHeader-1) #, parse_dates=[3], infer_datetime_format=True, date_parser=odvdatetime)
        dataCols=data[['Cruise', 'Station', 'Type', 'YYYY-MM-DDThh:mm:ss.sss', 'Longitude [degrees_east]', 'Latitude [degrees_north]', 'LOCAL_CDI_ID', 'EDMO_code', 'Bot. Depth [m]']].copy()
    except ValueError as e:
        st.write("There are some problems with the file: "+fn)
        st.write(e)

    return dataCols

def fromfilecoords(fn,dirname):
    """load 1 ODV file entirely into Odv object: dataframe + metadata fields for columns"""
    counterHeader = 1
    headODV=[]
    
    try:
        f = open(dirname+'/'+fn,'r')
        while True:
            l=f.readline()
            if 'Cruise' in l:
                headODV.append(l)            
            if l.find('//')==-1:
                break
            else:
                headODV.append(l)            
            counterHeader += 1
    except IOError:
        sys.exit(-1)

    try:
        data = pd.read_csv(dirname+'/'+fn,sep='\t',index_col=False, na_values=numpy.nan, skiprows = counterHeader-1) #, parse_dates=[3], infer_datetime_format=True, date_parser=odvdatetime)
        data.columns = [c.replace(' ', '_') for c in data.columns]
        data['Station'].fillna(method='ffill', inplace = True)
        data['Longitude_[degrees_east]'].fillna(method='ffill', inplace = True)
        data['Latitude_[degrees_north]'].fillna(method='ffill', inplace = True)
        data['LOCAL_CDI_ID'].fillna(method='ffill', inplace = True)
        data['filename']=fn
        data['filename'].fillna(method='ffill', inplace = True)
        dataCoords=data[['filename', 'Latitude_[degrees_north]', 'Longitude_[degrees_east]', 'LOCAL_CDI_ID']].copy()
    except ValueError as e:
        st.write("There are some problems with the file: "+fn)
        st.write(e)

    return dataCoords.drop_duplicates(),headODV


def fromfile(fn,dirname):
    """load 1 ODV file entirely into Odv object: dataframe + metadata fields for columns"""
    counterHeader = 1
    headODV=[]  
    try:
        f = open(dirname+'/'+fn,'r')
        while True:
            l=f.readline()
            if l.find('//')==-1:
                break
            else:
                headODV.append(l)
            counterHeader += 1
    except IOError:
        sys.exit(-1)

    try:
        data = pd.read_csv(dirname+'/'+fn,sep='\t',index_col=False, na_values=numpy.nan, skiprows = counterHeader-1) #, parse_dates=[3], infer_datetime_format=True, date_parser=odvdatetime)
        data.columns = [c.replace(' ', '_') for c in data.columns]
        data['Cruise'].fillna(method='ffill', inplace = True)
        data['Station'].fillna(method='ffill', inplace = True)
        data['Type'].fillna(method='ffill', inplace = True)
        if 'YYYY-MM-DDThh:mm:ss.sss' in data.columns:
            data['YYYY-MM-DDThh:mm:ss.sss'].fillna(method='ffill', inplace = True)
        if 'YYYY-MM-DDThh:mm:ss' in data.columns:
            data['YYYY-MM-DDThh:mm:ss'].fillna(method='ffill', inplace = True)
        data['Longitude_[degrees_east]'].fillna(method='ffill', inplace = True)
        data['Latitude_[degrees_north]'].fillna(method='ffill', inplace = True)
        data['LOCAL_CDI_ID'].fillna(method='ffill', inplace = True)
        data['EDMO_code'].fillna(method='ffill', inplace = True)
        data['Bot._Depth_[m]'].fillna(method='ffill', inplace = True)
        data['filename']=fn
        data['filename'].fillna(method='ffill', inplace = True)
    except ValueError as e:
        st.write("There are some problems with the file: "+fn)
        st.write(e)

    return data,headODV



def fromfileMerge(fn,dirname):
    """load 1 ODV file entirely into Odv object: dataframe + metadata fields for columns"""
    counterHeader = 1   
    try:
        f = open(dirname+'/'+fn,'r')
        while True:
            l=f.readline()
            if l.find('//')==-1:
                break
            counterHeader += 1
    except IOError:
        sys.exit(-1)

    data = pd.read_csv(dirname+'/'+fn,sep='\t',index_col=False, na_values=numpy.nan, skiprows = counterHeader-1) #, parse_dates=[3], infer_datetime_format=True, date_parser=odvdatetime)
    data.columns = [c.replace(' ', '_') for c in data.columns]
    data['Cruise'].fillna(method='ffill', inplace = True)
    data['Station'].fillna(method='ffill', inplace = True)
    data['Type'].fillna(method='ffill', inplace = True)
    data['YYYY-MM-DDThh:mm:ss.sss'].fillna(method='ffill', inplace = True)
    data['Longitude_[degrees_east]'].fillna(method='ffill', inplace = True)
    data['Latitude_[degrees_north]'].fillna(method='ffill', inplace = True)
    data['LOCAL_CDI_ID'].fillna(method='ffill', inplace = True)
    data['EDMO_code'].fillna(method='ffill', inplace = True)
    data['Bot._Depth_[m]'].fillna(method='ffill', inplace = True)

    return data


def qc():
    st.title(':blue[Assign QC Flags to ODV] 📈')
    
    cols = st.columns(2)
    
    
    with cols[0]:
        st.write("You can load several ODVs, for each one You can assign a quality check")
        # check if the dataframe df in st.session_state and is not blank
        files = st.file_uploader("Upload ODV files", type=['txt'], accept_multiple_files=True)
        if 'dirname' in st.session_state and st.session_state['dirname'] is not None:
            dirname=st.session_state['dirname']
            st.write('Working...')
            st.write('Using directory: '+st.session_state['dirname'])
        #if the df does not exist in sesssion state then populate it       
        else:
            import uuid
            import time
            idrnd = uuid.uuid4()
            dirname=str(time.strftime("%Y%m%d%H%M%S")+'-'+str(idrnd))
            os.mkdir(dirname)
            st.session_state['dirname'] = dirname
    
    if files:
        with cols[1]:
            for uploaded_file in files:
                with open(os.path.join(dirname,uploaded_file.name),"wb") as f:
                    f.write(uploaded_file.getbuffer())
            counterDummy=1
            
            li=[]
            allhead=[]
            for u in os.listdir(dirname):
                data,head=fromfilecoords(u,dirname)
                li.append(data)
                allhead.append(head)
                counterDummy += 1
            if counterDummy >1:
                dfodv = pd.concat(li)
            st.subheader(':orange[Stations List] ✔')
            st.write(dfodv)
        
        with cols[0]:
            # FOLIUM click event map
            counter=0
            import folium
            from streamlit_folium import st_folium
            from folium import plugins
            from folium.plugins import Draw
            from folium.plugins import MiniMap
            from folium.plugins import MousePosition
            m = folium.Map(location=[20, 0],tiles="OpenTopoMap", zoom_start=2)
            minimap = plugins.MiniMap()
            m.add_child(minimap)
            for _, row in dfodv.iterrows():
                lat=str(row['Latitude_[degrees_north]'])
                lon=str(row['Longitude_[degrees_east]'])       
                folium.Marker(
                    [lat, lon],
                    popup=row['filename'],
                    tooltip=row['filename']
                ).add_to(m)             
            map_data = st_folium(m, height=500, width=500)
        
        with cols[1]:
            # FOLIUM result clicked map
            st.subheader(':orange[Selected station details] ✔')
            selected_station = None
            if map_data["last_object_clicked_popup"]:
                selected = map_data["last_object_clicked_popup"]
                selected_station = selected
                changestation=0
                if 'mystation' in st.session_state and st.session_state['mystation'] is not None and st.session_state['mystation']==selected_station:
                    mystation=st.session_state['mystation']
                else:
                    st.session_state['mystation']=selected_station
                    changestation=1
                counter=0
                m = folium.Map(location=[20, 0], zoom_start=2)
                for _, row in dfodv.iterrows():
                    if row['filename']==selected_station:
                        st.write('LOCAL_CDI_ID'+row['LOCAL_CDI_ID'])
                        st.write('Filename'+row['filename'])
                        outODVFileName=row['filename']
                        st.write("Lat: "+str(row['Latitude_[degrees_north]']))
                        st.write("Lon: "+str(row['Longitude_[degrees_east]']))
                        
                        if 'df' in st.session_state and st.session_state['df'] is not None and changestation==0:
                            df=st.session_state['df']               
                        else:
                           mydataodv,head=fromfile(row['filename'],dirname)
                           for tmpcol in mydataodv.columns:
                               cleanCol=function_cleaner(tmpcol)
                               mydataodv.rename(columns={tmpcol: cleanCol}, inplace=True)
                           st.session_state['df']=mydataodv
    
    if 'df' in st.session_state:  
        with cols[1]:
            seedata = st.toggle('See dataframe', key="2")
            df= st.session_state['df']   
            if "WebQCIndex" not in df.columns:
                df['WebQCIndex'] = range(1, len(df) + 1)
                st.write('To manage the QC, a column labelled WebQCIndex has been added to the dataframe')
            if seedata:
                st.write(df)    
            
            colsGrid = st.columns(2)
            param_column=['']
            param_column.extend(df.columns)
            qc_column=['']
            qc_column.extend(df.columns)
            with colsGrid[0]:
                selected_param_column = st.selectbox('Select param column to check:', param_column)
            with colsGrid[1]:
                selected_qc_column = st.selectbox('Select QC flag column:', qc_column)
        
        if selected_param_column != '' and selected_qc_column != '':
            myY=selected_param_column
            myZ=selected_qc_column
            point_selector = alt.selection_point("point_selection")
            interval_selector = alt.selection_interval("interval_selection")
            chartFilter = st.toggle('Use Chart with filters (WARNING: anomaly behaviour with great datasets)', key="5")
            
            if chartFilter:
                chart = (
                    alt.Chart(dataframe_explorer(df, case=False))
                    .mark_circle()
                    .encode(
                        x="WebQCIndex",
                        y=myY,
                        color=myZ+":N",
                        tooltip=["WebQCIndex", myY, myZ],
                        fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3))
                    )
                    .add_params(point_selector, interval_selector)
                    .properties(width=1100, height=900)
                )  
            else:
                chart = (
                    alt.Chart(df)
                    .mark_circle()
                    .encode(
                        x="WebQCIndex",
                        y=myY,
                        color=myZ+":N",
                        tooltip=["WebQCIndex", myY, myZ],
                        fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3))
                    )
                    .add_params(point_selector, interval_selector)
                    .properties(width=1100, height=900)
                )          
            event = st.altair_chart(chart, theme="streamlit", key="alt_chart", on_select="rerun")
            downloaddata = st.toggle('Download data CSV format', key="1")
            if downloaddata:
                import time
                import uuid
                idrnd = uuid.uuid4()
                savename=str(time.strftime("%Y%m%d%H%M%S")+'-'+str(idrnd))
                st.download_button(
                    label="Download Saved data data as CSV", data=df.to_csv(index=False), file_name="Saved_data"+savename+".csv",
                    mime="text/csv"
                )   
            downloaddataodv = st.toggle('Download data ODV format', key="3")
            if downloaddataodv:
                import time
                import uuid
                idrndodv = uuid.uuid4()
                outputodv=""
                for x in head:
                     outputodv+=str(x)
                
                preColumnsnew=fromfileprecols(u,dirname)
                df = df.drop('filename', axis=1)
                df = df.drop('WebQCIndex', axis=1)
                df = df.drop('Cruise', axis=1)
                df = df.drop('Station',axis=1) 
                df = df.drop('Type', axis=1)
                df = df.drop('YYYY-MM-DDThh_mm_ss_sss', axis=1)
                df = df.drop('Longitude__degrees_east_',axis=1) 
                df = df.drop('Latitude__degrees_north_',axis=1) 
                df = df.drop('LOCAL_CDI_ID', axis=1)
                df = df.drop('EDMO_code', axis=1)
                df = df.drop('Bot__Depth__m_', axis=1)
                frames = [preColumnsnew, df]
                dataOutOdv = pd.concat(frames, axis=1)
                tmpodv = dataOutOdv.to_csv(index=False, header=False, sep='\t')
                outputodv+=tmpodv
                st.download_button(label="Download Saved data data as ODV", data=outputodv, file_name=outODVFileName, key="4")
                
            if str(event)!='{\'selection\': {\'interval\': {}}}':
                with colsGrid[0]:
                    myFlags=[0,1,2,3,4,5,6,7,8,9]
                    selected_flag = st.selectbox('Select QC FLAG:', myFlags)
                with colsGrid[1]: 
                    st.write('')
                    st.write('')
                    if st.button("Assign QC FLAG"):                    
                        x = event.get("selection").get("interval_selection").get("WebQCIndex")
                        y = event.get("selection").get("interval_selection").get(myY)
                        if str(event)!='{\'selection\': {\'interval\': {}}}':
                            count=0
                            for u in x:
                                if count==0:
                                    bottomId = math.floor(u)
                                    count+=1
                                else:
                                    topId = math.ceil(u)   
                            count=0
                            for e in y:
                                if count==0:

                                    bottomParam = e
                                    count+=1
                                else:
                                    topParam = e 
                            
                            for i in range(bottomId, topId):
                                if df[myY][i] >= bottomParam and df[myY][i] <= topParam:
                                    df[myZ][i]=selected_flag
                            st.rerun()
        
    else:
        st.write('Please LOAD DATA')

def load_data():
    '''
    loads the selected file into a dataframe
    stores the selected file and dataframe in st.session_state
    '''
    st.title(':blue[Load CSV dataset] 📂')
    # check if the dataframe df in st.session_state and is not blank
    if 'df' in st.session_state and st.session_state['df'] is not None:
        df=load_data_2_dataframe(st.session_state['selected_file'])
        
    else:
        file = st.file_uploader("Upload a file", type=['csv'])
        separa = st.radio(
            "Specify the separator",
            ["COMMA", "TAB", "COLON", "SEMICOLON"])       
        if file is not None:     
            if separa == 'COMMA':
                separaval=','
            if separa == 'TAB':
                separaval='\t'
            if separa == 'COLON':
                separaval=':'
            if separa == 'SEMICOLON':
                separaval=';'
            st.session_state['selected_file'] = file
            df=load_data_2_dataframe(st.session_state['selected_file'],separaval)

def loadDataEditor():
    if 'dfodvmerge' in st.session_state:
        df= st.session_state['dfodvmerge']
        st.title(':blue[Data Editor] 📝')
        cols = st.columns(2)
        with cols[0]:
            selected_column = st.selectbox('Select column name to delete:', df.columns,index=None, placeholder="Select ...",)
            if st.button("Delete Column"):
                if selected_column is not None:
                    df.drop(columns=[selected_column], axis=1, inplace=True)
                
        with cols[1]:            
            title = st.text_input(
                "Insert column name to create a new one 👇",
                "",
                key="placeholder",
            )
            if st.button("Create Column"):
                if title != '':
                    df[title] = ''
 
        st.data_editor(dataframe_explorer(df, case=False), num_rows="dynamic")
    else:
        st.write('Please LOAD DATA')

            
if choice == "HOME - Clear Data":
    reset_data()
elif choice == "Edit Dataframe":
    loadDataEditor()
elif choice == "ODVs Quality Control":
    qc()
elif choice == "ODVs Merge and plot":
    reset_dataOdv()