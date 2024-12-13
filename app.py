import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Define allowed usernames and passwords
USER_CREDENTIALS = {
    "cardpromag": "password123",
    "pancakeanalytics": "Deadpool2411!",
    "admin": "adminpass"
}

# Login function
def login():
    st.title("CardPro TCG Index Analysis Dashboard")
    st.write("### Please log in to access the dashboard")
    
    # Login form
    username = st.text_input("User ID")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    # Check credentials
    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.success(f"Welcome, {username}!")
            return True
        else:
            st.error("Invalid User ID or Password. Please try again.")
            return False

# Show the login form and check authentication
if login():
    # Main Streamlit app content starts here
    st.title("CardPro TCG Index Analysis Dashboard")

    # Load data from the website
    file_url = "https://pancakebreakfaststats.com/wp-content/uploads/2024/12/data_file_cp.xlsx"

    @st.cache_data
    def load_data(file_path):
        df = pd.read_excel(file_path, sheet_name=0)
        # Rename columns
        df.rename(columns={
            'console-name': 'TCG Set',
            'product-name': 'TCG Product Name'
        }, inplace=True)
        return df

    # Load the data
    try:
        df = load_data(file_url)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    # Display maximum update date
    max_update_date = df['update date'].max()
    st.markdown(f"**Data is updated through: {max_update_date.strftime('%B %d, %Y')}**")

    # Define the individual indexes
    indexes = [
        "Pokemon Price High",
        "Pokemon Cluster Index",
        "Pokemon Volume High Index",
        "MTG Volume High Index",
        "MTG Price High",
        "MTG Cluster Index",
        "YuGioh Cluster Index",
        "YuGioh Volume High Index",
        "YuGioh Price High Index"
    ]

    # Individual Index Analysis
    st.subheader("Individual Index Analysis")
    for index in indexes:
        st.subheader(f"Analysis for {index}")
        
        # Filter data for the current index
        if 'Index' in df.columns:  # Check if the column exists
            index_data = df[df['Index'] == index]
            
            if not index_data.empty:
                # **Data Visualization with Labels**
                # Bar graph: Sum of `current`, `last`, and `percent change`
                current_sum = index_data['current'].sum()
                last_sum = index_data['last'].sum()
                avg_percent_change = index_data['percent change'].mean()
                
                fig, ax = plt.subplots()
                bars = ax.bar(['Current', 'Last', 'Percent Change'], 
                              [current_sum, last_sum, avg_percent_change], 
                              color=['blue', 'orange', 'green'])
                ax.set_title(f"Analysis for {index}")
                ax.set_ylabel('Values')

                # Add data labels
                for bar in bars:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
                            f"{bar.get_height():,.2f}",
                            ha='center', va='bottom', fontsize=10)
                st.pyplot(fig)
                
                # **Table for Value Change and Percent Change**
                st.write("Value Change and Percent Change")
                st.table(index_data[['TCG Product Name', 'value change', 'percent change']])
                
                # **Top 3 Products by Positive and Negative Value Change (With Percent Change)**
                st.write("### Top 3 Products by Value Change")
                top_positive = index_data.nlargest(3, 'value change')
                top_negative = index_data.nsmallest(3, 'value change')
                
                st.write("#### Top 3 Positive Value Change (With Percent Change)")
                st.table(top_positive[['TCG Product Name', 'value change', 'percent change']])
                
                st.write("#### Top 3 Negative Value Change (With Percent Change)")
                st.table(top_negative[['TCG Product Name', 'value change', 'percent change']])
                
                # **Analysis Write-Up**
                st.write(f"""
                The analysis for the **{index}** reveals the following insights:
                - The total current value is **{current_sum:,.2f}**, while the total last value is **{last_sum:,.2f}**.
                - The average percent change is **{avg_percent_change:.2f}%**, providing an overall sense of the index's performance.
                - The top three products driving positive value changes are highlighted in the table above, along with their percent changes.
                - The bottom three products (negative value changes) show areas of potential concern or decline.
                """)
            else:
                st.write(f"No data available for {index}")
        else:
            st.error("The 'Index' column is missing in the DataFrame.")

    # Analysis Grouped by Brand
    st.subheader("Analysis Grouped by Brand: MTG, Pokemon, and Yu-Gi-Oh")
    brand_mapping = {
        "MTG": ["MTG Cluster Index", "MTG Price High", "MTG Volume High Index"],
        "Pokemon": ["Pokemon Cluster Index", "Pokemon Price High", "Pokemon Volume High Index"],
        "YuGioh": ["YuGioh Cluster Index", "YuGioh Price High Index", "YuGioh Volume High Index"]
    }
    df['TCG Brand'] = df['Index'].apply(
        lambda x: next((brand for brand, indexes in brand_mapping.items() if x in indexes), None)
    )
    brand_summary = df.groupby('TCG Brand', as_index=False).agg({
        'current': 'sum',
        'last': 'sum',
        'percent change': 'mean'
    })
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(brand_summary))
    bar_width = 0.25
    current_bars = ax.bar([p - bar_width for p in x], brand_summary['current'], bar_width, label='Current', color='blue')
    last_bars = ax.bar(x, brand_summary['last'], bar_width, label='Last', color='orange')
    percent_bars = ax.bar([p + bar_width for p in x], brand_summary['percent change'], bar_width, label='Percent Change', color='green')
    ax.set_xticks(x)
    ax.set_xticklabels(brand_summary['TCG Brand'])
    ax.legend()
    st.pyplot(fig)

    # Analysis Write-Up
    st.write("""
    ### Analysis Grouped by Brand
    The grouped analysis for MTG, Pokemon, and Yu-Gi-Oh reveals the following key insights:
    """)
    for _, row in brand_summary.iterrows():
        st.write(f"""
        - **{row['TCG Brand']}**:
          - Total Current Value: **{row['current']:,.2f}**
          - Total Last Value: **{row['last']:,.2f}**
          - Average Percent Change: **{row['percent change']:.2f}%**
        """)

    # About Me Section
    st.subheader("About Pancake Analytics LLC")
    st.write("""
    Pancake Analytics LLC is a data-driven consultancy that specializes in bringing advanced analytics to the collectibles space.
    Founded in 2019, Pancake Analytics empowers collectors, hobbyists, and businesses with actionable insights to make better-informed decisions. 
    From trading cards to comics, we leverage cutting-edge tools and methodologies to provide clear and comprehensive analysis.

    Whether it's tracking trends, forecasting market shifts, or creating tools like the CardPro TCG Index Analysis Dashboard, 
    our mission is to simplify complex data and help the collectibles community thrive. 
    If you'd like to learn more or have a custom project in mind, feel free to reach out!
    """)

else:
    st.stop()
