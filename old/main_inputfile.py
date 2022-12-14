import base64
import json
import re
import time

import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.interpolate as sc
from dash import Dash, dcc, html, ctx
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

## Variables
movespeed = " F3000"
probespeed = " F500"
sol_ON = "M08\n"
sol_OFF = "M09\n"
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

## Initiate program
# s = serial.Serial('/dev/tty.usbmodem101', 115200)
# print("Starting up DocumeNDT firmware...")
log = open('../dynamic_text_files/logfile.txt', 'a')


def stream():
    # f = open('dynamic_text_files/grbl.gcode', 'r')
    #
    # # Wake up grbl
    # temp = "\r\n\r\n"
    # s.write(temp.encode())
    # time.sleep(0.1)  # Wait for grbl to initialize
    # s.flushInput()  # Flush startup text in serial input
    #
    # # Stream g-code to grbl
    # for line in f:
    #     l = line.strip()  # Strip all EOL characters for consistency
    #     print('Sending: ' + l)
    #     tempo = l + '\n'
    #     s.write(tempo.encode())  # Send g-code block to grbl
    #     grbl_out = s.readline()  # Wait for grbl response with carriage return
    #     print(' : ' + str(grbl_out.strip()))
    #     log.write('Sending: ' + l + '\n')
    #     log.write(str(grbl_out.strip()) + '\n')
    #
    # # # Wait here until grbl is finished to close serial port and file.
    # # input("  Press <ENTER> to exit and disable the control firmware.")
    #
    # # Close file and serial port
    # f.close()
    # # s.close()
    return "streamed"


def df_maker():
    temp_lst = []
    # string to search in file
    word = 'PRB:'
    with open(r'../dynamic_text_files/logfile.txt', 'r') as fp:
        # read all lines in a list
        lines = fp.readlines()
        for line in lines:
            # check if string present on a current line
            if line.find(word) != -1:
                # print('Line Number:', lines.index(line))
                # print('Line:', line)
                xyz = [float(s) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', line)]
                temp_lst.append(xyz)
                # print(xyz)
    df = pd.DataFrame(temp_lst, columns=['x', 'y', 'h (z)', 'scale'])
    # print(df)
    df.to_csv('probing_points.csv', sep='\t')
    return df


def last_movement_searcher():
    templst = []
    word = 'G90 X'
    with open(r'../dynamic_text_files/logfile.txt', 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            if line.find(word) != -1:
                xy = [float(s) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', line)]
                templst.append(xy)
    if len(templst) == 0:
        templst = [[0.0, 0.0, 0.0]]
    else:
        templst = templst

    return templst


def surface_plot(df):
    x = np.array(df["x"])
    # print(x)
    y = np.array(df["y"])
    # print(y)
    z = np.array(df["h (z)"])
    # print(z)

    xi = np.linspace(x.min(), x.max(), 100)
    yi = np.linspace(y.min(), y.max(), 100)

    X, Y = np.meshgrid(xi, yi)

    Z = sc.griddata((x, y), z, (X, Y), method='cubic')

    fig = go.Figure(go.Surface(x=xi, y=yi, z=Z))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True,
                                      highlightcolor="limegreen", project_z=True))
    fig.update_layout(title='Wall Surface [mm]')
    fig.update_layout(template="plotly",
                      scene=dict(
                          zaxis=dict(range=[min(z), max(z)])))
    # width=700,
    # margin=dict(r=20, l=10, b=10, t=10))

    # fig.show()
    return fig


app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])

# Encoded Images Used
title_png = 'Images/DocumeNDT.png'
test_base64 = base64.b64encode(open(title_png, 'rb').read()).decode('ascii')
solenoid_png = 'Images/walle.svg'
solenoid_base64 = base64.b64encode(open(solenoid_png, 'rb').read()).decode('ascii')

