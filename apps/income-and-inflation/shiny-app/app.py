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
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

# Load inflation data 
cpi_data = pd.read_csv("cpi_dim.csv", header = 0)
cpi_data["inflation_rate"] = cpi_data["cpi_u"]/cpi_data["cpi_u"].shift(1) - 1
year_min_inf = cpi_data["year"].min()
year_max_inf = cpi_data["year"].max()

# Load population data
income_data_dis = pd.read_csv("income_data.csv", header = 0)
regions_arr = np.sort(income_data_dis["reg_name"].unique())
regions = regions_arr.tolist()

years_arr = np.sort(income_data_dis["year"].unique())
years = years_arr.tolist()
year_min = np.min(years_arr)
year_max = np.max(years_arr)

income_data_reg = income_data_dis.groupby(["year","reg_name"]).agg({"population":"sum","households":"sum","income_median":"median"}).reset_index()

# Determine reference year for inflation adjustment. Max year for income data from US Census.
year_ref = income_data_reg["year"].max()

# Compute inflation adjustment factor:
#   Inflation Adjustment Factor = CPI in reference year / CPI in year of interest
cpi_ref = cpi_data["cpi_u"].loc[cpi_data["year"] == year_ref].rename("cpi_ref")
cpi_data = pd.merge(left=cpi_data, right=cpi_ref, how="cross")
cpi_data["ref_inf_fac"] = cpi_data["cpi_ref"]/cpi_data["cpi_u"]

# Adjust income data for inflation using inflation adjustment factor.
income_data_reg = pd.merge(left=income_data_reg, right=cpi_data[["year","ref_inf_fac"]], how="inner", on="year")
income_data_reg["income_med_inf_adj"] = income_data_reg["income_median"]*income_data_reg["ref_inf_fac"]

income_data_adj = income_data_reg[["year","reg_name","income_med_inf_adj"]]
income_data_org = income_data_reg[["year","reg_name","income_median"]]

help_page = ui.markdown(
    "Contents for Help Page"
)

annual_median_income_data = ui.card(
    ui.card_header("Median Income Data"),
    ui.output_data_frame("income_df"),
)

annual_median_income_panel = ui.layout_columns(
    ui.card(
        ui.card_header("Median Income"),
        output_widget("income_org_plot"),
    ),    
    ui.card(
        ui.card_header("Inflation Adjusted Median Income in 2023 USD"),
        output_widget("income_adj_plot"),
    ),    
    col_widths=[6, 6],
)

income_page = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("inc_ann_slider",
                        "Select a year",
                        min=year_min,
                        max=year_max,
                        value=(min,max),
                        sep=""),
        ui.input_checkbox_group("inc_reg_check",
                                 "Select US Census Regions",
                                 choices=regions,
                                 selected=regions),
        bg="#f8f8f8"
    ),
    ui.layout_columns(
        ui.value_box("Number of Households", 
                     ui.output_ui("num_households"), 
                     ui.output_ui("year_cur_h"), 
                     showcase=ICONS["user"],
                     ),
        ui.value_box("Median Household Income", 
                     ui.output_ui("income_median"), 
                     ui.output_ui("year_cur_i"), 
                     showcase=ICONS["wallet"],
                     ),
        ui.value_box("Total Earnings", 
                     ui.output_ui("income_total"), 
                     ui.output_ui("year_cur_t"), 
                     showcase=ICONS["currency-dollar"],
                     ),
        col_widths=[4, 4, 4],
    ),
    ui.layout_columns(
        ui.navset_card_tab(
            ui.nav_panel("Annual Median Income", annual_median_income_panel),
            ui.nav_panel("Data", annual_median_income_data),
        ),
        ui.card(
            ui.card(ui.card_header("Income Distribution"),),
            output_widget("income_adj_ridgeplot"),
        ),
        col_widths=[12, 12],
    ),
)

cpi_page = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("cpi_ann_slider", 
                        "Select a year",
                        min=year_min_inf, 
                        max=year_max_inf,
                        value=(year_max_inf - 10, year_max_inf),
                        sep=""),
        bg="#f8f8f8"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Inflation Rate Estimated Using Consumer Price Index"),
            output_widget("cpi_plot"),
        ),
        ui.card(
            ui.card_header("Annual Counsumer Price Index and Inflation Rate"),
            ui.output_data_frame("cpi_df"),
        ),
        col_widths=[8, 4],
    ),    
)

