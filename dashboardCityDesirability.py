from select import select
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np
import pandas as pd
import geopandas as gpd
import pyproj
from traitlets import Type

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
ave_prop4rent_city = ave_prop4rent_city.set_index('city') 

#  median salary for jobs in NCR
ave_jobs_city = jobs.groupby(by='city')['salary'].median().reset_index()
ave_jobs_city = ncr_geodata.merge(ave_jobs_city, on='city', how='inner')
ave_jobs_city = ave_jobs_city.set_index('city') 

#  property prices with respective coordinates
#  data is filtered to remove outliers in the latitude column
prop4sale_geo = prop4sale[~((prop4sale.latitude.gt(15)) | prop4sale.latitude.lt(14))]

#  aggregating data for bar chart—frequency count for schools in each city
#  creating a static bar chart as well
city_dist = schools.city.value_counts().reset_index()
city_dist = city_dist.rename(columns={'index': 'city', 'city': 'count'})

bar_chart = px.bar(city_dist, 
                   x='city',
                   y='count',
                   width=800,
                   height=500)

######################################################## LAYOUT ########################################################

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
                                                                           children=['City Desirability Dashboard'])])])
                             ]), 
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
                                            className='row img-fluid mx-auto d-block')
                                   ]),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Div(id='first-section',
                         className='container-lg section-header',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='col-lg-10',
                                                               children=[html.H2(className='section-title',
                                                                                 children=['City Comparison\t\t\t\t\t',
                                                                                           html.Span(className='description',
                                                                                                     children=['to compare cities according to ammenities'])])]),
                                                      html.Div(className='col-lg-1',
                                                               children=[html.Div(id='nav1',
                                                                                className='btn-group col-lg-12',
                                                                                role='group',
                                                                                children=[html.A(className='btn btn-outline-dark',
                                                                                                 href='#navbar',
                                                                                                 children=['↑']),
                                                                                          html.A(className='btn btn-outline-dark',
                                                                                                 href='#navbar',
                                                                                                 children=['home']),
                                                                                          html.A(className='btn btn-outline-dark',
                                                                                                 href='#second-section',
                                                                                                 children=['↓'])])]),
                                                      html.Hr()])
                                   ]),
                html.Div(className='container-lg card-full-l',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-6 radio-group my-2',
                                                                                  children=[html.Br(),
                                                                                            dbc.RadioItems(id='radio-section1',
                                                                                                           className='btn-group radio',
                                                                                                           inputClassName='btn-check',
                                                                                                           labelClassName='btn btn-outline-dark',
                                                                                                           labelCheckedClassName='active',
                                                                                                           options=[{'label': 'for sale', 'value': 1},
                                                                                                                    {'label': 'for rent', 'value': 2},
                                                                                                                    {'label': 'salaries', 'value': 3}],
                                                                                                           value=1)]),
                                                                         html.Div(className='col-lg-6',
                                                                                  children=[dcc.Graph(id='choropleth-map')])
                                                                         ])])
                                   ]),
                html.Br(),
                html.Div(className='container-lg', 
                         children=[html.Div(className='row justify-content-between',
                                            children=[html.Div(className='col-lg-5 card-half',
                                                               children=[html.Div(className='row', 
                                                                                  children=[html.H4(className='text-center my-3',
                                                                                                    id='bar-title')]),
                                                                         dcc.Graph(id='horizontal-bar')]),
                                                      html.Div(className='col-lg-5 card-half',
                                                               children=[html.Div(className='row',
                                                                                  children=[html.H4(className='text-center my-3',
                                                                                                    id='distribution-title')]),
                                                                         dcc.Graph(id='histogram')])])
                                   ]),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Div(id='second-section',
                         className='container-lg section-header',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='col-lg-10',
                                                               children=[html.H2(className='section-title',
                                                                                 children=['Property Comparison\t\t\t\t\t',
                                                                                           html.Span(className='description',
                                                                                                     children=['to compare properties according to their prices in their respective locations'])])]),
                                                      html.Div(className='col-lg-1',
                                                               children=[html.Div(id='nav2',
                                                                                className='btn-group col-lg-12',
                                                                                role='group',
                                                                                children=[html.A(className='btn btn-outline-dark',
                                                                                                 href='#first-section',
                                                                                                 children=['↑']),
                                                                                          html.A(className='btn btn-outline-dark',
                                                                                                 href='#navbar',
                                                                                                 children=['home']),
                                                                                          html.A(className='btn btn-outline-dark',
                                                                                                 href='#third-section',
                                                                                                 children=['↓'])])]),
                                                      html.Hr()])
                                   ]),
                html.Br(),
                html.Div(className='container-lg card-full-xl',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-8',
                                                                                  children=[dcc.Graph(id='scatter-map')])])])
                                   ]),
                html.Br(),
                html.Div(className='container-lg',
                         children=[html.Div(className='row justify-content-center', 
                                            children=[html.Div(className='col-lg-12', 
                                                               children=[html.H5(className='text-center my-3',
                                                                                 children=['Choose a property type'])]),
                                                      html.Div(className='col-lg-3 radio-group text-center',
                                                               children=[dbc.RadioItems(id='radio-section2',
                                                                                        className='btn-group',
                                                                                        inputClassName='btn-check',
                                                                                        labelClassName='btn btn-outline-dark',
                                                                                        labelCheckedClassName='active',
                                                                                        options=[{'label': 'for sale', 'value': 1},
                                                                                                 {'label': 'for rent', 'value': 2}]
                                                                                        ,value=1)]), 
                                                      html.Br(),
                                                      html.Br(),
                                                      html.H5(className='text-center my-4',
                                                              children=['Slide to set your budget']),
                                                      html.Br(),
                                                      dcc.Slider(marks=None,
                                                                 id='slider-scatter',
                                                                 tooltip={"placement": "bottom", "always_visible": False}
                                                                 ),
                                                      html.Br(),
                                                      html.Br(),
                                                      html.Br()])
                                   ]),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Div(id='third-section',
                         className='container-lg section-header',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='col-lg-10',
                                                               children=[html.H2(className='section-title',
                                                                                 children=['School Comparison\t\t\t\t\t',
                                                                                           html.Span(className='description',
                                                                                                     children=['to compare the number of schools in each city'])])]),
                                                      html.Div(className='col-lg-1',
                                                               children=[html.Div(id='nav3',
                                                                                className='btn-group col-lg-12',
                                                                                role='group',
                                                                                children=[html.A(className='btn btn-outline-dark',
                                                                                                 href='#second-section',
                                                                                                 children=['↑']),
                                                                                          html.A(className='btn btn-outline-dark',
                                                                                                 href='#navbar',
                                                                                                 children=['home']),
                                                                                          html.A(className='btn btn-outline-dark',
                                                                                                 href='#third-section',
                                                                                                 children=['↓'])])]),
                                                      html.Hr()])
                                   ]), 
                html.Br(),
                html.Div(className='container-lg card-full',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-7',
                                                                                  children=[dcc.Graph(id='bar', figure=bar_chart)])])])
                                   ]),
                html.Br(),
                html.Div(className='container-lg card-full',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-7',
                                                                                  children=[dcc.Graph(id='treemap')])])])
                                   ]),
                html.Br(),
                html.Br()
                ])


