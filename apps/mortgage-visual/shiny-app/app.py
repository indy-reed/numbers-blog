#
#   Template for a Shiny app with different features. When correctly implemented,
#   the code run. The web app will be empty with any error.
#

import faicons as fa
import numpy as np
import pandas as pd
import plotly.express as px

from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget  

help_page = ui.markdown(
    "Contents for Help Page"
)

income_page = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(id = "home_price_slider",
                        label = "Home price",
                        min = 0,
                        max = 1e6,
                        value = 2e5,
                        pre = "$"),
        ui.input_slider(id = "interest_rate_slider",
                        label = "Interest rate (API)",
                        min = 1,
                        max = 16,
                        value = 5,
                        step = 0.1,
                        post = " %"),
        ui.input_slider(id = "inflation_rate_slider",
                        label = "Inflation rate",
                        min = 1,
                        max = 16,
                        value = 5,
                        step = 0.1,
                        post = " %"),
        ui.input_slider(id = "appreciation_rate_slider",
                        label = "Appreciation rate",
                        min = 1,
                        max = 16,
                        value = 5,
                        step = 0.1,
                        post = " %"),
        ui.input_slider(id = "tax_rate_slider",
                        label = "Property tax rate per $100 of home price (appraised value)",
                        min = 0,
                        max = 4,
                        value = 2,
                        step = 0.1,
                        post = " %"),
        ui.input_slider(id = "insurance_slider",
                        label = "Homeowners insurance rate per $100 of home price",
                        min = 0,
                        max = 4,
                        value = 2,
                        step = 0.1,
                        post = " %"),
        bg="#f8f8f8"
    ),
)

app_ui = ui.page_fluid(
    ui.h1("Mortgage"),
    ui.navset_card_underline(
        ui.nav_panel("Income", income_page),
        ui.nav_spacer(),  
        ui.nav_menu(
            "More",  # The title of the dropdown menu
            ui.nav_panel("Help", help_page),
            "---",  # A horizontal divider
            ui.nav_control(ui.a("Posit", href="https://posit.co", target="_blank")), # External link
            ui.nav_control(ui.a("US Census", href="https://data.census.gov/", target="_blank")), # External link
            ui.nav_control(ui.a("BLS", href="https://www.bls.gov/", target="_blank")), # External link
            align="right", # Aligns the menu to the right side of the navbar
        ),
        id="selected_navset_card_underline",
    ),
    title="Mortgage",
)

def server(input, output, session):
    pass

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

