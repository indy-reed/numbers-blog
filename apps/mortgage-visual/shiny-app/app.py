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

# General financial functions for models:

# Mortgage payment - payment assumes an annuity immediate rather than an annuity
# due - meaning the first payment is made at time = 1 rather than at time = 0.
# Assumes annual as opposed to monthly payment of all mortgage, property tax, 
# and insurance. Assumes home loan compounds annually at fixed interest rate.

def a_nbar_i_pv (i: float, n: int) -> float:
    # where i is the interest rate and n is the number of payments (or the length
    # of the loan)
    return (1 - (1 + i) ^-n)/i

# Inflation rate is assumed to act geometrically and compounds like interests.
# The real interest rate or rate of return is the ratio of the nominal interest 
# rate to the inflation rate.

def r_real (r_nominal: float, r_inflation: float) -> float:
    return (1 + r_nominal) / (1 + r_inflation) - 1

# Functions for adjusting the time value of money based on a fixed rate.

# Future value  
def fv (pv: float, i: float, n: int) -> float:
    # where i is the rate of return (it may be nominal or real - adjusted for 
    # inflation), n is the time period and pv is the present value of the amount.
    return pv * (1 + i)^n

# Present value
def pv (fv: float, i: float, n: int) -> float:
    # where i is the rate of return (it may be nominal or real - adjusted for 
    # inflation) and n is the time period.
    fv * (1 + i)^-n

help_page = ui.markdown(
    "Contents for Help Page"
)

mortgage_page = ui.page_sidebar(
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
    ui.layout_columns(
        ui.value_box("House payment", 
                     ui.output_ui("house_payment"), 
                     ),
        ui.value_box("Property tax", 
                     ui.output_ui("property_tax"), 
                     ),
        ui.value_box("Homeowners insurance", 
                     ui.output_ui("insurance"), 
                     ),
        col_widths=[4, 4, 4],
    ),    
)

app_ui = ui.page_fluid(
    ui.h1("Mortgage"),
    ui.navset_card_underline(
        ui.nav_panel("Mortgage", mortgage_page),
        ui.nav_spacer(),  
        ui.nav_menu(
            "More",  # The title of the dropdown menu
            ui.nav_panel("Help", help_page),
            "---",  # A horizontal divider
            ui.nav_control(ui.a("Posit", href="https://posit.co", target="_blank")), # External link
            align="right", # Aligns the menu to the right side of the navbar
        ),
        id="selected_navset_card_underline",
    ),
    title="Mortgage",
)

def server(input, output, session):

    @render.ui
    def house_payment():

        house_price = input.home_price_slider()

        return "${:.2f}".format(house_price)

    @render.ui
    def property_tax():

        property_tax = input.tax_rate_slider() * input.home_price_slider() / 100

        return "${:.2f}".format(property_tax)

    @render.ui
    def insurance():

        property_tax = input.insurance_slider() * input.home_price_slider() / 100

        return "${:.2f}".format(property_tax)


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