########################################################CHARTING PLOTS########################################################
#  setting mapbox access token
px.set_mapbox_access_token('pk.eyJ1IjoicnVpemxvcmVuem9jaGF2ZXoiLCJhIjoiY2wzZHp5MTNlMDM4aDNmbzN5bjhva29ueiJ9.sKJbYBhB5MwOdBqvplljWw')

#  for choropleth map 
@app.callback( 
       Output('choropleth-map', 'figure'),
       Input('radio-section1', 'value')
)
def update_choropleth(df_num):
       if df_num == 1:
              choro_map = px.choropleth_mapbox(ave_prop4sale_city, 
                                               geojson=ave_prop4sale_city.geometry,
                                               locations=ave_prop4sale_city.index, 
                                               color='price', 
                                               center={'lat': 14.60886, 'lon': 121.037402},
                                               mapbox_style='light',
                                               zoom=10,
                                               width=600,
                                               height=600,
                                               color_continuous_scale= px.colors.sequential.Reds)
       elif df_num == 2:
              choro_map = px.choropleth_mapbox(ave_prop4rent_city, 
                                               geojson=ave_prop4rent_city.geometry,
                                               locations=ave_prop4rent_city.index, 
                                               color='price', 
                                               center={'lat': 14.60886, 'lon': 121.037402},
                                               mapbox_style='light',
                                               zoom=10,
                                               width=600,
                                               height=600,
                                               color_continuous_scale= px.colors.sequential.Blues)
       else:
              choro_map = px.choropleth_mapbox(ave_jobs_city, 
                                               geojson=ave_jobs_city.geometry,
                                               locations=ave_jobs_city.index, 
                                               color='salary', 
                                               center={'lat': 14.60886, 'lon': 121.037402},
                                               mapbox_style='light',
                                               zoom=10,
                                               width=600,
                                               height=600,
                                               color_continuous_scale= px.colors.sequential.Greens)
       return choro_map