app.layout = html.Div([
    html.Div(children=[
        html.H1('Data points'),
        # html.Label('Number of HORIZONTAL points'),
        # dcc.Slider(1, 10, 1, value=3, id='slider-input-mesh-horizontal',
        #            marks={
        #                1: {'label': '1 ', 'style': {'color': '#FFFFFF'}},
        #                2: {'label': '2 ', 'style': {'color': '#FFFFFF'}},
        #                3: {'label': '3 ', 'style': {'color': '#FFFFFF'}},
        #                4: {'label': '4 ', 'style': {'color': '#FFFFFF'}},
        #                5: {'label': '5 ', 'style': {'color': '#FFFFFF'}},
        #                6: {'label': '6 ', 'style': {'color': '#FFFFFF'}},
        #                7: {'label': '7 ', 'style': {'color': '#FFFFFF'}},
        #                8: {'label': '8 ', 'style': {'color': '#FFFFFF'}},
        #                9: {'label': '9  ', 'style': {'color': '#FFFFFF'}},
        #                10: {'label': '10', 'style': {'color': '#FFFFFF'}}
        #
        #            }
        #            ),
        # html.Div(id='slider-output-mesh-horizontal'),
        #
        # html.Label('Number of VERTICAL points'),
        # dcc.Slider(1, 10, 1, value=3, id='slider-input-mesh-vertical',
        #            marks={
        #                1: {'label': '1', 'style': {'color': '#FFFFFF'}},
        #                2: {'label': '2', 'style': {'color': '#FFFFFF'}},
        #                3: {'label': '3', 'style': {'color': '#FFFFFF'}},
        #                4: {'label': '4', 'style': {'color': '#FFFFFF'}},
        #                5: {'label': '5', 'style': {'color': '#FFFFFF'}},
        #                6: {'label': '6', 'style': {'color': '#FFFFFF'}},
        #                7: {'label': '7', 'style': {'color': '#FFFFFF'}},
        #                8: {'label': '8', 'style': {'color': '#FFFFFF'}},
        #                9: {'label': '9 ', 'style': {'color': '#FFFFFF'}},
        #                10: {'label': '10', 'style': {'color': '#FFFFFF'}}
        #
        #            }
        #            ),
        # html.Div(id='slider-output-mesh-vertical'),
        #
        # html.Div(children=[
        #     html.Label('Enter X-offset [mm] in the work area:'),
        #     dbc.Input(id='x-offset', type='number', value=0.0),
        #     html.Div(id='output-x-offset'),
        #
        #     html.Label('Enter Y-offset [mm] in the work area:'),
        #     dbc.Input(id='y-offset', type='number', value=0.0),
        #     html.Div(id='output-y-offset')
        # ]),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload'),
        dcc.Graph(id="plot"),

        html.Div([
            dcc.Markdown("""
                ***Current Position:*** 
            """),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Br(),
        dcc.Graph(id="3dplot"),
        dcc.Interval(id="refresh-graph-interval", disabled=False, interval=5000),

        dbc.Row([
            dbc.Col([
                dbc.Button('Download Excel', id='btn-nclicks-12', color='success', outline=True),
                html.Div(id='download-button'), html.Div(id='download-button-output'),
                dcc.Download(id="download-dataframe-xlsx")], width='auto'
            ),
            dbc.Col([
                dbc.Button('Delete previous datapoints', id='btn-nclicks-13', color='danger', outline=True),
                html.Div(id='delete-button-output')
            ])], justify='center')
    ], style={'padding': 50, 'flex': 1}),

    ########################################################################################################################

    ########################################################################################################################

    html.Div(children=[
        html.H1('Solenoid'),
        dbc.Row([dbc.Col([
            daq.Knob(
                id="frequency-knob",
                label="Frequency [Hz]",
                value=3,
                color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 7.5], "red": [7.5, 10]}}
            )]
        ),
            dbc.Col(
                daq.Knob(
                    id='hitting-knob',
                    label="Number of Hits [-]",
                    max=500,
                    value=25
                )

            )]),
        dbc.Row([
            dbc.Col(html.Div(id='slider-output-frequency'), width="auto"),
            dbc.Col(html.Div(id='hitter-output-frequency'), width="auto")
        ], justify="center"),

        # html.Label('Solenoid frequency [Hz]'),
        # dcc.Slider(1, 10, 0.25, value=3, id='slider-input-frequency',
        #            marks={
        #                1: {'label': '1 Hz', 'style': {'color': '#FFFFFF'}},
        #                2: {'label': '2 Hz', 'style': {'color': '#FFFFFF'}},
        #                3: {'label': '3 Hz', 'style': {'color': '#66E188'}},
        #                4: {'label': '4 Hz', 'style': {'color': '#FFFFFF'}},
        #                5: {'label': '5 Hz', 'style': {'color': '#FFFFFF'}},
        #                6: {'label': '6 Hz', 'style': {'color': '#FFFFFF'}},
        #                7: {'label': '7 Hz', 'style': {'color': '#FFFFFF'}},
        #                8: {'label': '8 Hz', 'style': {'color': '#FFFFFF'}},
        #                9: {'label': '9 Hz ', 'style': {'color': '#FFFFFF'}},
        #                10: {'label': '10Hz', 'style': {'color': '#DA0A0A'}}
        #
        #            }
        #            ),
        # html.Div(id='slider-output-frequency'),
        #
        # html.Br(),
        #
        # html.Label('Amount of hits per location:'),
        # dbc.Input(id='input-number-of-hits', type='number', value= 20),
        # html.Div(id='output-number-of-hits'),

        html.Br(),
        dbc.Row([dbc.Col(
            [dbc.Button('Home Machine', id='btn-nclicks-4', n_clicks=0, color='dark', outline=True),
             html.Div(id='home-button'), html.Div(id='home-button-output')], width='auto'
        ),
            dbc.Col([
                dbc.Button('Position Solenoid', id='btn-nclicks-1', n_clicks=0, color='primary', outline=True),
                html.Div(id='position-solenoid-button')], width="auto"
            ),
            dbc.Col([
                dbc.Button('Start Hitting', id='btn-nclicks-2', n_clicks=0, color="success", outline=True),
                html.Div(id='start-solenoid-button'),
                html.Div(id='start-solenoid-output')], width="auto"),

            # dbc.Col([
            #     dbc.Button('STOP', id='btn-nclicks-3', n_clicks=0, color="danger", outline=True),
            #     html.Div(id='stop-button'),
            #     html.Div(id='stop-button-output')
            # ], width="auto")

        ], justify='center'),
        html.Br(),
        html.H1('Controller'),

        html.Br(),
        dbc.Row([
            dbc.Col(
                html.Div(
                    [
                        html.P("X micro-adjustments [mm]"),
                        dbc.Input(type="number", min=-100, max=100, step=1, id="x-adjustment", value=0),
                    ],

                )
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P("Y micro-adjustments [mm]"),
                        dbc.Input(type="number", min=-100, max=100, step=0.5, id="y-adjustment", value=0),
                    ],

                )
            )]
            , justify='center'
        ),
        html.Br(),
        dbc.Row(dbc.Col([
            dbc.Button([html.I(className="bi bi-arrows-move"), "  Move"], id='btn-nclicks-100', n_clicks=0,
                       color="warning",
                       outline=False),
            html.Div(id='move-button'),
            html.Div(id='move-button-output')], width='auto'), justify='center'
        ),

        html.Br(),
        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.CardImg(src='https://www.hiig.de/wp-content/uploads/2016/04/Wall-e.jpg.jpg')
        ])

    ], style={'padding': 50, 'flex': 1}),  # right side
], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
    Output('slider-output-frequency', 'children'),
    Input('frequency-knob', 'value'))
