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

#  binning numerical values 
prop4sale['price_range'] = pd.cut(x=prop4sale.price, bins=5, right=False)
prop4rent['price_range'] = pd.cut(x=prop4rent.price, bins=5, right=False)
jobs['salary_range'] = pd.cut(x=jobs.salary, bins=6, right=False)

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
city_dist = schools.city.value_counts().reset_index()
city_dist = city_dist.rename(columns={'index': 'city', 'city': 'count'})

######################################################## PRE-CHART ########################################################
#  setting color map
city_colors = {'quezon': '#9369a8',
               'manila': '#cd4a77',
               'taguig': '#3078b4',
               'pasig': '#9fdbad',
               'makati': '#f3df4d',
               'mandaluyong': '#feae51',
               'san juan': '#ec8b83'}

#  creating a static bar chart
bar_chart = px.bar(city_dist, 
                   x=city_dist.city.str.capitalize(),
                   y='count',
                   width=1200,
                   height=600,
                   color='city',
                   color_discrete_map=city_colors,
                   template='plotly_white',
                   title='Total Number of Schools in Select Metro Manila Cities',
                   text='count',
                   hover_name=['Quezon City', 
                               'Manila City',
                               'Taguig City',
                               'Pasig City',
                               'Makati City',
                               'Mandaluyong City',
                               'San Juan City'],
                   hover_data={'city': False},
                   labels={'x': 'City',
                           'count': 'Count'})

#  hiding legends 
bar_chart.update_layout(showlegend=False)

#  updating title 
bar_chart.update_layout(title={'y':0.9,
                               'x':0.5,
                               'xanchor': 'center',
                               'yanchor': 'top',
                               'font': {'size': 25}})   