#  for horizontal bar & title 

#  for histogram
@app.callback(
       Output('histogram', 'figure'),
       Output('distribution-title', 'children'),
       Input('radio-section1', 'value'),
       Input('choropleth-map', 'clickData')
)
def update_histogram(df_num, city):
       if df_num == 1:
              try:
                     select_city = city['points'][0]["location"]
                     df = prop4sale.query(f'city == "{select_city}"')
                     hist = px.histogram(df, 
                                         x='price', 
                                         height=383,
                                         color_discrete_sequence= ['red'])
                     hist_title = f'Distribution of Property Prices in {select_city.capitalize()} City'
                     return hist, hist_title 
              except TypeError:
                     df = prop4sale
                     hist = px.histogram(df, x='price', 
                                         height=383, 
                                         color_discrete_sequence= 
                                         ['red'])
                     hist_title = 'Distribution of Property Prices in Selected Cities'
                     return hist, hist_title
       elif df_num == 2:
              try:
                     select_city = city['points'][0]["location"]
                     df = prop4rent.query(f'city == "{select_city}"')
                     hist = px.histogram(df, 
                                         x='price', 
                                         height=383,
                                         color_discrete_sequence= ['blue'])
                     hist_title = f'Distribution of Property Prices in {select_city.capitalize()} City'
                     return hist, hist_title 
              except TypeError:
                     df = prop4rent
                     hist = px.histogram(df, 
                                         x='price', 
                                         height=383,
                                         color_discrete_sequence= ['blue'])
                     hist_title = 'Distribution of Property Prices (Rent)'
                     return hist, hist_title 
       else:
              try:
                     select_city = city['points'][0]["location"]
                     df = jobs.query(f'city == "{select_city}"')
                     hist = px.histogram(df, 
                                         x='salary', 
                                         height=383,
                                         color_discrete_sequence= ['green'])
                     hist_title = f'Distribution of Salaries Offered in {select_city.capitalize()} City'
                     return hist, hist_title 
              except TypeError:
                     df = jobs
                     hist = px.histogram(df, 
                                         x='salary', 
                                         height=383,
                                         color_discrete_sequence= ['green'])
                     hist_title = 'Distribution of Salaries'
                     return hist, hist_title 

#  for slider
@app.callback(
       Output('slider-scatter', 'min'),
       Output('slider-scatter', 'max'),
       Output('slider-scatter', 'value'),
       Input('radio-section2', 'value'),
)
def update_slider(df_num):       
       if df_num == 1:
              df = prop4sale_geo
              mini = df.price.min()
              maxi = df.price.max()
              value = df.price.median()
              return mini, maxi, value
       else:
              df = prop4rent
              mini = df.price.min()
              maxi = df.price.max()
              value = df.price.median()
              return mini, maxi, value
       
#  for scatter map 
@app.callback(
       Output('scatter-map', 'figure'),
       Input('radio-section2', 'value'),
       Input('slider-scatter', 'value')
)
def update_scatter(df_num, budget):
       if df_num == 1:
              df = prop4sale_geo.query(f"price <= {budget}")
              scatter_map = px.scatter_mapbox(df, 
                                              lat="latitude", 
                                              lon="longitude",
                                              hover_name="listing", 
                                              width=1170, 
                                              height=780,  
                                              center={'lat': 14.59665, 'lon': 121.0369}, 
                                              zoom=11.5, 
                                              opacity=.5)
              
              return scatter_map 
       else:
              df = prop4rent.query(f"price <= {budget}")
              scatter_map = px.scatter_mapbox(df, 
                                              lat="latitude", 
                                              lon="longitude",
                                              hover_name="listing",  
                                              width=1170,
                                              height=780,   
                                              center={'lat': 14.5663, 'lon': 121.0372}, 
                                              zoom=11.5, 
                                              opacity=.5)
              return scatter_map

#  for treemap
@app.callback(
       Output('treemap', 'figure'),
       Input('bar', 'clickData')
)
def update_treemap(location):
       try:
              select_city = location['points'][0]["x"]
              df = schools.query(f'city == "{select_city}"')
              treemap = px.treemap(df, 
                                   path=['sector','curricular_class', 'school_subclass', 'school_name'], 
                                   width=800,
                                   height=500, 
                                   color='curricular_class')
              return treemap
       except TypeError:
              df = schools
              treemap = px.treemap(df, 
                                   path=['sector','curricular_class', 'school_subclass', 'school_name'], 
                                   width=800,
                                   height=500, 
                                   color='curricular_class')
              return treemap

#  runs server
if __name__ == '__main__':
       app.run_server(debug=True)