app_ui = ui.page_fluid(
    ui.h1("Data Playground"),
    ui.navset_card_underline(
        ui.nav_panel("Income", income_page),
        ui.nav_panel("CPI", cpi_page),
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
    title="Data Playground",
)

def server(input, output, session):

    @reactive.calc
    def cpi_slice():

        year_first = input.cpi_ann_slider()[0]
        year_last = input.cpi_ann_slider()[1]

        return cpi_data.query("year >= {} and year <= {}".format(year_first, year_last))

    @reactive.calc
    def income_slice_org():

        year_first = input.inc_ann_slider()[0]
        year_last = input.inc_ann_slider()[1]
        region = input.inc_reg_check()
        data = income_data_org.query("year >= {} and year <= {}".format(year_first, year_last))
        data = data.loc[data["reg_name"].isin(region)]

        return data

    @reactive.calc
    def income_slice_adj():

        year_first = input.inc_ann_slider()[0]
        year_last = input.inc_ann_slider()[1]
        region = input.inc_reg_check()
        data = income_data_adj.query("year >= {} and year <= {}".format(year_first, year_last))
        data = data.loc[data["reg_name"].isin(region)]

        return data

    @render.ui
    def num_households():

        year = input.inc_ann_slider()[1]
        region = input.inc_reg_check()
        data = income_data_reg.query("year == {}".format(year))
        data = data.loc[data["reg_name"].isin(region)]

        return "{:.2f}M".format(data["households"].sum() / 1e6)

    @render.ui
    def income_median():

        year = input.inc_ann_slider()[1]
        region = input.inc_reg_check()
        data = income_data_dis.query("year == {}".format(year))
        data = data.loc[data["reg_name"].isin(region)]

        return "${:,.2f}".format(data["income_median"].median())

    @render.ui
    def income_total():

        year = input.inc_ann_slider()[1]
        region = input.inc_reg_check()
        data = income_data_dis.query("year == {}".format(year))
        data = data.loc[data["reg_name"].isin(region)]
        data["income_total"] = data["income_mean"] * data["households"]

        return "${:,.2f}T".format(data["income_total"].sum() / 1e12)

    @render.ui
    def year_cur_h():
        return "{}".format(input.inc_ann_slider()[1])

    @render.ui
    def year_cur_i():
        return "{}".format(input.inc_ann_slider()[1])

    @render.ui
    def year_cur_t():
        return "{}".format(input.inc_ann_slider()[1])

    @render.data_frame  
    def cpi_df():

        data = cpi_slice()
        data = data.rename(columns={"cpi_u":"cpi urban", "inflation_rate":"inflation rate"})
        data["inflation rate"] = data["inflation rate"].map("{:.4f}".format)
        data["cpi urban"] = data["cpi urban"].map("{:.1f}".format)

        return render.DataGrid(data=data[["year", "cpi urban", "inflation rate"]])

    @render.data_frame
    def income_df():

        year_first = input.inc_ann_slider()[0]
        year_last = input.inc_ann_slider()[1]
        region = input.inc_reg_check()
        data = income_data_reg.query("year >= {} and year <= {}".format(year_first, year_last))
        data = data.loc[data["reg_name"].isin(region)]
        data = data.rename(columns={"reg_name": "region", "income_median": "income median", "income_med_inf_adj": "adjusted median"})
        data["households"] = data["households"].map("{:,.0f}".format)
        data["income median"] = data["income median"].map("${:,.2f}".format)
        data["adjusted median"] = data["adjusted median"].map("${:,.2f}".format)

        return render.DataGrid(data=data[["year", "region", "households", "income median", "adjusted median"]])

    @render_widget  
    def cpi_plot():  

        lineplot = px.line(
            data_frame=cpi_slice(),
            x="year",
            y="inflation_rate"
        )

        lineplot.update_layout(
            xaxis_title = "year",
            yaxis_title = "inflation rate",
        ) 
        return lineplot

    @render_widget
    def income_adj_plot():  

        lineplot = px.line(
            data_frame=income_slice_adj(),
            x="year",
            y="income_med_inf_adj",
            color="reg_name"
        )

        lineplot.update_layout(
            xaxis_title = "year",
            yaxis_title = "median income (2023 USD)",
            legend_title = "region",
        ) 
            
        return lineplot

    @render_widget
    def income_org_plot():  

        lineplot = px.line(
            data_frame=income_slice_org(),
            x="year",
            y="income_median",
            color="reg_name"
        )

        lineplot.update_layout(
            xaxis_title = "year",
            yaxis_title = "median income",
            legend_title = "region",
        ) 

        return lineplot

    @render_widget
    def income_adj_ridgeplot():
        from ridgeplot import ridgeplot

        year = input.inc_ann_slider()[1]
        reg_list = input.inc_reg_check()
        income_data = [income_data_dis.query("year == {} and reg_name == '{}'".format(year,reg))["income_median"].to_list() for reg in reg_list]

        plt = ridgeplot(
            samples = income_data,
            labels = reg_list
        )
        return plt

    @render.text
    def text():
        return input.inc_reg_check()

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

