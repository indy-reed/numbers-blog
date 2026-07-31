#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    https://shiny.posit.co/
#

# The point at which home ownership is more advantageous than renting can be
# a bit subjective. There are bunch of variables to consider and in some cases
# it comes down to several factors.

# To start, consider all factors in a typical house payment:
#   1. Equity (Payment to Principal)
#   2. Interest
#   3. Insurance
#   4. Taxes

library(shiny)
library(bslib)
#library(tidyverse)

# General financial functions for models:

# Mortgage payment - payment assumes an annuity immediate rather than an annuity
# due - meaning the first payment is made at time = 1 rather than at time = 0.
# Assumes annual as opposed to monthly payment of all mortgage, property tax, 
# and insurance. Assumes home loan compounds annually at fixed interest rate.

a_nbar_i_pv <- function (i, n) {
  # where i is the interest rate and n is the number of payments (or the length
  # of the loan)
  (1 - (1 + i) ^-n)/i
}

# Inflation rate is assumed to act geometrically and compounds like interests.
# The real interest rate or rate of return is the ratio of the nominal interest 
# rate to the inflation rate.

r_real <- function(r_nominal, r_inflation) {
  (1 + r_nominal) / (1 + r_inflation) - 1
}

# Functions for adjusting the time value of money based on a fixed rate.

# Future value  
fv <- function(pv, i, n) {
  # where i is the rate of return (it may be nominal or real - adjusted for 
  # inflation), n is the time period and pv is the present value of the amount.
  pv * (1 + i)^n
}

# Present value
pv <- function(fv, i, n) {
  # where i is the rate of return (it may be nominal or real - adjusted for 
  # inflation) and n is the time period.
  fv * (1 + i)^-n
}

create_payment_schedule <- function(p, r, i, a, ptr, hir, n) {
  # where r is the interest rate, n is the number of payments (or the length
  # of the loan), p is the mortgage repayment amount, a is the appreciation
  # rate.
  #   PV = (Payment) [Annuity Immediate (interest rate, term) ] = Home price
  payment <- p / a_nbar_i_pv(i = r, n = n)
  
  # Construct mortgage table as reference for visualization
  
  # Number of years from start of the mortgage
  time <- seq(n)
  
  # Level mortgage payment, level property tax payment, level insurance premium
  # payment, mortgage interest and principal
  mortgage_payment <- rep(payment, n)
  interest_payment <- rep(NA_real_, n)
  principal_payment <- rep(NA_real_, n)
  
  # Property tax and homeowners insurances will be based on the value of the
  # house.
  home_value <- rep(p, n)
  property_tax_rate <- rep(ptr * p, n)
  home_insurance_rate <- rep(hir * p, n)
  
  # variable used to track how much of the home loan has been paid.
  # The value will be used to determine how much interest is paid for
  # a particular payment. 
  remaining_principal <- p
  
  # For the moment, it is easier to iterate through each year and decrease
  # the principal from the loan amount.
  for (j in 1:n) {
    interest_payment[j] <- remaining_principal * r
    principal_payment[j] <- payment - interest_payment[j]
    remaining_principal <- remaining_principal - principal_payment[j] 
  }
  
  # appreciated home value. Assumes constant appreciation rate. Parameter
  # supplied in function input. Nominal rate - not adjusted to inflation.
  nominal_value <- fv(
    pv = home_value,
    i = a,
    n = time
  )
  
  # appreciated value of property tax amount
  nominal_property_tax <- fv(
    pv = property_tax_rate,
    i = a,
    n = time
  )

  # appreciated value of homeowners insurance amount
  nominal_home_insurance <- fv(
    pv = home_insurance_rate,
    i = a,
    n = time
  )
  
  # inflation adjustments. Assumes inflation compounds with time at a constant
  # rate (i) which is supplied as a parameter to the function.
  # Each nominal mortgage payment is adjusted for inflation. 
  real_mortgage_payment <- pv(
    fv = mortgage_payment,
    i = i,
    n = time
  )
  
  # Each nominal portion of principal is adjusted for inflation. 
  real_principal_payment <- pv(
    fv = principal_payment,
    i = i,
    n = time
  )
  
  # Each interest portion of principal is adjusted for inflation. 
  real_interest_payment <- pv(
    fv = interest_payment,
    i = i,
    n = time
  )
  
  # Real appreciation rate: nominal appreciation rate (a) adjusted for
  # inflation (i).
  real_appreciation_rate <- r_real(a, i)
  
  # Real future value of house over time.
  real_value <- fv(
    pv = p,
    i = real_appreciation_rate,
    n = time
  )
  
  real_property_tax <- fv(
    pv = property_tax_rate,
    i = real_appreciation_rate,
    n = time
  )
  
  real_home_insurance <- fv(
    pv = home_insurance_rate,
    i = real_appreciation_rate,
    n = time
  )
  
  # Combine information into a data frame for visualization and other analysis.
  #payment_schedule <- tibble(time = time, 
  #                           nominal_mortgage = mortgage_payment, 
  #                           nominal_principal = principal_payment,
  #                           nominal_interest = interest_payment,
  #                           nominal_value = nominal_value,
  #                           nominal_property_tax = nominal_property_tax,
  #                           nominal_home_insurance = nominal_home_insurance,
  #                           real_mortgage = real_mortgage_payment,
  #                           real_principal = real_principal_payment,
  #                           real_interest = real_interest_payment,
  #                           real_value = real_value,
  #                           real_property_tax = real_property_tax,
  #                           real_home_insurance = real_home_insurance)

  #return(payment_schedule)
}

