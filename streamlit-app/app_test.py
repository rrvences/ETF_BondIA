import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Data
table_maturity_1 = {
    'Under 1 Year': '0.1%', '1 - 5 Years': '41.1', '5 - 10 Years': '30.7',
    '10 - 15 Years': '10.0', '15 - 20 Years': '7.3', '20 - 25 Years': '3.6%',
    'Over 25 Years': '7.1'
}



table_maturity_2 = {
    'Cash and Derivatives': '-0.05', '0 - 1 Years': '1.36', '1 - 2 Years': '9.81',
    '2 - 3 Years': '10.88', '3 - 5 Years': '18.61', '5 - 7 Years': '13.12',
    '7 - 10 Years': '17.13', '10 - 15 Years': '10.23', '15 - 20 Years': '8.91',
    '20+ Years': '10.99'
}


table_sector_1 = {'Treasury': '100.05', 'Cash': '-0.05'}

table_sector_2 = {'Treasury': '99.9%', 'Cash': '0.1'}

table_rating_1 = {'Cash and/or Derivatives': '-0.05', 'AAA': '22.88', 'AA': '35.46', 'A': '18.49', 'BBB': '23.22'}

table_rating_2 = {'AAA': '22.8%', 'AA': '35.7', 'A': '17.8', 'BBB': '21.1', 'Not Rated': '2.5'}

table_market_1 = {'France': '23.7%', 'Italy': '22.2', 'Germany': '18.5', 'Spain': '14.3', 'Belgium': '5.2', 'Netherlands': '4.1%', 'Austria': '3.7', 'Portugal': '1.8', 'Finland': '1.6', 'Ireland': '1.5'}

table_market_2 = {'FRANCE (REPUBLIC OF)': '23.52%', 'ITALY (REPUBLIC OF)': '22.12%', 'GERMANY (FEDERAL REPUBLIC OF)': '18.57%', 'SPAIN (KINGDOM OF)': '14.35%', 'BELGIUM KINGDOM OF (GOVERNMENT)': '5.16%', 'NETHERLANDS (KINGDOM OF)': '4.10%', 'AUSTRIA (REPUBLIC OF)': '3.64%', 'PORTUGAL (REPUBLIC OF)': '1.95%', 'FINLAND (REPUBLIC OF)': '1.62%', 'IRELAND (GOVERNMENT)': '1.52%', 'Total of Portfolio': '96.55%'}


def clean_keys(table):
    table = {key.split(" ")[0].capitalize(): value for key, value in table.items() 
             if "Total" not in key and 'Derivatives' not in key}

    return table



def clean_tables(table_1, table_2, element):

    # Convert to DataFrame
    df1 = pd.DataFrame(list(table_1.items()), columns=[element, 'Value 1'])
    df2 = pd.DataFrame(list(table_2.items()), columns=[element, 'Value 2'])

    # Convert values to numeric
    df1['Value 1'] = df1['Value 1'].replace('%', '', regex=True).astype(float)
    df2['Value 2'] = df2['Value 2'].replace('%', '', regex=True).astype(float)

    df_merged = pd.merge(df1, df2, on=element, how='outer').fillna(0)
    return df1, df2, df_merged

# Streamlit App
# st.title("Maturity Tables Comparison")

# col1, col2 = st.columns(2)
# with col1:
#     st.write("### Table Maturity 1")
#     st.dataframe(df1)
# with col2:
#     st.write("### Table Maturity 2")
#     st.dataframe(df2)

# Title
st.title(":dart: ETF Bonds Comparison")

# Introduction
st.markdown("""
Welcome to the **ETF Bonds** page — your guide to understanding how Exchange-Traded Funds (ETFs) can be used to invest in bonds. 
ETF bonds combine the benefits of **bond investing** with the **flexibility of ETFs**, making it easier and more accessible to investors seeking exposure to the bond market.
""")