bar_chart.update_traces(textposition='outside')

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
                                                               className='btn-group col-lg-10',
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
                                                      html.Div(className='col-lg-2',
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
                html.Div(className='container-lg card-full-xl',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-6 radio-group my-2',
                                                                                  children=[html.Br(),
                                                                                            html.P(['Choose which amenity to explore'], className='description'),
                                                                                            dbc.RadioItems(id='radio-section1',
                                                                                                           className='btn-group radio',
                                                                                                           inputClassName='btn-check',
                                                                                                           labelClassName='btn btn-outline-dark',
                                                                                                           labelCheckedClassName='active',
                                                                                                           options=[{'label': 'property prices', 'value': 1},
                                                                                                                    {'label': 'rental prices', 'value': 2},
                                                                                                                    {'label': 'job salaries', 'value': 3}],
                                                                                                           value=1),
                                                                                            html.Br(),
                                                                                            html.Br(),
                                                                                            html.P('Description',
                                                                                                   className='p-title'),
                                                                                            html.P('''Shown here is the map of Metro Manila that displays the median in their respective data. 
                                                                                                   Once you have chosen your dataset, you will see here is the expected average per city, and their respective map. 
                                                                                                   You can also click on the map to see more information about your selected amenity.''',
                                                                                                   className='p-body'),
                                                                                            html.P('How to use:',
                                                                                                   className='p-title'),
                                                                                            html.P([html.Ol([html.Li('Choose and click what data you want to explore'),
                                                                                                             html.Li('Hover your mouse to the cities on the map to see the average'),
                                                                                                             html.Li('Click on the map to see more information about your selected amenity'),
                                                                                                             html.Li('Enjoy!')])],
                                                                                                   className='p-body')]),
                                                                         html.Div(className='col-lg-6',
                                                                                  children=[dcc.Graph(id='choropleth-map')])
                                                                         ])])
                                   ]),
                html.Br(),
                html.Div(className='container-lg', 
                         children=[html.Div(className='row justify-content-between',
                                            children=[html.Div(className='col-lg-5 card-half',
                                                               children=[html.Br(),
                                                                         html.Div(className='row', 
                                                                                  children=[dcc.Graph(id='variable-chart')])]),
                                                      html.Div(className='col-lg-5 card-half',
                                                               children=[html.Br(), 
                                                                         html.Div(className='col-lg-row',
                                                                                  children=[dcc.Graph(id='histogram')])])])
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
                                                      html.Div(className='col-lg-2',
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
                html.Div(className='container-lg card-full-xxl',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-8',
                                                                                  children=[dcc.Graph(id='scatter-map')])])])
                                   ]),
                html.Br(),
                html.Div(className='container-lg',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='col-lg-2', 
                                                               children=[html.P(className='description',
                                                                                 children=['Choose a property type'])]),
                                                      html.Div(className='col-lg-10',
                                                               children=[html.P(className='description',
                                                                                 children=['Slide to set your budget'])])]),
                                   html.Div(className='row',
                                            children=[html.Div(className='col-lg-2 radio-group',
                                                               children=[dbc.RadioItems(id='radio-section2',
                                                                                        className='btn-group',
                                                                                        inputClassName='btn-check',
                                                                                        labelClassName='btn btn-outline-dark',
                                                                                        labelCheckedClassName='active',
                                                                                        options=[{'label': 'for sale', 'value': 1},
                                                                                                 {'label': 'for rent', 'value': 2}],
                                                                                        value=1)]),
                                                      html.Div(className='col-lg-10',
                                                               children=[dcc.Slider(id='slider-scatter',
                                                                                    tooltip={"placement": "bottom", 
                                                                                             "always_visible": False},
                                                                                    min=prop4sale_geo.price.min(),
                                                                                    max=prop4sale_geo.price.max(),
                                                                                    value=prop4sale_geo.price.median())])]),
                                   html.Br(),
                                   html.Br(),
                                   html.Div(className='row justify-content-center', 
                                            children=[html.Div([html.P('Description', 
                                                                      className='p-title'), 
                                                               html.P('''Shown here are the property comparison according to their prices in their respective locations. 
                                                                      You can see the range of the property price based on their colors shown on the right side.
                                                                      ''',
                                                                      className='p-body')],
                                                               className='col-lg-6'),
                                                      html.Div([html.P('How to use:',
                                                                       className='p-title'),
                                                               html.P([html.Ol([html.Li('Select the property type that you want to explore'),
                                                                                html.Li('Set your budget using the slider above to isolate that budget and see it on the map'),
                                                                                html.Li('Enjoy!')])],
                                                                      className='p-body')],
                                                               className='col-lg-6')])
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
                                                      html.Div(className='col-lg-2',
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
                html.Div(className='container-lg',
                         children=[html.Div(className='row',
                                            children=[html.Div(className='row justify-content-center', 
                                                               children=[html.Div([html.P('Description', 
                                                                                          className='p-title'), 
                                                                                   html.P('''Presented below is graph that shows the total number of available schools per city of Manila. 
                                                                                          This section will provide you how many schools there are in Metro Manila including the number of types 
                                                                                          of school to fit your desired educational institution, which can be found below the initial graph''',
                                                                                          className='p-body')],
                                                                                  className='col-lg-6'),
                                                                         html.Div([html.P('How to use:',
                                                                                          className='p-title'),
                                                                                   html.P([html.Ol([html.Li('Click any of the vertical bar to view the availability of the school type'),
                                                                                                    html.Li('Hover over your desired type of school below the initial graph to know more details'),
                                                                                                    html.Li('Enjoy!')])],
                                                                                          className='p-body')],
                                                                                  className='col-lg-6')])])]),
                html.Br(),
                html.Div(className='container-lg card-full-l',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div(className='row',
                                                               children=[html.Div(className='col-lg-12',
                                                                                  children=[dcc.Graph(id='bar', 
                                                                                                      figure=bar_chart)])])])
                                   ]),
                html.Br(),
                html.Div(className='container-lg card-full',
                         children=[html.Div(className='container-lg',
                                            children=[html.Div([html.Div(className='col-lg-12',
                                                                         children=[dcc.Graph(id='treemap2')])],
                                                               className='row'),
                                                      html.Br(),
                                                      html.Div(html.Div(className='col-lg-12',
                                                                        children=[html.P('Description',
                                                                                         className='p-title'),
                                                                                  html.P('''The figure above shows the hierarchy of the type of schools available in your selected city. 
                                                                                         As presented, you may have a quick perception of which school type is largely available at your desired place. 
                                                                                         This may aid you in choosing the right school fitted to your preference. 
                                                                                         Don’t forget you can hover on the figure itself to see more details!''',
                                                                                         className='p-body'),
                                                                                  html.Br(),
                                                                                  html.Br(),
                                                                                  html.Br()]))])]),
                
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
                                               width=620,
                                               height=640,
                                               color_continuous_scale=px.colors.sequential.Reds,
                                               title='Median Property Prices in Select Metro Manila Cities')
              choro_map.update_layout(title={'y':0.9,
                                             'x':0.5,
                                             'xanchor': 'center',
                                             'yanchor': 'top',
                                             'font': {'size': 18}})  
       elif df_num == 2:
              choro_map = px.choropleth_mapbox(ave_prop4rent_city, 
                                               geojson=ave_prop4rent_city.geometry,
                                               locations=ave_prop4rent_city.index, 
                                               color='price', 
                                               center={'lat': 14.60886, 'lon': 121.037402},
                                               mapbox_style='light',
                                               zoom=10,
                                               width=620,
                                               height=640,
                                               color_continuous_scale=px.colors.sequential.Blues,
                                               title='Median Rental Prices in Select Metro Manila Cities')
              choro_map.update_layout(title={'y':0.9,
                                             'x':0.5,
                                             'xanchor': 'center',
                                             'yanchor': 'top',
                                             'font': {'size': 18}})  
       else:
              choro_map = px.choropleth_mapbox(ave_jobs_city, 
                                               geojson=ave_jobs_city.geometry,
                                               locations=ave_jobs_city.index, 
                                               color='salary', 
                                               center={'lat': 14.60886, 'lon': 121.037402},
                                               mapbox_style='light',
                                               zoom=10,
                                               width=620,
                                               height=640,
                                               color_continuous_scale=px.colors.sequential.Greens,
                                               title='Median Job Salaries in Select Metro Manila Cities')
              choro_map.update_layout(title={'y':0.9,
                                             'x':0.5,
                                             'xanchor': 'center',
                                             'yanchor': 'top',
                                             'font': {'size': 18}})  
       return choro_map

