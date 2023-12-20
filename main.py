'''Module for the main entrypoint to the application'''

__all__ = ["main"]

# necessary imports for application
import os
from dotenv import load_dotenv

import pandas as pd
import psycopg2
import plotly.express as px
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")


@app.route('/')
def hello_world():
    '''
    Route to render the data visualization dashboard page

    Returns:
        str: Rendered HTML content.
    '''
    # Obtaining plotly line charts for all 4 datasets
    temperature_data = connect_to_db("CM_HAM_DO_AI1/Temp_value", "Temperature (Celsius)")
    ph_data = connect_to_db("CM_HAM_PH_AI1/pH_value", "pH")
    dissolved_oxygen_data = connect_to_db("CM_PID_DO/Process_DO", "Dissolved Oxygen (%)")
    pressure_data = connect_to_db("CM_PRESSURE/Output", "Pressure (psi)")

    # returning dashboard page and providing charts as input
    return render_template("index.html", temp=temperature_data, pH=ph_data, DO=dissolved_oxygen_data, pres=pressure_data)


def connect_to_db(table_name, y_axis):
    '''
    Connects to the database, obtains specified data, and returns a Plotly Express line chart

    Parameters:
        table_name (str): Name of table to obtain data from
        y_axis (str): Title for y-axis as well as the units

    Returns:
        plot_html (plotly chart): Interactive line chart displaying the data from the specified table
    '''
    # Load the variables from .env file to test connection to database use different password
    load_dotenv()

    # handling configuration
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")

    # making connection to database
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    # Query data from the database
    query = f'SELECT time, value FROM public."{table_name}";'
    df = pd.read_sql(query, conn)

    # Create a Plotly Express line chart
    fig = px.line(df, x='time', y='value', labels={'x': 'Time', 'y': 'Value'}, render_mode="svg")

    #updating layout to fit on page better and fix display
    fig.update_layout(
        autosize=False,
        width=1200,
        height=500,
        yaxis=dict(
            title_text=y_axis,
            titlefont=dict(size=20),
        ),
        xaxis=dict(
            title_text="Time (Timestamp)",
            titlefont=dict(size=20),
        ),
        margin=dict(l=100),
        paper_bgcolor="White",
    )

    #adjust y axis for margin room
    fig.update_yaxes(automargin='left+top')

    # Convert the Plotly figure to HTML
    plot_html = fig.to_html(full_html=False)

    # Close the database connection
    conn.close()

    return plot_html


def main() -> None:
    '''Main function entrypoint for the application'''
    app.run(host='0.0.0.0', port=8000)


if __name__ == "__main__":
    main()