def update_output(value):
    return '{} Hz'.format(np.round(value, 1))


@app.callback(
    Output('hitter-output-frequency', 'children'),
    Input('hitting-knob', 'value'))
def update_output(value):
    return '{} Hits'.format(int(np.round(value, 0)))


@app.callback(
    Output('start-solenoid-output', 'children'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('hitting-knob', 'value'),
    Input('frequency-knob', 'value')
)
def start_hitting(btn2, n, freq):  # n = number of hits, freq = frequency
    if "btn-nclicks-2" == ctx.triggered_id:
        msg = "Finished hitting cycle"
        f = open('../dynamic_text_files/grbl.gcode', 'a')
        number = np.round(n, 0)
        f.truncate(0)  # delete previous code
        t_wait = (1 / (2 * freq)) + 0.001  # for some reason the stream has this constant delay
        for i in range(int(number)):  # start hitting at t_wait interval for i times
            f.write(sol_ON)
            f.write('G4 P' + str(t_wait) + '\n')
            f.write(sol_OFF)
            f.write('G4 P' + str(t_wait) + '\n')
        f.close()
        stream()
        return html.Div(msg)


@app.callback(
    Output('home-button-output', 'children'),
    Input('btn-nclicks-4', 'n_clicks')
)
def home(btn4):  # n = number of hits, freq = frequency
    if "btn-nclicks-4" == ctx.triggered_id:
        msg = "Machine has homed"
        f = open('../dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write('G90 Z1 F5000')
        f.write('G90 X0 Y0 F5000\n')
        f.close()
        stream()
        return html.Div(msg)


@app.callback(
    Output('delete-button-output', 'children'),
    Input('btn-nclicks-13', 'n_clicks')
)
def home(btn13):  # n = number of hits, freq = frequency
    if "btn-nclicks-13" == ctx.triggered_id:
        msg = "All datapoints were deleted.\nReady for new test."
        log.truncate(0)

        return html.Div(msg)


@app.callback(
    Output("plot", "figure"),
    Input("slider-input-mesh-horizontal", "value"),
    Input("slider-input-mesh-vertical", "value"),
    Input("x-offset", "value"),
    Input("y-offset", "value")
)
def mesh_grid(res_x, res_y, x_offset, y_offset):
    w_cnc = 0.50
    h_cnc = 0.98
    x_offset = x_offset / 100
    y_offset = y_offset / 100
    w = w_cnc - x_offset
    h = h_cnc - y_offset
    dx = w / (res_x + 1)
    dy = h / (res_y + 1)

    x_lst = []
    for i in range(res_x):
        x_cc = dx * (i + 1) + x_offset
        x_lst.append(x_cc)
    y_lst = []
    for i in range(res_y):
        y_cc = dy * (i + 1) + y_offset
        y_lst.append(y_cc)

    x_cc = []
    y_cc = []
    for x in x_lst:
        for y in y_lst:
            x_cc.append(x)
            y_cc.append(y)

    fig1 = go.Figure(go.Scatter(x=x_cc, y=y_cc, mode="markers"))
    fig2 = go.Figure(
        go.Scatter(x=[x_offset, w_cnc, w_cnc, x_offset, x_offset], y=[y_offset, y_offset, h_cnc, h_cnc, y_offset],
                   fill="tonext"))
    # fig3 = go.Figure(
    #     go.Scatter(x=[0, w_cnc, w_cnc, 0, 0], y=[0, 0, h_cnc, h_cnc, 0],
    #                fill="tonext"))
    fig = go.FigureWidget(data=fig1.data + fig2.data)
    fig.update_xaxes(range=[0.0, 0.6])
    fig.update_traces(marker={'size': 15})
    fig.update_yaxes(range=[0, 1])
    fig.update_layout(template="plotly")
    fig.update_layout(showlegend=False)
    fig.update_yaxes(automargin='left+top+right+bottom')
    fig.update_layout(clickmode='event+select')

    fig.update_traces(marker_size=20)

    # fig.show()
    return fig


@app.callback(
    Output('click-data', 'children'),
    Input('plot', 'clickData'))
def display_click_data(clickData):
    if str(json.dumps(clickData, indent=2)) == "null":
        mssg = "No point has been selected.\nPlease click on a blue dot in order to move"
    else:
        # extract location data from
        txt = json.dumps(clickData, indent=2)
        xtxt = txt.splitlines()[6]
        ytxt = txt.splitlines()[7]
        x = float(xtxt[11:-1]) * 1000
        y = float(ytxt[11:-1]) * 1000
        print('\nSelected/clicked position [x] [y]:')
        print(x, y)

        # Creating GCODE
        f = open('../dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(sol_OFF)
        f.write("G90 Z1" + movespeed + "\n")  # home z axis
        # f.write('G91 G01 Z20 F500\n')
        movetemp = "G90 X{} Y{}" + movespeed + "\n".format(x, y)
        f.write(movetemp)
        f.close()
        stream()

        mssg = "Arrived at: x = ", x, "   y = ", y, "   [mm]"
    return mssg


# Position solenoid
@app.callback(
    Output('position-solenoid-button', 'children'),
    Input('btn-nclicks-1', 'n_clicks')
)
def hit(btn1):
    if "btn-nclicks-1" == ctx.triggered_id:
        msg = "Solenoid is in position."
        f = open('../dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(sol_ON)
        f.write(sol_OFF)
        f.write('G38.5 Z150' + probespeed + '\n')  # probe up to 150 mm deep
        f.write('G91 G01 Z-5 F5000\n')  # move back if needed
        f.close()
        stream()
        return html.Div(msg)


# Refresh 3D
@app.callback(
    Output("3dplot", "figure"),
    [Input("refresh-graph-interval", "n_intervals")]
)
def refresh_graph_interval_callback(n_intervals):
    if n_intervals is not None:
        for i in range(0, 5):
            time.sleep(0.1)
            if int(len(df_maker())) == 0:
                x = np.linspace(0, 1, 10)
                y = x
                z = np.array([0] * len(x))

                fig3d = go.Figure(go.Surface(x=x, y=y, z=z))
            elif int(len(df_maker())) == 1:
                x = np.linspace(0, 1, 10)
                y = x
                z = np.array([0] * len(x))

                fig3d = go.Figure(go.Surface(x=x, y=y, z=z))
            elif int(len(df_maker())) == 2:
                x = np.linspace(0, 1, 10)
                y = x
                z = np.array([0] * len(x))

                fig3d = go.Figure(go.Surface(x=x, y=y, z=z))

            else:
                fig3d = surface_plot(df_maker())
            return fig3d
    raise PreventUpdate()


# Dowload dataframe as excel file
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn-nclicks-12", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    df = df_maker()
    return dcc.send_data_frame(df.to_excel, "wall_heights.xlsx", sheet_name="Wall")


@app.callback(
    Output("move-button-output", "children"),
    Input("btn-nclicks-100", "n_clicks"),
    Input("x-adjustment", "value"),
    Input("y-adjustment", "value")
)
def mini_move(btn, x, y):  # TODO: add button input + code rest of function
    if "btn-nclicks-100" == ctx.triggered_id:
        current_x = float(last_movement_searcher()[-1][-2])
        current_y = float(last_movement_searcher()[-1][-1])
        X = current_x + x
        Y = current_y + y

        # Creating GCODE
        f = open('../dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(sol_OFF)
        f.write("G90 Z1" + movespeed + "\n")  # home z axis
        movetemp = "G90 X" + str(X) + " Y" + str(Y) + movespeed + "\n"
        f.write(movetemp)
        f.close()
        stream()
        # mesg = "Arrived at {}, {} [mm]".format(X, Y)
    # return mesg


if __name__ == '__main__':
    app.run_server(debug=True)