room_colors = {'1.0': px.colors.qualitative.Plotly[0],
               '2.0': px.colors.qualitative.Plotly[1],
               '3.0': px.colors.qualitative.Plotly[2]}

#  for variable chart 
@app.callback(
       Output('variable-chart', 'figure'),
       Input('radio-section1', 'value'),
       Input('choropleth-map', 'clickData')
)
def update_varbar(df_num, city):
       if df_num == 1: #  scatter of floor_area and property price 
              try: 
                     select_city = city['points'][0]["location"]
                     df = prop4sale.query(f'city == "{select_city}"')
                     scatter = px.scatter(df,
                                          x='floor_area',
                                          y='price',
                                          color=df['bedroom_num'].astype(str),
                                          height=420,
                                          template='plotly_white',
                                          color_discrete_map=room_colors,
                                          labels={'floor_area': 'floor area'},
                                          title=f'Property Price vs Floor Area in {select_city.capitalize()} City',
                                          hover_name='listing')
                     scatter.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})
                     scatter.update_layout(legend_title_text='# of Bedrooms')  
                     return scatter                   
              except TypeError:
                     df = prop4sale
                     scatter = px.scatter(df,
                                          x='floor_area',
                                          y='price',
                                          color=df['bedroom_num'].astype(str),
                                          height=420,
                                          template='plotly_white',
                                          color_discrete_map=room_colors,
                                          labels={'floor_area': 'floor area'},
                                          title='Property Price vs Floor Area in Select Metro Manila',
                                          hover_name='listing')
                     scatter.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     scatter.update_layout(legend_title_text='# of Bedrooms') 
                     return scatter
       
       elif df_num == 2: #  scatter of floor_area and property price 
              try: 
                     select_city = city['points'][0]["location"]
                     df = prop4rent.query(f'city == "{select_city}"')
                     scatter = px.scatter(df,
                                          x='floor_area',
                                          y='price',
                                          color=df['bedroom_num'].astype(str),
                                          height=420,
                                          template='plotly_white',
                                          color_discrete_map=room_colors,
                                          labels={'floor_area': 'floor area'},
                                          title=f'Rental Price vs Floor Area in {select_city.capitalize()} City',
                                          hover_name='listing')
                     scatter.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     scatter.update_layout(legend_title_text='# of Bedrooms') 
                     return scatter                   
              except TypeError:
                     df = prop4rent
                     scatter = px.scatter(df,
                                          x='floor_area',
                                          y='price',
                                          color=df['bedroom_num'].astype(str),
                                          height=420,
                                          template='plotly_white',
                                          color_discrete_map=room_colors,
                                          labels={'floor_area': 'floor area'},
                                          title='Rental Price vs Floor Area in Select Metro Manila',
                                          hover_name='listing')
                     scatter.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     scatter.update_layout(legend_title_text='# of Bedrooms') 
                     return scatter
       
       else:  #  bar chart of 
              try: 
                     select_city = city['points'][0]["location"]
                     df = jobs.query(f'city == "{select_city}"').company.value_counts().head(10).sort_values(ascending=True)
                     barh = px.bar(df, 
                                   x=df.values,
                                   y=df.index,
                                   labels={'index': 'company',
                                           'x': 'count'},
                                   template='plotly_white',
                                   height=420,
                                   text=df.values,
                                   color_discrete_sequence=[city_colors[city['points'][0]["location"]]],
                                   title=f'Top Ten Companies with Most Job Openings in {select_city.capitalize()} City')
                     barh.update_traces(textposition='outside')
                     barh.update_layout(title={'y':0.9,
                               'x':0.5,
                               'xanchor': 'center',
                               'yanchor': 'top',
                               'font': {'size': 18}})  
                     
                     return barh
              except TypeError:
                     df = jobs.company.value_counts().head(10).sort_values(ascending=True)
                     barh = px.bar(df,
                                   x=df.values,
                                   y=df.index,
                                   labels={'index': 'company',
                                           'x': 'count'},
                                   template='plotly_white',
                                   height=420,
                                   text=df.values,
                                   color_discrete_sequence=['#357a38'],
                                   title='Top Ten Companies with Most Job Openings')
                     barh.update_traces(textposition='outside')
                     barh.update_layout(title={'y':0.9,
                               'x':0.5,
                               'xanchor': 'center',
                               'yanchor': 'top',
                               'font': {'size': 18}})  
                     
                     return barh

