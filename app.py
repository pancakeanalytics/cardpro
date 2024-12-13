import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("CardPro TCG Index Analysis Dashboard")

# Load data from the website
file_url = "https://pancakebreakfaststats.com/wp-content/uploads/2024/12/data_file_cp.xlsx"

@st.cache_data
def load_data(url):
    df = pd.read_excel(url, sheet_name=0)
    # Rename columns
    df.rename(columns={
        'console-name': 'TCG Set',
        'product-name': 'TCG Product Name'
    }, inplace=True)
    return df

# Load the data
df = load_data(file_url)

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


# Summary analysis across all indexes
st.subheader("Total Analysis Across All Indexes")
current_total = df['current'].sum()
last_total = df['last'].sum()

# Total bar graph with labels
fig, ax = plt.subplots()
bars = ax.bar(['Current Total', 'Last Total'], [current_total, last_total], color=['blue', 'orange'])
ax.set_title("Total Current and Last Across All Indexes")
ax.set_ylabel('Sum')

# Add data labels
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():,.2f}",
            ha='center', va='bottom', fontsize=10)
st.pyplot(fig)

# Bar chart: Percent Change by Index with labels
st.subheader("Percent Change by Index")
percent_change_by_Index = df.groupby('Index', as_index=False)['percent change'].mean()

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(percent_change_by_Index['Index'], percent_change_by_Index['percent change'], color='green')
ax.set_title("Average Percent Change by Index")
ax.set_ylabel("Percent Change")
ax.set_xlabel("Index")
ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for readability

# Add data labels
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.2f}%",
            ha='center', va='bottom', fontsize=10)
st.pyplot(fig)

# Section: Analysis Grouped by Brand
st.subheader("Analysis Grouped by Brand: MTG, Pokemon, and Yu-Gi-Oh")

# Define brand groupings
brand_mapping = {
    "MTG": ["MTG Cluster Index", "MTG Price High", "MTG Volume High Index"],
    "Pokemon": ["Pokemon Cluster Index", "Pokemon Price High", "Pokemon Volume High Index"],
    "YuGioh": ["YuGioh Cluster Index", "YuGioh Price High Index", "YuGioh Volume High Index"]
}

# Create a new column for TCG Brand based on the mapping
df['TCG Brand'] = df['Index'].apply(
    lambda x: next((brand for brand, indexes in brand_mapping.items() if x in indexes), None)
)

# Group data by TCG Brand and calculate totals and averages
brand_summary = df.groupby('TCG Brand', as_index=False).agg({
    'current': 'sum',
    'last': 'sum',
    'percent change': 'mean'  # Average percent change
})

# Bar Graph: Current, Last, and Percent Change by Brand
fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(brand_summary))  # Position for each brand
bar_width = 0.25

# Plot bars for Current, Last, and Percent Change
current_bars = ax.bar([p - bar_width for p in x], brand_summary['current'], bar_width, label='Current', color='blue')
last_bars = ax.bar(x, brand_summary['last'], bar_width, label='Last', color='orange')
percent_bars = ax.bar([p + bar_width for p in x], brand_summary['percent change'], bar_width, label='Percent Change', color='green')

# Add labels
ax.set_xticks(x)
ax.set_xticklabels(brand_summary['TCG Brand'])
ax.set_title("Current Value, Last Value, and Percent Change by Brand")
ax.set_ylabel("Value")
ax.legend()

# Add data labels
for bars in [current_bars, last_bars, percent_bars]:
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():,.2f}",
                ha='center', va='bottom', fontsize=10)

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
