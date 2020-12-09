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
def make_figure(results, offset=True):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=[z['month']/12 for z in results], 
                            y=[z['principle'] for z in results],
                    hovertemplate = '%{x:.1f} years<br>\nPrinciple: %{y:$,.0f}<extra></extra>',
                    mode='lines+markers',
                    name='Principle remaining'))
    fig.add_trace(go.Scatter(x=[z['month']/12 for z in results], 
                            y=[z['interest_paid'] for z in results],
                    hovertemplate = '%{x:.1f} years<br>\nInterest: %{y:$,.0f}<extra></extra>',
                    mode='lines+markers',
                    name='Interest paid'))
    if offset:
        fig.add_trace(go.Scatter(x=[z['month']/12 for z in results], 
                            y=[z['offset'] for z in results],
                    mode='lines+markers',
                    hovertemplate = '%{x:.1f} years<br>\nOffset: %{y:$,.0f}<extra></extra>',
                    name='Offset account balance'))

    fig.update_layout(
        width=1100, height=600,
                xaxis_title="Years",
    yaxis_title="Loan value",
    font = {"size": 14},
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.6
    ),
    # hovermode="x unified" ,
        # font_family="Courier New",
        # font_color="blue",
        # title_font_family="Times New Roman",
        # title_font_color="red",
        # legend_title_font_color="green"
    )

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
            break    
            

@st.cache
def scenario2(rate, principle, income=0, start_cash=0, expenses=2500, reserve=1500, offset=True):
    loan = Loan(principle, rate, 30*12)
    if offset:
        loan.offset = start_cash
    results = []
    for m in range(12*30):
        payment = income - expenses - reserve
        if offset:
            loan.offset += reserve
        i = loan.make_payment(payment)
        results.append({"month": m, "principle": loan.principle, "interest_paid": loan.interest_paid, "offset": loan.offset})
        if loan.principle <= 0 or loan.principle <= loan.offset:
            break    
    return results

@st.cache
def load_stamps():
    return pd.read_csv("stamps.csv")

# @st.cache
def calc_stamp_duty(state, house_cost):
    duty = 0
    info = ""
    stamps = load_stamps()
    stamps = stamps[stamps.state == state]
    for i, row in stamps.iterrows():
        if house_cost < row['max']:
            duty = row['constant'] + .01*row['percent']*(house_cost-row['subtract'])
    if state == "Vic" and house_cost < 1000000:
        duty *= 0.75
        info = "discount applied"
    return int(duty), info


def nope():
    duty = 0
    message = ""
    if state == "Vic":
        if house_cost < 1000000:
            duty = int(0.75 * (0.055 * house_cost))
            message = "discount applied"
        else:
            duty = int((0.055 * house_cost))
    elif state == "NSW":
        if house_cost < 1033000:
            duty = int(9285 + .045*(house_cost - 310000))
        else:
            duty = (41820 + .055*(house_cost - 1033000))

    else:
        duty = .04*house_cost
        message = "Not real value"

    return int(duty), message

st.title('Mortgage calculator')

st.sidebar.markdown("## House and loan")
house_cost = st.sidebar.slider('Cost of house', value=1000000, min_value=300000, max_value=2000000, step=5000)
state = st.sidebar.selectbox("State:", ["ACT", "Vic", "NSW", "Tas", "Qld", "WA", "SA", "NT"], index=1)
stamp_duty, info = calc_stamp_duty(state, house_cost)
star= "" if len(info) == 0 else "*"
st.sidebar.markdown(f"Stamp duty: ${stamp_duty:,}{star}")
cash = st.sidebar.number_input('Total cash', value=200000, step=5000)
borrow = st.sidebar.slider("Amount to borrow", value=house_cost + stamp_duty - cash, min_value=500000, max_value=house_cost, step=10000)
cash_left = cash - house_cost - stamp_duty + borrow 
lvr = borrow/house_cost
st.sidebar.markdown(f"Cash left: ${cash_left:,}  --  LVR: {lvr*100:.1f}%")
rate = st.sidebar.slider("Interest rate", value=2.6, min_value=2.0, max_value=5.0, step=.1)
term = st.sidebar.radio("Term", [20, 25, 30], index=2)
offset = st.sidebar.radio("Offset", ['Yes', 'No'], index=0)

if len(info) > 0:
   st.sidebar.markdown(f"*{info}")

loan = Loan(borrow, rate, term*12)
income = st.number_input("Monthly net income", value=9000, step=500)
expenses = st.number_input("Monthly expenses", value=2500, step=100)
st.markdown(f"Min. monthly payment: **${int(loan.payment_monthly):,}**")
reserve = st.slider("Reserve cash (monthly) - goes into offset account if available", min_value=0, max_value=int(income-expenses-loan.payment_monthly), step=500)

results = scenario2(rate, borrow, income=income, start_cash=cash_left, expenses=expenses, reserve=reserve, offset=(offset=="Yes"))
st.markdown(f"### Paid off in {len(results)/12:.1f} years. Total interest paid: ${int(results[-1]['interest_paid']):,}")
fig = make_figure(results, offset=(offset=="Yes"))

st.plotly_chart(fig)