average_colors = {'mean': px.colors.qualitative.Light24[0],
                  'median': px.colors.qualitative.Light24[1]}


                          
#  for histogram
@app.callback(
       Output('histogram', 'figure'),
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
                                         title = f'Distribution of Property Prices in {select_city.capitalize()} City', 
                                         height=420,
                                         color_discrete_sequence=[city_colors[city['points'][0]["location"]]],
                                         template='plotly_white')
                     hist.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     hist.add_vline(type="line", 
                                    line_color=average_colors['mean'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dashdot",
                                    x=df.price.mean(),
                                    annotation_text='Mean')
                     hist.add_vline(type="line", 
                                    line_color=average_colors['median'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dot",
                                    x=df.price.median(),
                                    annotation_text='Median',
                                    annotation_position='top left'
                                    )
                     return hist
              except TypeError:
                     df = prop4sale
                     hist = px.histogram(df, x='price', 
                                         height=420, 
                                         color_discrete_sequence=['#b30000'],
                                         title = 'Distribution of Property Prices in Select Cities',
                                         template='plotly_white')
                     hist.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     hist.add_vline(type="line", 
                                    line_color=average_colors['mean'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dashdot",
                                    x=df.price.mean(),
                                    annotation_text='Mean')
                     hist.add_vline(type="line", 
                                    line_color=average_colors['median'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dot",
                                    x=df.price.median(),
                                    annotation_text='Median',
                                    annotation_position='top left'
                                    )
                     return hist
       elif df_num == 2:
              try:
                     select_city = city['points'][0]["location"]
                     df = prop4rent.query(f'city == "{select_city}"')
                     hist = px.histogram(df, 
                                         x='price', 
                                         title = f'Distribution of Rental Prices in {select_city.capitalize()} City',
                                         height=420,
                                         color_discrete_sequence= [city_colors[city['points'][0]["location"]]],
                                         template='plotly_white')
                     hist.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     hist.add_vline(type="line", 
                                    line_color=average_colors['mean'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dashdot",
                                    x=df.price.mean(),
                                    annotation_text='Mean')
                     hist.add_vline(type="line", 
                                    line_color=average_colors['median'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dot",
                                    x=df.price.median(),
                                    annotation_text='Median',
                                    annotation_position='top left'
                                    )
                     return hist
              except TypeError:
                     df = prop4rent
                     hist = px.histogram(df, 
                                         x='price', 
                                         height=420,
                                         color_discrete_sequence=['#004999'],
                                         title = 'Distribution of Rental Prices in Select Cities',
                                         template='plotly_white')
                     hist.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     hist.add_vline(type="line", 
                                    line_color=average_colors['mean'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dashdot",
                                    x=df.price.mean(),
                                    annotation_text='Mean')
                     hist.add_vline(type="line", 
                                    line_color=average_colors['median'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dot",
                                    x=df.price.median(),
                                    annotation_text='Median',
                                    annotation_position='top left'
                                    )
                     return hist
       else:
              try:
                     select_city = city['points'][0]["location"]
                     df = jobs.query(f'city == "{select_city}"')
                     hist = px.histogram(df, 
                                         x='salary', 
                                         title = f'Distribution of Salaries Offered in {select_city.capitalize()} City',
                                         height=420,
                                         color_discrete_sequence= [city_colors[city['points'][0]["location"]]],
                                         template='plotly_white')
                     hist.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}})  
                     hist.add_vline(type="line", 
                                    line_color=average_colors['mean'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dashdot",
                                    x=df.salary.mean(),
                                    annotation_text='Mean')
                     hist.add_vline(type="line", 
                                    line_color=average_colors['median'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dot",
                                    x=df.salary.median(),
                                    annotation_text='Median',
                                    annotation_position='top left')
                     return hist 
              except TypeError:
                     df = jobs
                     hist = px.histogram(df, 
                                         x='salary', 
                                         height=420,
                                         color_discrete_sequence=['#357a38'],
                                         title = 'Distribution of Salaries in Select Cities',
                                         template='plotly_white')
                     hist.update_layout(title={'y':0.9,
                                               'x':0.5,
                                               'xanchor': 'center',
                                               'yanchor': 'top',
                                               'font': {'size': 18}}) 
                     hist.add_vline(type="line", 
                                    line_color=average_colors['mean'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dashdot",
                                    x=df.salary.mean(),
                                    annotation_text='Mean')
                     hist.add_vline(type="line", 
                                    line_color=average_colors['median'], 
                                    line_width=3, 
                                    opacity=1, 
                                    line_dash="dot",
                                    x=df.salary.median(),
                                    annotation_text='Median',
                                    annotation_position='top left')
                     return hist

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
              
       if df_num == 2:
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
                                              color='price', 
                                              width=1170, 
                                              height=780,  
                                              center={'lat': 14.59665, 'lon': 121.0369}, 
                                              zoom=11.5, 
                                              opacity=.5,
                                              color_continuous_scale=px.colors.sequential.OrRd)
              scatter_map.update_layout(transition=dict(duration=1400,
                                                    easing="circle-in"))
              return scatter_map 
       else:
              df = prop4rent.query(f"price <= {budget}")
              scatter_map = px.scatter_mapbox(df, 
                                              lat="latitude", 
                                              lon="longitude",
                                              hover_name="listing", 
                                              color='price', 
                                              width=1170,
                                              height=780,   
                                              center={'lat': 14.5663, 'lon': 121.0372}, 
                                              zoom=12, 
                                              opacity=.5,
                                              color_continuous_scale=px.colors.sequential.algae)
              scatter_map.update_layout(transition=dict(duration=1400,
                                                    easing="circle-in"))
              
              return scatter_map

curr_colors = {'Purely ES': '#9d915a',
               'All Offering (K to 12)': '#b35f44',
               'ES and JHS (K to 10)': '#96999b',
               'Purely SHS': '#f0e3ce',
               'JHS with SHS': '#7f3838',
               'Purely JHS': '#00a779'}

#  for treemap
@app.callback(
       Output('treemap2', 'figure'),
       Input('bar', 'clickData')
)
def update_treemap2(location):
       try:
              select_city = location['points'][0]["x"]
              df = schools.query(f'city == "{select_city.lower()}"')
              treemap = px.treemap(df, 
                                   path=['sector','curricular_class', 'school_name'], 
                                   width=1200,
                                   height=1000, 
                                   color='curricular_class',
                                   title=f'Schools in {select_city} City Grouped According to its Sector and Curricular Offering',
                                   color_discrete_map=curr_colors)
              treemap.update_layout(transition=dict(duration=750,
                                                    easing="quad"))
              treemap.update_layout(title={'y':0.955,
                                            'x':0.5,
                                            'xanchor': 'center',
                                            'yanchor': 'top',
                                            'font': {'size': 25}})
              treemap.update_traces(root_color="#98b2d1")
              return treemap
       except TypeError:
              df = schools
              treemap = px.treemap(df, 
                                   path=['sector','curricular_class', 'school_name'], 
                                   width=1200,
                                   height=1000, 
                                   color='curricular_class',
                                   title='Schools in Metro Manila Grouped According to its Sector and Curricular Offering',
                                   color_discrete_map=curr_colors)
              treemap.update_layout(transition=dict(duration=750,
                                                    easing="quad"))
              treemap.update_layout(title={'y':0.955,
                                            'x':0.5,
                                            'xanchor': 'center',
                                            'yanchor': 'top',
                                            'font': {'size': 26}})  
              treemap.update_traces(root_color="#98b2d1") 
              return treemap
              
              
#  runs server
if __name__ == '__main__':
       app.run_server(debug=True)
       