# **What Are ETF Bonds?**
st.markdown("""
            
    ###        :moneybag: **What are bonds?**
            
A **bond** is a type of loan. When you buy a bond, you're lending money to a **government**, **corporation**, or other entity in exchange for:

- **Regular interest payments** (called coupons)
- **Repayment of the full amount** at the end of the bond's term (called maturity)

Bonds are considered **fixed income investments** because they typically offer steady, predictable returns.


### 🧐 **What Are ETF Bonds?**

**ETF Bonds** (Exchange-Traded Funds for Bonds) are a type of **investment fund** that holds a **diversified portfolio of bonds** and is traded on a stock exchange. Just like stock ETFs, bond ETFs are bought and sold throughout the day, providing liquidity and flexibility.

Here’s what makes **ETF Bonds** attractive:
- **Diversification**: Bond ETFs hold a wide variety of bonds in their portfolio, allowing you to gain exposure to **different issuers**, **sectors**, and **maturity dates**. 
- **Liquidity**: Since ETF bonds trade on exchanges, you can **buy and sell** them like stocks, offering more liquidity compared to traditional bonds.
- **Low Fees**: Bond ETFs generally have **lower management fees** than actively managed bond funds, as they track an index of bonds.
- **Ease of Access**: Investors can gain bond exposure with as little as one share of an ETF, making it easier for small investors to access the bond market.
- **Income Generation**: Bond ETFs typically pay **interest income** (from the underlying bonds) to shareholders, distributed on a **monthly or quarterly basis**.

---

### 📈 **Why Invest in ETF Bonds?**

- **Diversified Bond Exposure**: Instead of buying individual bonds, bond ETFs allow you to invest in a broad **portfolio of bonds** in one single trade.
- **Flexibility and Liquidity**: Like stocks, you can buy and sell ETF bonds throughout the trading day, which gives you more control over your investment compared to traditional bonds that might require you to hold them to maturity.
- **Lower Risk**: Since bond ETFs invest in multiple bonds, they offer **greater diversification** compared to holding a single bond, which can help mitigate the impact of credit or interest rate risk.
- **Income Stream**: If you're looking for regular income, ETF bonds can offer **steady coupon payments**, which are passed on to ETF shareholders.

---

### 📅 **How Do ETF Bonds Work?**

- **Investment Strategy**: Bond ETFs typically track a **bond index**, such as the **Barclays Capital U.S. Aggregate Bond Index** or **J.P. Morgan Emerging Markets Bond Index**. These indexes represent a large portion of the bond market, giving ETF investors broad exposure.
  
- **Reinvestment**: The interest generated by the bonds in the ETF portfolio is typically **distributed to investors** in the form of **monthly or quarterly dividends**. 

- **Capital Appreciation**: In addition to interest income, bond ETFs may experience **capital appreciation** or depreciation, depending on changes in interest rates and the overall bond market.

---

### 🏦 **Types of ETF Bonds**

There are several types of bond ETFs, each with its own focus and investment strategy:

- **Treasury Bond ETFs**: These ETFs invest in government bonds, typically with very low risk and low yield. Examples: **iShares 20+ Year Treasury Bond ETF (TLT)**.
- **Corporate Bond ETFs**: These ETFs invest in bonds issued by corporations. They usually offer higher yields than government bonds but come with higher risk. Examples: **Vanguard Total Corporate Bond ETF (VTC)**.
- **High-Yield Bond ETFs**: These ETFs focus on bonds with lower credit ratings (junk bonds), offering higher yields but greater risk. Examples: **SPDR Bloomberg Barclays High Yield Bond ETF (JNK)**.
- **Municipal Bond ETFs**: These ETFs invest in bonds issued by state and local governments, often tax-exempt. Examples: **Vanguard Tax-Exempt Bond ETF (VTEB)**.
- **Emerging Markets Bond ETFs**: These ETFs invest in bonds from emerging markets and offer higher returns along with higher risk. Examples: **iShares J.P. Morgan EM Local Currency Bond ETF (LEMB)**.

---

### 💡 **Pros and Cons of ETF Bonds**

**Pros**:
- **Accessibility**: ETFs allow small investors to diversify their bond holdings without needing significant capital.
- **Liquidity**: Bond ETFs trade on the open market, allowing for **instant buy and sell orders** during market hours.
- **Cost-Efficiency**: Most bond ETFs have low expense ratios, making them a cost-effective way to invest in bonds.

**Cons**:
- **Interest Rate Risk**: Bond ETFs are still subject to **interest rate risk**, meaning if rates rise, bond prices (and the value of the ETF) may fall.
- **Credit Risk**: Some bond ETFs, especially those focused on high-yield or corporate bonds, can carry **credit risk** if the underlying bonds default.
- **Market Volatility**: While bond ETFs are generally less volatile than stocks, they can still experience price fluctuations based on market conditions.

---

### 📊 **ETF Bond Strategy**

When building your bond portfolio, consider mixing **Treasury Bond ETFs** for stability with **Corporate Bond ETFs** for higher yield. If you have a longer-term horizon, you might opt for **Long-Term Treasury ETFs** for price appreciation potential.

---

### 🚀 **Conclusion**

**ETF bonds** are an excellent way to gain diversified exposure to the bond market with the flexibility and liquidity of **ETFs**. They are a solid choice for both conservative and more aggressive investors, depending on the mix of bonds in the ETF.

By understanding how ETF bonds work, their different types, and their pros and cons, you can make informed decisions about whether they’re the right choice for your investment portfolio.
""")

