# coding=utf-8

from datetime import datetime
from time import sleep

import plotly.graph_objs as go
import plotly.plotly as py

import ms5637

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.0.2'

# Bari sensor of MS5637
sensor = ms5637.Chip()
YUPPER = 40
YLOWER = -40
SETSIZE_MINI = 100
SETSIZE_MIDI = 1000
SETSIZE_MAXI = 10000
#OVERWRITE = True  # overwrites datafile
OVERWRITE = False  # appends datafile

credentials = py.get_credentials()
username = credentials['username']
api_key = credentials['api_key']
stream_token = credentials['stream_ids']

py.sign_in(username, api_key)

stream_level_mini = {'token': stream_token[0], 'maxpoints': SETSIZE_MINI}
stream_level_midi = {'token': stream_token[1], 'maxpoints': SETSIZE_MIDI}
stream_level_maxi = {'token': stream_token[2], 'maxpoints': SETSIZE_MAXI}

trace1 = {
    'stream': stream_level_mini,
    "x": [],
    "y": [],
    "mode": "lines",
    "name": "Last 10 seconds",
    "type": "scatter",
    "xaxis": "x",
    "yaxis": "y",
    "line": {"shape": "spline", "width": 1}
}

trace2 = {
    'stream': stream_level_midi,
    "x": [],
    "y": [],
    "mode": "lines",
    "name": "Last 2½ Minutes",
    "type": "scatter",
    "xaxis": "x2",
    "yaxis": "y2",
    "line": {"shape": "spline", "width": 1}
}

trace3 = {
    'stream': stream_level_maxi,
    "x": [],
    "y": [],
    "mode": "lines",
    "name": "100X Timeframe",
    "type": "scatter",
    "xaxis": "x3",
    "yaxis": "y3",
    "line": {"shape": "spline", "width": 1}
 }
data = go.Data([trace1, trace2, trace3])

layout = {
    "autosize": True,
    "hovermode": "closest",
    "legend": {"x": 0.44,
               "y": 1.03,
               "orientation": "v",
               "bgcolor": "rgba(209, 205, 205, 0.01)",
          #     "traceorder": "reversed"
               },
    "margin": {"r": 20,
               "t": 50,
               "b": 50,
               "l": 50,
               "pad": 0},
    "paper_bgcolor": "rgba(209, 205, 205, 0.4)",
    "plot_bgcolor": "rgba(249, 245, 245. 0,3)",
    "showlegend": True,
    "title": "Parramatta River Levels at Drummoyne Wharf",
    "xaxis": {"autorange": True,
              "domain": [0, 1],
              "showgrid": True,
              "showticklabels": True,
              "tickfont": {"color": "rgb(14, 10, 19)", "size": 10},
              #"side": "top",
              "type": "date",
              "zeroline": False},
    "xaxis2": {"autorange": True,
               "anchor": "y2",
               "domain": [0, 1],
              # "title": "Local Time, Sydney AEDT",
              # "side": "top",
               "tickfont": {"color": "rgb(48, 13, 89)", "size": 10},
               "type": "date"},
    "xaxis3": {"anchor": "y3",
               "autorange": True,
               "domain": [0, 1],
               "showgrid": True,
               "showticklabels": True,
             #  "side": "top",
               "type": "date",
               "zeroline": False},
    "yaxis": {"anchor": "x",
              "autorange": False,
              "domain": [0.80, 1],
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
               "domain": [0.50, .75],
               "range": [YLOWER, YUPPER],
               "showgrid": True,
               "showticklabels": True,
               "side": "left",
               "ticks": "inside",
               "title": "Approx CM",
               "titlefont": {"size": 10},
               "type": "spline",
               "zeroline": True},
    "yaxis3": {"anchor": "x3",
               "autorange": True,
               "domain": [0, .45],
               "range": [YLOWER, YUPPER],
               "showgrid": True,
               "showticklabels": True,
               "side": "left",
               "ticks": "inside",
               "title": "Approx CM",
               "titlefont": {"size": 10},
               "type": "spline",
               "zeroline": True}
}
fig = go.Figure(data=data, layout=layout)

if OVERWRITE is True:
    py.plot(fig, filename='BariSensor', auto_open=False)  # Overwrites the error you just introduced
else:
    py.plot(fig, filename='BariSensor', auto_open=False, fileopt='extend')  # Appends trace spools

stream_data1 = py.Stream(stream_id=stream_token[0])
stream_data2 = py.Stream(stream_id=stream_token[1])
stream_data3 = py.Stream(stream_id=stream_token[2])


stream_data1.open()
stream_data2.open()
stream_data3.open()

rightnow = 0
sum_of_list = 0.0
floating_zero_list = []
count = 0

while True:
    now = datetime.now()
    rightnow = now.strftime('%Y-%m-%d %H:%M:%S.%f')

    try:
        pressure, temperatue = sensor.bari()
    except OSError:
        sensor.__init__()
        pressure, temperatue = sensor.bari()

    if len(floating_zero_list) >= 2001:
        sum_of_list -= floating_zero_list.pop()

    sum_of_list += pressure
    floating_zero_list.append(pressure)
    floating_zero = sum_of_list / len(floating_zero_list)
    # print(pressure, ' SUM:', sum_of_list, ' List:', len(floating_zero_list))
    pressure -= floating_zero
    pressure /= 50  # @1/2 air chamber ratio approx pascal/water delta in centimetres
    count += 1
    # print(pressure)
    stream_data1.write({"x": rightnow, "y": pressure})
    stream_data2.write({"x": rightnow, "y": pressure})
    if count >= 9:
        count = 0
        stream_data3.write({"x": rightnow, "y": pressure})
    # SMOKO
    sleep(.1)

stream_data1.close()
stream_data2.close()
stream_data3.close()