term <- 30

# Define UI for application 
ui <- fluidPage(

  # Application title
  titlePanel("To own or not to own"),
  
  sidebarLayout(
    sidebarPanel(
      sliderInput(inputId = "home_price_slider",
                  label = "Home price",
                  min = 0, 
                  max = 1e6, 
                  value = 2e5,
                  pre = "$"), 
      
      sliderInput(inputId = "interest_rate_slider",
                  label = "Interest rate (API)",
                  min = 1, 
                  max = 16, 
                  value = 5,
                  step = 0.1,
                  post = " %"), # Adds the '%' sign to the displayed value

      sliderInput(inputId = "inflation_rate_slider",
                  label = "Inflation rate",
                  min = 1, 
                  max = 16, 
                  value = 5,
                  step = 0.1,
                  post = " %"), # Adds the '%' sign to the displayed value
      
      sliderInput(inputId = "appreciation_rate_slider"
                  ,
                  label = "Appreciation rate",
                  min = 1, 
                  max = 16, 
                  value = 5,
                  step = 0.1,
                  post = " %"), # Adds the '%' sign to the displayed value
      
      # The maximum value of county by county property tax rates by Tax Foundation
      # found the highest effective property tax rate in the nation to be 3.6361%
      # in 2023 (Menominee County, WI). Several counties in Alaska, Hawaii, Nevada,
      # South Dakota, and Texas had did not report an effective rate.
      # 
      sliderInput(inputId = "tax_rate_slider",
                  label = "Property tax rate per $100 of home price (appraised value)",
                  min = 0, 
                  max = 4, 
                  value = 2,
                  step = 0.1,
                  post = " %"), # Adds the '%' sign to the displayed value

      # The maximum value on a state wide basis was roughly 2% of the replacement
      # cost of the home. Various options are available to move these rates up or
      # down including location, current replacement cost, and percentage of the 
      # replacement cost covered by the insurer (80% to 100% are typical ranges). 
      # Ideally the end user will know the cost of home owners insurance in terms
      # of the cost of the home.
      # 
      sliderInput(inputId = "insurance_slider",
                  label = "Homeowners insurance rate per $100 of home price",
                  min = 0, 
                  max = 4, 
                  value = 1,
                  step = 0.1,
                  post = " %"), # Adds the '%' sign to the displayed value
      width = 3
    ),

    mainPanel(
#      layout_columns(
#        card("Card 1"),
#        card("Card 2"),
#        card("Card 3")
#      ),
      #fluidRow(
      #  column(
      #    width = 6,
      #    plotOutput("nominal_payment")
      #  ),
      #  column(
      #    width = 6,
      #    plotOutput("real_payment")
      #  )
      #)
      #plotOutput("nominal_interest")
    )
  )  
)