# Function to toggle the visibility of info sections
def toggle_info(info_key):
    if info_key not in st.session_state:
        st.session_state[info_key] = False
    st.session_state[info_key] = not st.session_state[info_key]

st.markdown("""
    ### :information_source: More Info
""")

text=rf"""
:rain_cloud: **Accumulating** vs **Distributing** Funds"""

with st.expander(text, expanded=False):
    st.info("""
       **Accumulating Funds**:
- The income (interest/dividends) generated by the fund is automatically **reinvested** into the fund.
- This leads to **compounding growth**, ideal for long-term investors who seek growth over time.

**Distributing Funds**:
- The income generated by the fund is **paid out** to investors on a regular basis (e.g., monthly, quarterly).
- This is ideal for investors seeking **regular income** from their investments, such as retirees or income-focused investors.

#### Comparison at a Glance:

| Feature               | Accumulating Funds            | Distributing Funds         |
|-----------------------|--------------------------------|----------------------------|
| **Income Handling**    | Reinvests income automatically | Pays out income to investors |
| **Growth**             | Faster growth (compounding)    | Slower growth (income paid out) |
| **Investor Benefit**   | Capital growth over time       | Regular income, often for cash flow |
| **Suitable For**       | Long-term investors, growth-focused | Investors needing steady income (e.g., retirees) |

    """)
    
with st.expander(":money_with_wings: What is **Dividend Yield**?", expanded=False):
    st.info("""

The **Dividend Yield** of a Bond ETF is the annual income (interest payments) generated by the bonds held in the fund, expressed as a percentage of the ETF's current market price. It provides a way to measure the income you can expect from your investment in a Bond ETF, relative to its current price.

The yield can fluctuate based on several factors, including **interest rates**, **bond types**, and overall **market conditions**.

Here's how the Dividend Yield behaves in different market conditions:

| **Market Condition**         | **Behavior of Dividend Yield**                                         | **Key Impact on Investors**                                                                 |
|------------------------------|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Rising Interest Rates        | Yield increases as ETF price decreases.                                | Higher yield, but potential capital loss on ETF price.                                     |
| Falling Interest Rates       | Yield decreases as ETF price increases.                                | Lower yield, but potential capital gain on ETF price.                                      |
| Stable Interest Rates        | Stable yield reflecting market rates.                                  | Consistent income with less price volatility.                                               |
| High-Yield Bonds             | Higher yield due to risk, more volatility.                             | Higher potential income but higher risk and volatility.                                    |
| Corporate Bonds              | Variable yield depending on economic conditions.                       | Higher yield with more credit risk and market sensitivity.                                 |
| Inflation-Protected Bonds    | Yield increases as inflation rises.                                    | Higher yield during inflation periods with protection against inflation.                   |
""")

