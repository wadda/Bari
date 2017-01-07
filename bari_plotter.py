# coding=utf-8

from datetime import datetime
from time import sleep

import plotly.graph_objs as go
import plotly.plotly as py

import ms5637

__author__ = 'Moe'
__copyright__ = 'Copyright 2017  Moe'
__license__ = 'MIT'
__version__ = '0.0.2'

# Bari sensor of MS5637
sensor = ms5637.Chip()

YUPPER = 40
YLOWER = -40
ZERO_SAMPLE = 100
SETSIZE_MINI = 1000
SETSIZE_MAXI = 10000

OVERWRITE = True  # overwrites datafile
# OVERWRITE = False  # extends datafile

credentials = py.get_credentials()
username = credentials['username']
api_key = credentials['api_key']
stream_token = credentials['stream_ids']

py.sign_in(username, api_key)

stream_level_maxi = {'token': stream_token[0], 'maxpoints': SETSIZE_MAXI}
stream_level_mini = {'token': stream_token[1], 'maxpoints': SETSIZE_MINI}

trace_maxi = {
    'stream': stream_level_maxi,
    "x": [],
    "y": [],
    "hoverinfo": "y+x",
    "mode": "lines",
    "name": "About 100X that ",
    "type": "scatter",
    "xaxis": "x",
    "yaxis": "y",
    "line": {"shape": "spline", "width": 1}
}
trace_mini = {
    'stream': stream_level_mini,
    "x": [],
    "y": [],
    "hoverinfo": "y",
    "mode": "lines",
    "name": "Last 2 Minutes, or so",
    "type": "scatter",
    "xaxis": "x2",
    "yaxis": "y2",
    "line": {"shape": "spline", "width": 2}
}

data = go.Data([trace_maxi, trace_mini])
# data = go.Data([trace_maxi])

layout = {
    "autosize": True,
    ##"hovermode": "closest",
    "legend": {"x": 0.44,
               "y": 1.03,
               "orientation": "v",
               "bgcolor": "rgba(209, 205, 205, 0.01)",
               "traceorder": "reversed"
               },
    ##    "margin": {"r": 50,
    ##               "t": 80,
    ##               "b": 80,
    ##               "l": 80,
    ##               "pad": 30},
    "paper_bgcolor": "rgba(209, 205, 205, 0.4)",
    "plot_bgcolor": "rgba(249, 245, 245. 0,3)",
    "showlegend": True,
    "title": "Parramatta River Levels @ Drummoyne Wharf",
    "xaxis": {"autorange": True,
              "domain": [0, 1],
              "showgrid": True,
              "showticklabels": True,
              "tickfont": {"color": "rgb(14, 10, 19)", "size": 10},
              # "side": "top",
              "type": "date",
              "zeroline": False},
    "xaxis2": {"autorange": True,
               "anchor": "y2",
               "domain": [0, 1],
               # "title": "Local Time, Sydney AEDT",
               # "side": "top",
               "tickfont": {"color": "rgb(48, 13, 89)", "size": 10},
               "type": "date"},
    "yaxis": {"anchor": "x",
              "autorange": True,
              "domain": [0.0, 0.5],
              "range": [YLOWER, YUPPER],
              "showgrid": True,
              "showticklabels": True,
              "side": "left",
              "ticks": "inside",
              "title": "Approx CM",
              "titlefont": {"size": 10},
              "type": "spline",
              "zeroline": True},
    "yaxis2": {"anchor": "x2",
               "autorange": False,
               "domain": [0.55, 1.0],
               "range": [YLOWER, YUPPER],
               "showgrid": True,
               "showticklabels": True,
               "side": "left",
               "ticks": "inside",
               "title": "Approx CM",
               "titlefont": {"size": 10},
               "type": "spline",
               "zeroline": True},
}

figure = go.Figure(data=data, layout=layout)

if OVERWRITE is True:
    py.plot(figure, filename='BariFFT', auto_open=False)  # Overwrites the error you just introduced
else:
    py.plot(figure, filename='BariFFT', auto_open=False, fileopt='extend')  # Appends trace spools

stream_maxi_data = py.Stream(stream_id=stream_token[0])
stream_mini_data = py.Stream(stream_id=stream_token[1])

stream_maxi_data.open()
stream_mini_data.open()

rightnow = 0
sum_of_current_list = 0.0

current_readings = []
count = 0
count2 = 0
while True:
    now = datetime.now()
    rightnow = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    try:
        pressure, temperatue = sensor.get_data()
    except OSError:
        sensor.__init__()
        pressure, temperatue = sensor.get_data()

    if len(current_readings) >= ZERO_SAMPLE:
        sum_of_current_list -= current_readings.pop()
    sum_of_current_list += pressure
    current_readings.append(pressure)
    floating_zero = sum_of_current_list / len(current_readings)  # floating zero

    pressure -= floating_zero
    pressure /= 50

    count += 1
    stream_mini_data.write({"x": rightnow, "y": pressure})
    if count >= 9:
        count = 0
        count2 += 1
        stream_maxi_data.write({"x": rightnow, "y": pressure})
        now_counter = int(now.strftime('%H%M'))
        # print('*')
        if now_counter % 100 == 0 and count2 >= 30:  # Every hour
            sensor.reset()  # recalibrate for ambient temperature/pressure change DDS, does't do shit. Twice an hour, in the same minute
            #    print('Get knocked down and get back up again')

            count2 = 0

    # SMOKO
    sleep(.1)

stream_maxi_data.close()
stream_mini_data.close()
## End
