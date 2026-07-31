#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    https://shiny.posit.co/
#

# Load packages used by the app
library(shiny)
library(bslib)
library(thematic)
library(tidyverse)

# helpers.R

# Set the default theme for ggplot2 plots
ggplot2::theme_set(ggplot2::theme_minimal())

# Apply the CSS used by the Shiny app to the ggplot2 plots
thematic_shiny()

# Wage model for pricing food at its affects on other variables.

meal_labor_cost <-function (meal_per_hour, labor_per_hour) {
  return(labor_per_hour/meal_per_hour)
}

meal_price <- function (material_cost, labor_cost, profit) {
  return(material_cost + labor_cost + profit)
}

my_demand <- function (budget, price){
  return(floor(budget / price))
}

# Define the Shiny UI layout
ui <- fluidPage(
  # Application title
  titlePanel("How inflation ate my lunch"),
  sliderInput(
    "material", 
    "Cost of Materials per meal", 
    min = 0, 
    max = 20, 
    value = 5,
    step = 0.1,
    round = FALSE
  ),
  sliderInput(
    "labor", 
    "Cost of Labor per hour", 
    min = 0, 
    max = 20, 
    value = 9,
    step = 0.1,
    round = FALSE
  ),
  sliderInput(
    "prod", 
    "Meals per hour", 
    min = 0, 
    max = 10, 
    value = 2,
    step = 0.1,
    round = FALSE
  ),
  sliderInput(
    "profit", 
    "Profit", 
    min = 0, 
    max = 20, 
    value = 0.5,
    step = 0.1,
    round = FALSE
  ),
  sliderInput(
    "budget", 
    "My Weekly Budget", 
    min = 0, 
    max = 100, 
    value = 50,
  ),
  verbatimTextOutput("price"),
  verbatimTextOutput("demand")
)

# Define the Shiny server function
server <- function(input, output) {
  labor_data <- reactive({
    meal_labor_cost(
      input$prod,
      input$labor
    )
  })
  meal_data <- reactive({
    meal_price(
      input$material,
      labor_data(),
      input$profit
    )
  })
  demand_data <- reactive({
    my_demand(
      input$budget,
      meal_data()
    )
  })
  output$price <- renderText({meal_data()})
  output$demand <- renderText({demand_data()})
}

# Create the Shiny app
shinyApp(ui = ui, server = server)
