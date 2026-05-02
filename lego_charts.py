import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('sets.csv')

#remove rows missing MSRP or Current Price values
df_clean = df.dropna(subset=['USD_MSRP', 'Current_Price']).copy()
#calculate value change (profit or loss)
df_clean['Value_Change'] = df_clean['Current_Price'] - df_clean['USD_MSRP']
#calculate return on investment percentage
df_clean['ROI_Percent'] = (df_clean['Value_Change'] / df_clean['USD_MSRP']) * 100

df_ppp = df_clean.dropna(subset=['Pieces']).copy()
df_ppp = df_ppp[df_ppp['Pieces'] > 0]
df_ppp['PPP'] = df_ppp['USD_MSRP'] / df_ppp['Pieces']

df_rating = df_clean.dropna(subset=['Rating']).copy()

#check required columns exist before plotting
if 'Current_Price' in df.columns and 'Year' in df.columns:
    yearly_avg = df.groupby('Year')['Current_Price'].mean()
    #plot yearly average
    yearly_avg.plot(figsize=(10, 6))
    plt.title('LEGO Average Current Price Trends Over Time') #Chart title
    plt.xlabel('Year') #X-axis label
    plt.ylabel('Average Current Price (USD)') #Y-axis label
    plt.show() #display the plot

#calculate average ROI per theme
theme_stats = df_clean.groupby('Theme')['ROI_Percent'].mean().sort_values(ascending=False)
#select top 10 themes
top_10_themes = theme_stats.head(10)

#plot bar chart of theme ROI
plt.figure(figsize=(12, 6))
top_10_themes.plot(kind='bar', color='skyblue')
plt.title('Top 10 LEGO Themes by Average ROI %')#title
plt.xlabel('Theme')#X-axis label
plt.ylabel('Average Return on Investment (%)')#y-axis label
plt.xticks(rotation=45) #rotate labels for readability
plt.tight_layout()
plt.show()

yearly_ppp = df_ppp.groupby('Year')['PPP'].mean()
yearly_msrp = df_ppp.groupby('Year')['USD_MSRP'].mean()
yearly_pieces = df_ppp.groupby('Year')['Pieces'].mean()

#goes throgh and looks at the different decades, and their rate of return in terms of percentages
df_clean['Decade'] = (df_clean['Year'] // 10) * 10
decade_roi = df_clean.groupby('Decade')['ROI_Percent'].mean()

plt.style.use('ggplot')
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

axes[0, 0].plot(yearly_ppp.index, yearly_ppp.values, color='green')
axes[0, 0].set_title('Avg Price-Per-Piece Over Time (PPP)')
axes[0, 0].set_ylabel('Cost per Piece ($)')
axes[0, 0].set_xlabel('Year')

ax2 = axes[0, 1].twinx()
axes[0, 1].plot(yearly_msrp.index, yearly_msrp.values, color='blue', label='Avg MSRP ($)')
ax2.plot(yearly_pieces.index, yearly_pieces.values, color='orange', label='Avg Piece Count')
axes[0, 1].set_title('Avg Set Price vs. Avg Piece Count')
axes[0, 1].set_ylabel('MSRP in USD', color='blue')
ax2.set_ylabel('Number of Pieces', color='orange')

decade_roi_filtered = decade_roi[decade_roi.index >= 1980]
axes[1, 0].bar(decade_roi_filtered.index.astype(str), decade_roi_filtered.values, color='purple')
axes[1, 0].set_title('Average Market ROI by Decade')
axes[1, 0].set_ylabel('Return on Investment (%)')
axes[1, 0].set_xlabel('Decade')

df_scatter = df_rating[df_rating['ROI_Percent'] <= 2000] 
axes[1, 1].scatter(df_scatter['Rating'], df_scatter['ROI_Percent'], alpha=0.3, color='red')
axes[1, 1].set_title('Does a Higher Rating Mean a Higher ROI?')
axes[1, 1].set_ylabel('ROI (%)')
axes[1, 1].set_xlabel('User Rating')

plt.tight_layout()
plt.show()