with st.expander(":warning: What happens during **inflation**, **deflation** & **volatile markets**?"):

    st.info("""
### 📉 **ETF Bonds in Different Market Conditions**

- **Inflation**:  
  In periods of inflation, bond prices typically **fall** as interest rates rise. Since most bond ETFs track broad indices of bonds, they may experience price declines during inflationary periods. However, **inflation-protected bond ETFs** (such as those that invest in **TIPS**—Treasury Inflation-Protected Securities) can perform better as they are specifically designed to adjust with inflation, offering some protection against rising prices.

- **Deflation**:  
  During deflation, when the economy is shrinking and prices are falling, bond prices usually **rise** as interest rates are often reduced to stimulate growth. Bond ETFs, especially those with long-duration bonds, may benefit in deflationary periods, as lower rates increase the value of existing bonds.

- **Volatile Markets**:  
  In volatile markets, ETF bond prices can fluctuate based on investor sentiment, interest rate changes, and economic conditions. **Corporate bond ETFs** might see more volatility compared to **government bond ETFs**, as corporate bonds carry more credit risk. **High-yield bond ETFs** are especially sensitive to market volatility, as their lower credit quality makes them more susceptible to economic downturns.


""")



# Maturity
df1, df2, df_merged = clean_tables(clean_keys(table_maturity_1), clean_keys(table_maturity_2), element='Maturity')
# Plot Comparison
st.write("### Maturity Distribution Comparison")
# Create a DataFrame for Bond ETF Maturity Stratification
df_maturity_info = {
    "Maturity Range": ["< 1 Year", "0 - 5 Years", "5 - 10 Years", "10 - 15 Years", "15 - 20 Years", "20+ Years"],
    "Yield": ["Very Low", "Low to Moderate", "Moderate", "Higher", "Very High", "Extremely High"],
    "Interest Rate Sensitivity": ["Very Low", "Low", "Moderate", "High", "Very High", "Extremely High"],
    "Duration": [
        "Ultra-short term",
        "Short term",
        "Medium term",
        "Long term",
        "Very long term",
        "Ultra-long term"
    ]
}
with st.expander("Maturity Stratification Info"):
    st.dataframe(df_maturity_info)

fig = px.bar(df_merged.melt(id_vars=['Maturity'], var_name='Table', value_name='Percentage'), 
             x='Maturity', y='Percentage', color='Table', barmode='group',
             title="Comparison of Maturity Distributions")
st.plotly_chart(fig)


# ### SECTOR
# df1, df2, df_merged = clean_tables(table_sector_1, table_sector_2, element='Sector')

# # Plot Sector Breakdown
# st.write("### Sector Breakdown Comparison")
# fig_sector = px.pie(df_merged.melt(id_vars=['Sector'], var_name='Table', value_name='Percentage'), 
#                     names='Sector', values='Percentage', color='Table',
#                     title="Comparison of Sector Breakdown")
# st.plotly_chart(fig_sector)


### RATING
df1, df2, df_merged = clean_tables(clean_keys(table_rating_1), clean_keys(table_rating_2), element='Rating')

# Plot Rating Breakdown
st.write("### Rating Breakdown Comparison")
fig_rating = px.bar(df_merged.melt(id_vars=['Rating'], var_name='Table', value_name='Percentage'), 
                    x='Rating', y='Percentage', color='Table', barmode='group',
                    title="Comparison of Rating Breakdown")

fig_rating.update_layout(barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)
st.plotly_chart(fig_rating)

### MARKET ALLOCATION
# Standardizing Country Names (Removing extra words for consistency)

df1, df2, df_market_merged = clean_tables(clean_keys(table_market_1), clean_keys(table_market_2), element='Country')
# Sort by first dataset for better comparison
df_market_merged = df_market_merged.sort_values(by="Value 1", ascending=False)

# Plot
st.write("### Market Allocation Comparison")
fig_market = px.bar(df_market_merged.melt(id_vars=['Country'], var_name='Table', value_name='Percentage'),
                    y='Country', x='Percentage', color='Table', barmode='group',
                    title="Comparison of Market Allocation",
                    orientation='h')  # Horizontal bars

st.plotly_chart(fig_market)


