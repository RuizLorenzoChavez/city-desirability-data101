from select import select
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import geopandas as gpd
import pyproj

########################################################DATA PROCESSING########################################################
#  loading the data from the cleaned datasets
prop4sale = pd.read_csv('data/clean/clean_ncr_prop4sale.csv',index_col=0)
prop4rent = pd.read_csv('data/clean/clean_ncr_prop4rent.csv',index_col=0)
jobs = pd.read_csv('data/clean/clean_ncr_jobs.csv',index_col=0)
schools = pd.read_csv('data/clean/clean_ncr_school.csv',index_col=0)
ph_geodata = gpd.read_file('data/ph-adm/PHL_adm2.shp')


#  filtering geodata to consider only those in NCR
ph_geodata.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
ncr_geodata = ph_geodata.query("NAME_1 == 'Metropolitan Manila'")
ncr_geodata = ncr_geodata.rename(columns={'NAME_2': 'city'})
ncr_geodata['city'] = ncr_geodata['city'].str.replace('City of', '')
ncr_geodata['city'] = ncr_geodata['city'].str.replace('City', '')
ncr_geodata['city'] = ncr_geodata['city'].str.lower()
ncr_geodata['city'] = ncr_geodata['city'].str.strip()
ncr_geodata = ncr_geodata.drop(columns=['NAME_1'])
ncr_geodata = ncr_geodata[['city', 'geometry']] 
ncr_geodata = ncr_geodata.reset_index(drop=True)


#  filtered and aggregated data for choropleth map 
#  median price of property for sale in NCR
ave_prop4sale_city = prop4sale.groupby(by='city')['price'].median().reset_index()
ave_prop4sale_city = ncr_geodata.merge(ave_prop4sale_city, on='city', how='inner')
ave_prop4sale_city = ave_prop4sale_city.set_index('city')

#  median price of property for rent in NCR
ave_prop4rent_city = prop4rent.groupby(by='city')['price'].median().reset_index()
ave_prop4rent_city = ncr_geodata.merge(ave_prop4rent_city, on='city', how='inner') 


#  median salary for jobs in NCR
ave_jobs_city = jobs.groupby(by='city')['salary'].median().reset_index()
ave_jobs_city = ncr_geodata.merge(ave_jobs_city, on='city', how='inner')



########################################################CHARTING PLOTS########################################################
#  setting mapbox access token
px.set_mapbox_access_token('pk.eyJ1IjoicnVpemxvcmVuem9jaGF2ZXoiLCJhIjoiY2wzZHp5MTNlMDM4aDNmbzN5bjhva29ueiJ9.sKJbYBhB5MwOdBqvplljWw')
sample_map = px.choropleth_mapbox(ave_prop4sale_city, 
                                  geojson=ave_prop4sale_city.geometry,
                                  locations=ave_prop4sale_city.index, 
                                  color='price', 
                                  center={'lat': 14.594364, 'lon': 121.038177},
                                  mapbox_style='light',
                                  zoom=11,
                                  width=600,
                                  height=1000)


########################################################DASHBOARDING########################################################

#  external_stylesheets to be used for creating the HTML layout
external_stylesheets = [
    #  for Bootstrap CDN
    {'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css',
     'rel': 'stylesheet',
     'integrity': 'sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor:',
     'crossorigin': 'anonymous'
    },
    #  Bree font import 
    {'href': 'https://fonts.googleapis.com/css2?family=Bree+Serif&family=Mulish&display=swap',
     'rel': 'stylesheet'
     },
    #  Mulish font import
    {'href': 'https://fonts.googleapis.com/css2?family=Mulish:wght@300&display=swap',
     'rel': 'stylesheet'
     }
]

#  initialize dashboard
app = Dash(__name__, external_stylesheets=external_stylesheets, title='City Desirability Dashboard')


#  dashboard layout
app.layout = html.Div(children=[html.Header(id='navbar', 
                         className='container-fluid', 
                         children=[
                             html.Div(className='row', 
                                      children=[html.Div(className='col-lg-12',
                                                         children=[html.H1(id='title-text',
                                                                           className='text-center my-3',
                                                                           children=['City Desirability Dashboard'])])])]), 
                html.Br(),
                html.Br(),
                html.Div(id='landing',
                         className='container-lg',
                         children=[html.Img(src='assets/banner.png',
                                            className='row img-fluid',
                                            alt='banner'),
                                   html.Br(), 
                                   html.Br(),
                                   html.Br(),
                                   html.Div(className='row',
                                            children=[html.Div(className='col-lg-12',children=[html.H3(id='button-text',
                                                                                                       className='text-center my-3',
                                                                                                       children='Start exploring now.')])]),
                                   html.Div(className='row justify-content-center',
                                            children=[html.Div(id='navbuttons',
                                                               className='btn-group col-lg-12',
                                                               role='group',
                                                               children=[html.A(className='btn btn-outline-dark',
                                                                                href='#first-section',
                                                                                children=['CITY COMPARISON']),
                                                                         html.A(className='btn btn-outline-dark',
                                                                                href='#second-section', 
                                                                                children=['PROPERTY COMPARISON']),
                                                                         html.A(className='btn btn-outline-dark',
                                                                                href='#third-section',
                                                                                children=['SCHOOL COMPARISON'])])]),
                                   html.Br(),
                                   html.Br(),
                                   html.Br(),
                                   html.Img(id='nav-arrow',
                                            src='assets/arrow-down-sign-to-navigate.png',
                                            className='row img-fluid mx-auto d-block')]),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Div(id='first-section',
                         className='container-lg section-header',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='col-lg-11',
                                                               children=[html.H2(id='section-title',
                                                                                 children=['City Comparison\t\t\t\t\t',
                                                                                           html.Span(className='description',
                                                                                                     children=['to compare cities according to ammenities'])])]),
                                                      html.Div(className='col-lg-1',
                                                               children=[html.A(href='#navbar',
                                                                                className='btn btn-outline-dark',
                                                                                children=['Home'])]),
                                                      html.Hr()])]),
                html.Div(className='container-lg',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='col-lg-10',
                                                               children=[dcc.Graph(id='choropleth-map', figure=sample_map)])])])
                ])




#  runs server
if __name__ == '__main__':
    app.run_server(debug=True)