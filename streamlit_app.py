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
    
    today = datetime.today()
    current_year = today.year
    start_of_financial_year = datetime(current_year, 4, 6)
    if today < start_of_financial_year:
        start_of_financial_year = datetime(current_year - 1, 4, 6)
    months_elapsed = (today.year - start_of_financial_year.year) * 12 + today.month - start_of_financial_year.month + 1
    
    salary_taken = st.number_input('Total Salary Taken to Date (£)', value=0.0)
    dividends_taken = st.number_input('Total Dividends Taken to Date (£)', value=0.0)
    salary_this_month = st.number_input('Salary Expected This Month (£)', value=0.0)
    dividends_this_month = st.number_input('Dividends Expected This Month (£)', value=0.0)
    savings_to_date = st.number_input('Savings for Tax to Date (£)', value=0.0)
    
    if st.button('Calculate Tax Savings'):
        total_salary_estimated = salary_taken + salary_this_month * (12 - months_elapsed)
        total_dividends_estimated = dividends_taken + dividends_this_month * (12 - months_elapsed)
        total_income_estimated = total_salary_estimated + total_dividends_estimated
        
        # Simplified tax calculation
        tax_free_allowance = 12500
        basic_rate_limit = 50000
        higher_rate_limit = 150000
        
        basic_rate = 0.20
        higher_rate = 0.40
        additional_rate = 0.45
        
        if total_income_estimated <= tax_free_allowance:
            tax_due = 0
        elif total_income_estimated <= basic_rate_limit:
            tax_due = (total_income_estimated - tax_free_allowance) * basic_rate
        elif total_income_estimated <= higher_rate_limit:
            tax_due = (basic_rate_limit - tax_free_allowance) * basic_rate + (total_income_estimated - basic_rate_limit) * higher_rate
        else:
            tax_due = (basic_rate_limit - tax_free_allowance) * basic_rate + (higher_rate_limit - basic_rate_limit) * higher_rate + (total_income_estimated - higher_rate_limit) * additional_rate
        
        st.write(f'Estimated Annual Salary: £{total_salary_estimated:.2f}')
        st.write(f'Estimated Annual Dividends: £{total_dividends_estimated:.2f}')
        st.write(f'Estimated Annual Income: £{total_income_estimated:.2f}')
        st.write(f'Estimated Tax Due: £{tax_due:.2f}')
        st.write(f'You should put aside approximately £{tax_due / total_income_estimated * 100:.2f}% of your income for tax savings.')
        
        remaining_months = 12 - months_elapsed
        savings_needed = tax_due - savings_to_date
        monthly_savings_needed = savings_needed / remaining_months
        
        st.write(f'To stay on track, you need to save approximately £{monthly_savings_needed:.2f} per month for the rest of the financial year.')

def ask_questions():
    st.header("Find Out Your Tax Saving Persona")
    
    questions = [
        "How often do you set aside money for taxes?",
        "How do you feel about your current tax preparation process?",
        "When do you start preparing for your tax payments?",
        "How knowledgeable are you about tax laws and regulations?",
        "Do you use any tools or services to help you with tax savings?"
    ]
    
    options = [
        ("a) I never set aside money.", 1),
        ("b) I set aside money sporadically.", 2),
        ("c) I set aside money regularly but without a clear plan.", 3),
        ("d) I set aside money regularly with a clear plan.", 4),
        ("e) I use sophisticated strategies to maximize my tax savings.", 5)
    ]
    
    scores = []
    for question in questions:
        st.subheader(question)
        choice = st.radio("", options, index=0, key=question)
        scores.append(choice[1])
    
    total_score = sum(scores)
    if total_score <= 7:
        persona = "The Rabbit"
    elif total_score <= 13:
        persona = "The Squirrel"
    elif total_score <= 19:
        persona = "The Ant"
    elif total_score <= 24:
        persona = "The Bee"
    else:
        persona = "The Owl"
    
    st.write(f"Your persona is: **{persona}**")

def main():
    st.title('Tax Savings and Estimation Tools')
    
    option = st.selectbox('Select a tool:', ('Home', 'Tax Saving Tool', 'Income Tax Predictor', 'Find Your Persona'))
    
    if option == 'Tax Saving Tool':
        tax_saving_tool()
    elif option == 'Income Tax Predictor':
        income_tax_predictor()
    elif option == 'Find Your Persona':
        ask_questions()
    else:
        st.write('Select a tool from the dropdown above.')

if __name__ == '__main__':
    main()