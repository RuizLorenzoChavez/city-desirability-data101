# City Desirability Dashboard 

This is a data visualization project created with the Plotly Dash library. A deployed version of the web application can be accessed here as well.  

The City Desirability Dashboard displays data on available properties, jobs, and schools across seven selected cities in Metro Manila.
It acts as a tool for users interested in moving to Metro Manila to choose which city has the amenities that is most suitable to their needs. 


## Dependencies 
- plotly == 5.8.0
dash == 2.5.1
```
pip install dash
```


dash_bootstrap_components == 1.1.0
```
pip install dash-bootstrap-components
```


gunicorn == 20.1.0
```
pip install 
```

pandas == 1.4.2
```
pip install pandas
```

geopandas == 0.10.2

To download the geopandas library, kindly install the version of the following binaries that match your version of Python.
Download binaries from this site https://www.lfd.uci.edu/~gohlke/pythonlibs/
Make sure to install the binaries in the same order as shown below:

```
pip install .\GDAL-3.1.1-cp37-cp37m-win_amd64.whl
pip install .\pyproj-2.6.1.post1-cp37-cp37m-win_amd64.whl
pip install .\Fiona-1.8.13-cp37-cp37m-win_amd64.whl
pip install .\Shapely-1.7.0-cp37-cp37m-win_amd64.whl
pip install .\geopandas-0.8.0-py3-none-any
```

## Instructions
Running the web application locally
1. Clone or fork the repository to your machine.
2. Download the required packages—indicated above—in your virtual environment, preferably conda.
3. Using the terminal, change the directory to the current location of the repository.
4. Run the command: 'python app.py'
5. Open this link on your browser to view the web application deployed on your local host: http://127.0.0.1:8050/
6. Enjoy.

Running the web application through Github
1. On the repository's home page, go to the environment's section on the column on the right.
2. Click on the 'city-desirability-dash' environment.
3. Click on the 'view deployment' button.
4. Enjoy.
