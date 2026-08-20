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

ICONS = {
    "payment": fa.icon_svg("sack-dollar"),
    "tax": fa.icon_svg("building-columns"),
    "house": fa.icon_svg("house-flood-water"),
}

# General financial functions for models:

# Mortgage payment - payment assumes an annuity immediate rather than an annuity
# due - meaning the first payment is made at time = 1 rather than at time = 0.
# Assumes annual as opposed to monthly payment of all mortgage, property tax, 
# and insurance. Assumes home loan compounds annually at fixed interest rate.

def a_nbar_i_pv (i: float, n: int) -> float:
    # where i is the interest rate and n is the number of payments (or the length
    # of the loan)
    return (1 - pow(1 + i, -n))/i

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

# Payment schedule
def create_payment_schedule (p: float, r: float, i: float, a: float, ptr: float, hir: float, n: int) :
    # where r is the interest rate, n is the number of payments (or the length
    # of the loan), p is the mortgage repayment amount, a is the appreciation
    # rate.
    #   PV = (Payment) [Annuity Immediate (interest rate, term) ] = Home price
    payment = p / a_nbar_i_pv(i = r, n = n)

    # Construct mortgage table as reference for visualization
  
    # Number of years from start of the mortgage
    time = pd.series(range(1, n))
  
    # Level mortgage payment, level property tax payment, level insurance premium
    # payment, mortgage interest and principal
    mortgage_payment = pd.series([payment] * n)
    interest_payment = pd.series([float('nan')] * n)
    principal_payment = pd.series([float('nan')] * n)
  
    # Property tax and homeowners insurances will be based on the value of the
    # house.
    home_value = pd.series([p] * n)
    property_tax_rate = pd.series([ptr * p] * n)
    home_insurance_rate = pd.series([hir * p] * n)
  
    # variable used to track how much of the home loan has been paid.
    # The value will be used to determine how much interest is paid for
    # a particular payment. 
    remaining_principal = p
  
    # For the moment, it is easier to iterate through each year and decrease
    # the principal from the loan amount.
    for j in range(n):
        interest_payment = remaining_principal * r
        principal_payment[j] = payment - interest_payment[j]
        remaining_principal = remaining_principal - principal_payment[j] 

    # appreciated home value. Assumes constant appreciation rate. Parameter
    # supplied in function input. Nominal rate - not adjusted to inflation.
    nominal_value = fv(pv = home_value, i = r, n = time)
  
    # appreciated value of property tax amount
    nominal_property_tax = fv(pv = property_tax_rate, i = a, n = time)

    # appreciated value of homeowners insurance amount
    nominal_home_insurance = fv(pv = home_insurance_rate, i = a, n = time)
  
    # inflation adjustments. Assumes inflation compounds with time at a constant
    # rate (i) which is supplied as a parameter to the function.
    # Each nominal mortgage payment is adjusted for inflation. 
    real_mortgage_payment = pv(fv = mortgage_payment, i = i, n = time)
  
    # Each nominal portion of principal is adjusted for inflation. 
    # real_principal_payment = pv(fv = principal_payment, i = i, n = time)
  
    # Each interest portion of principal is adjusted for inflation. 
    # real_interest_payment = pv(fv = interest_payment, i = i, n = time)
  
    # Real appreciation rate: nominal appreciation rate (a) adjusted for
    # inflation (i).
    # real_appreciation_rate = r_real(a, i)
  
    # Real future value of house over time.
    # real_value = fv(pv = p, i = real_appreciation_rate, n = time)
    # real_property_tax = fv(pv = property_tax_rate, i = real_appreciation_rate, n = time)
    # real_home_insurance = fv(pv = home_insurance_rate, i = real_appreciation_rate, n = time)
  
    # Combine information into a data frame for visualization and other analysis.
    payment_schedule = pd.DataFrame({'time': time, 'nominal_mortgage': mortgage_payment, 
    'nominal_principal': principal_payment, 'nominal_interest': interest_payment,
    'nominal_value': nominal_value, 'nominal_property_tax': nominal_property_tax,
    'nominal_home_insurance': nominal_home_insurance, 'real_mortgage': real_mortgage_payment})
#   payment_schedule <- tibble(time = time, 
#                              nominal_mortgage = mortgage_payment, 
#                              nominal_principal = principal_payment,
#                              nominal_interest = interest_payment,
#                              nominal_value = nominal_value,
#                              nominal_property_tax = nominal_property_tax,
#                              nominal_home_insurance = nominal_home_insurance,
#                              real_mortgage = real_mortgage_payment,
#                              real_principal = real_principal_payment,
#                              real_interest = real_interest_payment,
#                              real_value = real_value,
#                              real_property_tax = real_property_tax,
#                              real_home_insurance = real_home_insurance)

    return(payment_schedule)


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
        ui.value_box("Mortgage payment", 
                     ui.output_ui("house_payment"), 
                     showcase=ICONS["payment"],
                     ),
        ui.value_box("Property tax", 
                     ui.output_ui("property_tax"), 
                     showcase=ICONS["tax"],
                     ),
        ui.value_box("Homeowners insurance", 
                     ui.output_ui("insurance"), 
                     showcase=ICONS["house"],
                     ),
        col_widths=[4, 4, 4],
    ),    
    ui.layout_columns(
        ui.card(
            ui.card_header("Data"),
            ui.output_data_frame("schedule_df"),
        ),
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

        mortgage_payment = input.home_price_slider()/a_nbar_i_pv(0.01*input.interest_rate_slider(), 30)

        return "${:.2f}".format(mortgage_payment)

    @render.ui
    def property_tax():

        property_tax = input.tax_rate_slider() * input.home_price_slider() / 100

        return "${:.2f}".format(property_tax)

    @render.ui
    def insurance():

        property_tax = input.insurance_slider() * input.home_price_slider() / 100

        return "${:.2f}".format(property_tax)

    @render.data_frame
    def schedule_df():

        mortgage_payment = create_payment_schedule(
            input.home_price_slider(),
            0.01*input.interest_rate_slider(),
            0.01*input.inflation_rate_slider(),
            0.01*input.appreciation_rate_slider(),
            0.01*input.tax_rate_slider(),
            0.01*input.insurance_slider(),
            30)

        return render.DataGrid(data=mortgage_payment)


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

