import streamlit as st
from datetime import datetime
import pandas as pd

def calculate_monthly_savings(initial_savings, payments, start_date):
    total_savings_needed = sum(payment["amount"] for payment in payments) - initial_savings
    total_months = (payments[-1]["date"] - start_date).days // 30
    monthly_savings = total_savings_needed / total_months
    return monthly_savings, total_months

def tax_saving_tool():
    st.header('Tax Savings Plan Calculator')
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    if st.session_state.page == 1:
        st.header('Step 1: Current Savings and Payments')
        initial_savings = st.number_input('Initial Savings (£)', value=35000.0)
        
        today = datetime.today()
        current_year = today.year

        payments = []
        if today <= datetime(current_year, 1, 31):
            payment1_amount = st.number_input('Tax Payment (January 31st) (£)', value=0.0)
            payments.append({"date": datetime(current_year, 1, 31), "amount": payment1_amount})
            payment2_amount = st.number_input('1st Payment on Account (January 31st) (£)', value=0.0)
            payments.append({"date": datetime(current_year, 1, 31), "amount": payment2_amount})
        if today <= datetime(current_year, 7, 31):
            payment3_amount = st.number_input('2nd Payment on Account (July 31st) (£)', value=0.0)
            payments.append({"date": datetime(current_year, 7, 31), "amount": payment3_amount})

        if st.button('Next'):
            st.session_state.initial_savings = initial_savings
            st.session_state.payments = payments
            st.session_state.page = 2
            st.experimental_rerun()
    
    if st.session_state.page == 2:
        st.header('Step 2: Next Year\'s Tax Figures')
        
        next_year = datetime.today().year + 1
        payment1_amount = st.number_input('Tax Payment (January 31st) for next year (£)', value=0.0)
        payment2_amount = st.number_input('1st Payment on Account (January 31st) for next year (£)', value=0.0)
        payment3_amount = st.number_input('2nd Payment on Account (July 31st) for next year (£)', value=0.0)
        
        next_year_payments = [
            {"date": datetime(next_year, 1, 31), "amount": payment1_amount},
            {"date": datetime(next_year, 1, 31), "amount": payment2_amount},
            {"date": datetime(next_year, 7, 31), "amount": payment3_amount}
        ]
        
        if st.button('Calculate Savings Plan'):
            st.session_state.next_year_payments = next_year_payments
            st.session_state.page = 3
            st.experimental_rerun()
    
    if st.session_state.page == 3:
        st.header('Savings Plan')
        
        today = datetime.today()
        payments = st.session_state.payments + st.session_state.next_year_payments
        initial_savings = st.session_state.initial_savings
        
        monthly_savings, total_months = calculate_monthly_savings(initial_savings, payments, today)
        dates = pd.date_range(start=today, periods=total_months, freq='M')
        savings_plan = pd.DataFrame({"Date": dates, "Monthly Savings Needed": monthly_savings})
        savings_plan["Cumulative Savings"] = savings_plan["Monthly Savings Needed"].cumsum() + initial_savings

        for payment in payments:
            savings_plan.loc[savings_plan["Date"] >= payment["date"], "Cumulative Savings"] -= payment["amount"]

        st.write(savings_plan)
        
        if st.button('Start Over'):
            st.session_state.page = 1
            st.experimental_rerun()

def income_tax_predictor():
    st.header('Income Tax Predictor')
    
    salary = st.number_input('Annual Salary (£)', value=0.0)
    dividends = st.number_input('Annual Dividends (£)', value=0.0)
    
    if st.button('Calculate Tax Savings'):
        total_income = salary + dividends
        
        # Simplified tax calculation
        tax_free_allowance = 12500
        basic_rate_limit = 50000
        higher_rate_limit = 150000
        
        basic_rate = 0.20
        higher_rate = 0.40
        additional_rate = 0.45
        
        if total_income <= tax_free_allowance:
            tax_due = 0
        elif total_income <= basic_rate_limit:
            tax_due = (total_income - tax_free_allowance) * basic_rate
        elif total_income <= higher_rate_limit:
            tax_due = (basic_rate_limit - tax_free_allowance) * basic_rate + (total_income - basic_rate_limit) * higher_rate
        else:
            tax_due = (basic_rate_limit - tax_free_allowance) * basic_rate + (higher_rate_limit - basic_rate_limit) * higher_rate + (total_income - higher_rate_limit) * additional_rate
        
        st.write(f'Estimated Tax Due: £{tax_due:.2f}')
        st.write(f'You should put aside approximately £{tax_due / total_income * 100:.2f}% of your income for tax savings.')

def main():
    st.title('Tax Savings and Estimation Tools')
    
    option = st.selectbox('Select a tool:', ('Home', 'Tax Saving Tool', 'Income Tax Predictor'))
    
    if option == 'Tax Saving Tool':
        tax_saving_tool()
    elif option == 'Income Tax Predictor':
        income_tax_predictor()
    else:
        st.write('Select a tool from the dropdown above.')

if __name__ == '__main__':
    main()