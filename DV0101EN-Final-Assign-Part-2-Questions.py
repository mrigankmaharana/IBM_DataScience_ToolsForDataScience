#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# 1. Load the data
data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/"
    "historical_automobile_sales.csv"
)

# 2. Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"   # Task 2.1

# 3. Prepare dropdown options
stat_options = [
    {"label": "Yearly Statistics",           "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]
year_list = list(range(1980, 2014))  # valid years 1980–2013

# 4. Define the layout
app.layout = html.Div([
    # -- Title --
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={
            "textAlign": "center",
            "color": "#503D36",
            "font-size": "24px"
        }
    ),

    # -- Report-type dropdown --
    html.Div([
        html.Label("Select Report‐Type:"),
        dcc.Dropdown(
            id="dropdown-statistics",
            options=stat_options,
            value=None,                     # start with no selection
            placeholder="Select a report type",
            clearable=False,
            style={
                "width": "80%",
                "padding": "3px",
                "font-size": "20px",
                "text-align-last": "center"
            }
        )
    ], style={"margin": "10px"}),

    # -- Year selector dropdown --
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id="select-year",
            options=[{"label": y, "value": y} for y in year_list],
            value=year_list[0],             # default fallback
            placeholder="Select year",
            clearable=False,
            disabled=True                   # start disabled
        )
    ], style={"margin": "10px"}),

    # -- Output container --
    html.Div([
        html.Div(
            id="output-container",
            className="chart-grid",
            style={"display": "flex", "flexDirection": "column", "gap": "20px"}
        )
    ])
])

# 5. Callback to enable/disable the year dropdown
@app.callback(
    Output("select-year", "disabled"),
    Input("dropdown-statistics", "value")
)
def toggle_year_dropdown(selected_statistics):
    # enable only when Yearly Statistics is chosen
    return selected_statistics != "Yearly Statistics"

# 6. Callback to render the graphs
@app.callback(
    Output("output-container", "children"),
    [
        Input("dropdown-statistics", "value"),
        Input("select-year",         "value")
    ]
)
def update_output_container(selected_statistics, input_year):
    # ---- Recession Report ----
    if selected_statistics == "Recession Period Statistics":
        rec = data[data["Recession"] == 1]

        # 1) Avg sales over recession years
        yearly_rec = rec.groupby("Year")["Automobile_Sales"].mean().reset_index()
        R1 = dcc.Graph(figure=px.line(
            yearly_rec, x="Year", y="Automobile_Sales",
            title="Average Sales Over Recession Years"
        ))

        # 2) Avg vehicles sold by type during recessions
        rec_vt = rec.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        R2 = dcc.Graph(figure=px.bar(
            rec_vt, x="Vehicle_Type", y="Automobile_Sales",
            title="Avg Vehicles Sold by Type During Recession"
        ))

        # 3) Pie chart: ad spend share
        rec_ad = rec.groupby("Vehicle_Type")["Advertising_Expenditure"] \
                    .sum().reset_index()
        R3 = dcc.Graph(figure=px.pie(
            rec_ad, names="Vehicle_Type", values="Advertising_Expenditure",
            title="Ad Expenditure Share by Vehicle Type (Recession)"
        ))

        # 4) Effect of unemployment rate on sales
        unemp_data = rec.groupby(
            ["unemployment_rate", "Vehicle_Type"]
        )["Automobile_Sales"].mean().reset_index()
        R4 = dcc.Graph(figure=px.bar(
            unemp_data,
            x="unemployment_rate",
            y="Automobile_Sales",
            color="Vehicle_Type",
            labels={
                "unemployment_rate": "Unemployment Rate",
                "Automobile_Sales":  "Average Automobile Sales"
            },
            title="Effect of Unemployment Rate on Vehicle Type and Sales"
        ))

        return [
            html.Div([R1, R2], style={"display":"flex", "gap":"20px"}),
            html.Div([R3, R4], style={"display":"flex", "gap":"20px"})
        ]

    # ---- Yearly Statistics ----
    elif selected_statistics == "Yearly Statistics" and isinstance(input_year, int):
        # 1) Yearly avg sales
        yearly = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y1 = dcc.Graph(figure=px.line(
            yearly, x="Year", y="Automobile_Sales",
            title="Yearly Automobile Sales Statistics"
        ))

        # 2) Total monthly sales for selected year
        monthly = (
            data[data["Year"] == input_year]
            .groupby("Month")["Automobile_Sales"]
            .sum().reset_index()
        )
        Y2 = dcc.Graph(figure=px.line(
            monthly, x="Month", y="Automobile_Sales",
            title=f"Total Monthly Sales in {input_year}"
        ))

        # 3) Avg vehicles sold by type
        year_sel = data[data["Year"] == input_year]
        avr = year_sel.groupby("Vehicle_Type")["Automobile_Sales"] \
                      .mean().reset_index()
        Y3 = dcc.Graph(figure=px.bar(
            avr, x="Vehicle_Type", y="Automobile_Sales",
            title=f"Avg Vehicles Sold by Type in {input_year}"
        ))

        # 4) Ad spend pie for that year
        exp = year_sel.groupby("Vehicle_Type")["Advertising_Expenditure"] \
                      .sum().reset_index()
        Y4 = dcc.Graph(figure=px.pie(
            exp, names="Vehicle_Type", values="Advertising_Expenditure",
            title=f"Ad Expenditure by Vehicle Type in {input_year}"
        ))

        return [
            html.Div([Y1, Y2], style={"display":"flex", "gap":"20px"}),
            html.Div([Y3, Y4], style={"display":"flex", "gap":"20px"})
        ]

    # nothing to show if no valid selection
    return []

# 7. Run the app
if __name__ == '__main__':
    app.run(debug=True)
