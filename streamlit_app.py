import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import pandas as pd
from datetime import datetime
import os
import json

# Load Firebase credentials from environment variables
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials:
    cred = credentials.Certificate(json.loads(firebase_credentials))
    firebase_admin.initialize_app(cred)
else:
    st.error("Firebase credentials not found in environment variables")

# Function to calculate the monthly savings needed
def calculate_monthly_savings(initial_savings, payments, start_date):
    total_savings_needed = sum(payment["amount"] for payment in payments) - initial_savings
    total_months = (payments[-1]["date"] - start_date).days // 30
    monthly_savings = total_savings_needed / total_months
    return monthly_savings, total_months

# Main function to run the Streamlit app
def main():
    st.title('Tax Savings Plan Calculator')

    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.header("Welcome! Please register or log in.")
        auth_option = st.radio("Select an option", ["Register", "Log In"])

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if auth_option == "Register":
            if st.button("Register"):
                user_id = register_user(email, password)
                if user_id:
                    st.session_state.user = user_id
                    st.success("Registered successfully!")
                    st.experimental_rerun()
        else:
            if st.button("Log In"):
                user_id = authenticate_user(email, password)
                if user_id:
                    st.session_state.user = user_id
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
    else:
        st.header("Step 1: Current Savings and Payments")
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

if __name__ == '__main__':
    main()