# Define server logic required 
server <- function(input, output) {

  # Payment data 
  #payment_data <- reactive({
  #  create_payment_schedule(p = input$home_price_slider,
  #                          r = 0.01 * input$interest_rate_slider, 
  #                          i = 0.01 * input$inflation_rate_slider,
  #                          a = 0.01 * input$appreciation_rate_slider,
  #                          ptr = 0.01 * input$tax_rate_slider,
  #                          hir = 0.01 * input$insurance_slider, 
  #                          n = term)    
  #})
  
  # Upper limit for y-axis
  #nominal_limit <- reactive({
  #  payment_data() %>%
  #    mutate(nominal_total = rowSums(across(c(nominal_mortgage, 
  #                                            nominal_property_tax, 
  #                                            nominal_home_insurance)))) %>%
  #    filter(time == 30) %>% pull(nominal_total)
  #})
  
  #output$nominal_payment <- renderPlot({
    
    # Gather columns to be included in line chart for house payment. 
  #  nominal_payment <- payment_data() %>%
  #    select(time, nominal_mortgage, nominal_property_tax, nominal_home_insurance) %>%
  #    rename(
  #      Mortgage = nominal_mortgage, 
  #      Tax = nominal_property_tax,
  #      Insurance = nominal_home_insurance
  #    ) %>%
  #    pivot_longer(
  #      col = c(Mortgage, Tax, Insurance),
  #      names_to = "Payment",
  #      values_to = "Amount"
  #    )
    
  #  nominal_visual <- ggplot(
  #    data = nominal_payment,
  #    aes(x = time, y = Amount, fill = Payment)) + 
  #    geom_area(position = "stack", color = "white", linewidth = 0.2, alpha = 0.8) +
  #    labs(x = "Time (years)", y = "Amount (USD)", 
  #         title = "Annual Payment",
  #         subtitle = "Currency at time of payment") +
  #    scale_y_continuous(limits = c(0, nominal_limit())) +
  #    theme_light() + 
  #    theme(
  #      legend.position = "inside",
  #      legend.position.inside = c(0.20, 0.85) # Top-left interior corner
  #    ) 
    
  #  nominal_visual
    
  #})
  
  #output$real_payment <- renderPlot({

    # Gather columns to be included in line chart for house payment. 
  #  real_payment <- payment_data() %>%
  #    select(time, real_mortgage, real_property_tax, real_home_insurance) %>%
  #    rename(
  #      Mortgage = real_mortgage, 
  #      Tax = real_property_tax,
  #      Insurance = real_home_insurance
  #    ) %>%
  #    pivot_longer(
  #      col = c(Mortgage, Tax, Insurance),
  #      names_to = "Payment",
  #      values_to = "Amount"
  #    )
    
  #  real_visual <- ggplot(
  #    data = real_payment,
  #    aes(x = time, y = Amount, fill = Payment)) + 
  #    geom_area(position = "stack", color = "white", linewidth = 0.2, alpha = 0.8) +
  #    labs(x = "Time (years)", y = "Amount (USD)", 
  #         title = "Annual Payment",
  #         subtitle = "Adjusted to value at time of purchase") +
  #    scale_y_continuous(limits = c(0, nominal_limit())) +
  #    theme_light() + 
  #    theme(
  #      legend.position = "inside",
  #      legend.position.inside = c(0.20, 0.85) # Top-left interior corner
  #    ) 
    
  #  real_visual
    
  #})
  
  #output$nominal_interest <- renderPlot({
    
  #  interest <- payment_data() %>%
  #    select(time, nominal_principal, nominal_interest) %>%
  #    rename(
  #      Principal = nominal_principal, 
  #      Interest = nominal_interest, 
  #    ) %>%
  #    pivot_longer(
  #      col = c(Principal, Interest),
  #      names_to = "Payment",
  #      values_to = "Amount"
  #    )
    
  #  interest_visual <- ggplot(
  #    data = interest,
  #    aes(x = time, y = Amount, color = Payment)) + 
  #    geom_point() +
  #    labs(x = "Time (years)", y = "Amount (USD)", title = "Nominal Interest") +
  #    theme_minimal()
    
  #  interest_visual
    
  #})
  
  }

# Run the application 
shinyApp(ui = ui, server = server)
