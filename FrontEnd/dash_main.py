#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:18:43 2019

@author: sylvieshi
"""

import dash 
import dash_core_components as dcc
import dash_html_components as html 
import plotly.graph_objs as go 
import datetime
#from dateutil.relativedelta import relativedelta 

#start = datetime.datetime.today() - relativedelta(years=5)
#end = datetime.datetime.today()


app = dash.Dash()

app.layout = html.Div(
    html.Div(html.H1(children='RoboAdvisor')),
        
        )

if __name__ == '__main__':
    app.run_server(debug=True)
    