import streamlit as st
import pandas as pd
import plotly.express as px

# Initialize or load data

def load_data():
    try:
        df = pd.read_csv("expenses.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Category", "Item", "Amount"])
    return df

def save_data(df):
    df.to_csv("expenses.csv", index=False)

# Title and Sidebar Settings
st.set_page_config(page_title="KEEP A TRACK", layout="wide")
st.title("KEEP A TRACK")
st.sidebar.header("Settings")

# Income and Expense Input Section
st.sidebar.subheader("Input Your Income and Expenses")
income = st.sidebar.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)

expense_date = st.sidebar.date_input("Expense Date", pd.Timestamp.now().date())
expense_category = st.sidebar.selectbox("Expense Category", ["Food", "Entertainment", "Bills", "Transport", "Healthcare", "Other"])
expense_item = st.sidebar.text_input("Expense Item")
expense_amount = st.sidebar.number_input("Expense Amount (₹)", min_value=0.0, step=10.0)

if st.sidebar.button("Add Expense"):
    df = load_data()
    new_expense = pd.DataFrame({
        "Date": [expense_date],
        "Category": [expense_category],
        "Item": [expense_item],
        "Amount": [expense_amount]
    })
    df = pd.concat([df, new_expense], ignore_index=True)
    save_data(df)
    st.sidebar.success("Expense added successfully!")
    st.experimental_rerun()  

# Display Expense Table with Delete Option
st.sidebar.subheader("Expense Summary")
df = load_data()
delete_expense = st.sidebar.checkbox("Enable Delete", False)

if delete_expense:
    expenses_to_delete = st.sidebar.multiselect("Select Expenses to Delete", df.index)
    if st.sidebar.button("Delete Selected Expenses"):
        df = df.drop(index=expenses_to_delete)
        save_data(df)
        st.sidebar.success("Expense(s) deleted successfully!")
        st.experimental_rerun()  
st.sidebar.table(df)

# Visualization of Spending Trends
st.sidebar.subheader("Spending Trends")
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)  # Convert Period to string
    monthly_expense = df.groupby('Month')['Amount'].sum().reset_index()
    fig = px.line(monthly_expense, x='Month', y='Amount', title='Monthly Expense Trend')
    fig.update_traces(mode='lines+markers')
    st.sidebar.plotly_chart(fig)

# Category-Based Budgeting
st.sidebar.subheader("Category-Based Budgeting")
budget = {}
for category in df['Category'].unique():
    budget[category] = st.sidebar.number_input(f"Set Budget for {category} (₹)", min_value=0.0, step=500.0)

if st.sidebar.button("Show Budget Analysis"):
    category_expense = df.groupby('Category')['Amount'].sum().reset_index()
    budget_df = pd.DataFrame.from_dict(budget, orient='index', columns=['Budget'])
    budget_df['Spent'] = budget_df.index.map(category_expense.set_index('Category')['Amount']).fillna(0)
    budget_df['Difference'] = budget_df['Budget'] - budget_df['Spent']
    
    fig = px.bar(budget_df, x=budget_df.index, y=['Spent', 'Budget'], barmode='group', title='Category Budget Analysis')
    fig.update_layout(yaxis_title='Amount (₹)', legend_title='Legend', xaxis_title='Category')
    st.sidebar.plotly_chart(fig)

# Goal Setting and Tracking
st.sidebar.subheader("Set Your Financial Goals")
goal = st.sidebar.text_input("Enter your financial goal (e.g., Save ₹1000)")
goal_amount = st.sidebar.number_input("Goal Amount (₹)", min_value=0.0, step=1000.0)
if st.sidebar.button("Set Goal"):
    st.session_state['goal'] = goal
    st.session_state['goal_amount'] = goal_amount
    st.sidebar.success("Goal set successfully!")

if 'goal' in st.session_state:
    st.sidebar.write(f"Your goal: {st.session_state['goal']}")
    st.sidebar.write(f"Goal amount: ₹{st.session_state['goal_amount']:.2f}")
    total_savings = income - df['Amount'].sum()
    st.sidebar.write(f"Current savings: ₹{total_savings:.2f}")
    if total_savings >= st.session_state['goal_amount']:
        st.sidebar.success("Congratulations! You've reached your goal.")
    else:
        st.sidebar.write(f"You need ₹{st.session_state['goal_amount'] - total_savings:.2f} more to reach your goal.")

# Main Content Section
st.header("Welcome to Your Personal Expense Tracker")

# Expense Insights
st.subheader("Expense Insights")
if not df.empty:
    most_expensive_item = df.loc[df['Amount'].idxmax()]
    st.write(f"Most expensive item: {most_expensive_item['Item']} (₹{most_expensive_item['Amount']:.2f})")
    category_expense = df.groupby('Category')['Amount'].sum().reset_index()
    st.write(f"Category with highest spending: {category_expense.loc[category_expense['Amount'].idxmax(), 'Category']} (₹{category_expense['Amount'].max():.2f})")

# Alerts and Notifications
st.subheader("Alerts and Notifications")
if st.button("Check for Alerts"):
    for category, budget_amount in budget.items():
        if category in category_expense['Category'].values and category_expense.loc[category_expense['Category'] == category, 'Amount'].iloc[0] > budget_amount:
            st.warning(f"Over budget in {category}: Spent ₹{category_expense.loc[category_expense['Category'] == category, 'Amount'].iloc[0]:.2f}, Budget ₹{budget_amount:.2f}")

# Footer
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.info(
    "This app is a simple Personal Expense Tracker. "
    "It allows you to track your monthly expenses, set budgets, monitor your financial goals and alert when expenses overshoot."
)


# Author's details
st.sidebar.markdown("### Developed By:")
st.sidebar.markdown("[Subhi Arjaria](https://github.com/subhiarjaria18)")