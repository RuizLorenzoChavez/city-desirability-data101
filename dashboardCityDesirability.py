from select import select
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

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
                                                               children=[html.Button(type='button',
                                                                                     className='btn btn-outline-dark',
                                                                                     children=['CITY COMPARISON']),
                                                                         html.Button(type='button',
                                                                                     className='btn btn-outline-dark', 
                                                                                     children=['PROPERTY COMPARISON']),
                                                                         html.Button(type='button',
                                                                                     className='btn btn-outline-dark',
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
                                            children=[html.Div(className='col-lg-9',
                                                               children=[html.H2(id='section-title',
                                                                                 children=['City Comparison\t\t\t\t\t',
                                                                                           html.Span(className='description',
                                                                                                     children=['to compare cities according to ammenities'])])]),
                                                      html.Hr()])])
                ])




#  runs server
if __name__ == '__main__':
    app.run_server(debug=True)