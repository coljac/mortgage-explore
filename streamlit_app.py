import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Loan(object):
    def __init__(self, principle, rate, term_months):
        self.principle = principle
        self.rate = rate
        self.term_months = term_months
        self.interest_paid = 0.0
        self.term_months = term_months
        self.time_left = term_months
        self.payment_monthly = self.payment()
        self.offset = 0
      
    def payment(self):
        return self.principle/d(self.rate, self.term_months)
    
    def current_interest(self):
        return self.rate/1200.0 * (self.principle - self.offset)
   
    def make_payment(self, amount):
        interest = self.current_interest()
        self.interest_paid += min(interest, amount)
        self.principle -= max(0, amount - interest)
        return interest

def d(r, n):
    r = r/1200.0
    return (np.power(1+r, n) -1)/(r*np.power(1+r, n))

@st.cache
def make_figure(results):
    # fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=[z['month']/12 for z in results], 
                            y=[z['principle'] for z in results],
                    mode='lines+markers',
                    name='principle remaining'))
    fig.add_trace(go.Scatter(x=[z['month']/12 for z in results], 
                            y=[z['interest_paid'] for z in results],
                    mode='lines+markers',
                    name='interest paid'))

    fig.add_trace(go.Scatter(x=[z['month']/12 for z in results], 
                            y=[z['offset'] for z in results],
                    mode='lines+markers',
                    name='offset'))

    return fig

@st.cache
def scenario(rate, principle, payment, cash_left=0, offset_average=0):
    loan = Loan(principle, rate, 30*12)
    loan.offset = offset_average
    results = []
    for m in range(12*30):
        i = loan.make_payment(payment)
        results.append([loan.principle, loan.interest_paid, i])
        if loan.principle <= 0:
            print(f"Paid off in {m/12:.1f} years. Total interest paid: ${loan.interest_paid:.0f}")
            break    
            

@st.cache
def scenario2(rate, principle, income=0, start_cash=0, expenses=2500, reserve=1500):
    loan = Loan(principle, rate, 30*12)
    loan.offset = start_cash
    results = []
    for m in range(12*30):
        payment = income - expenses - reserve
        loan.offset += reserve
        i = loan.make_payment(payment)
        results.append({"month": m, "principle": loan.principle, "interest_paid": loan.interest_paid, "offset": loan.offset})
        if loan.principle <= 0 or loan.principle <= loan.offset:
            break    
    return results

st.title('Mortgage calculator')

house_cost = st.sidebar.slider('Cost of house', value=1000000, min_value=900000, max_value=1200000, step=5000)
stamp_duty =int( 0.75 * 2870+(house_cost-130000)*0.06)

st.sidebar.text(f"Stamp duty: ${stamp_duty}")
cash = st.sidebar.number_input('Total cash', value=200000)
borrow = st.sidebar.slider("Amount to borrow", value=house_cost + stamp_duty - cash, min_value=500000, max_value=house_cost, step=10000)
cash_left = cash - house_cost - stamp_duty + borrow 
st.sidebar.text(f"Cash left: ${cash_left}")
rate = st.sidebar.slider("Interest rate", value=2.6, min_value=2.0, max_value=5.0, step=.1)
term = st.sidebar.radio("Term", [20, 25, 30], index=2)
offset = st.sidebar.radio("Offset", ['Yes', 'No'], index=0)

loan = Loan(borrow, rate, term*12)
income = st.number_input("Monthly net income", value=15000)
expenses = st.number_input("Monthly expenses", value=2500)
st.text(f"Min. payment: ${int(loan.payment_monthly)}")
reserve = st.slider("Reserve cash (monthly)", min_value=0, max_value=int(income-expenses-loan.payment_monthly), step=500)

results = scenario2(rate, borrow, income=income, start_cash=cash_left, expenses=expenses, reserve=reserve)
st.markdown(f"Paid off in {len(results)/12:.1f} years. Total interest paid: ${loan.interest_paid:.0f}")
fig = make_figure(results)

# st.sidebar.slider()

# wavelength_min = st.sidebar.slider("WL start", min_value=100, max_value=20000, value=1000)
# wavelength_max = st.sidebar.slider("WL end", min_value=100, max_value=50000, value=10000)

# show_lines = st.sidebar.checkbox("Show lines")
# spectrum =  st.sidebar.selectbox(
#     "Plot:",
#     ['Quiescent', 'Star-Forming', 'M-star', 'other']
# )

# filters = st.sidebar.multiselect(
#     "Filters", options=get_all_filters(), default=[], format_func=lambda x: str(x), key='filters'
# )
    
# fig = make_figure(load_spectrum(spectrum), filters)

st.plotly_chart(fig)






