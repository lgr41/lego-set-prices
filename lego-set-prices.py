import pandas as pd

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

print(f"\nHighest priced set: ${df['Current_Price'].max()}") #maximum price
print(f"Lowest priced set: ${df['Current_Price'].min()}")#minimum price
print(f"Average price: ${df['Current_Price'].mean():.2f}")#mean price

most_appreciated = df_clean.sort_values(by='Value_Change', ascending=False)#sort sets by highest appreciation
most_depreciated = df_clean.sort_values(by='Value_Change', ascending=True)#sort sets by highest depreciation
columns_to_print = ['Name', 'Theme', 'USD_MSRP', 'Current_Price', 'Value_Change', 'ROI_Percent']#columns we want displayed in outputs

#top 5 most appreciated
print("TOP 5 MOST APPRECIATED LEGO SETS (By Dollar Amount)")
#display top 5 sets with largest price increases
print(most_appreciated[columns_to_print].head(5).to_string(index=False))

#top themes
print("TOP 10 MOST PROFITABLE THEMES (By Average % ROI)")
#calculate average ROI per theme
theme_stats = df_clean.groupby('Theme')['ROI_Percent'].mean().sort_values(ascending=False)
#select top 10 themes
top_10_themes = theme_stats.head(10)
#print results
print(top_10_themes.to_string())

target_themes = ['Advanced Models', 'Minecraft', 'Harry Potter', 'Star Wars', 'Lord of the Rings', 'Indiana Jones']
for theme in target_themes:
    theme_df = df_clean[df_clean['Theme'].str.contains(theme, case=False, na=False)]
    if not theme_df.empty:
        most_app = theme_df.sort_values(by='Value_Change', ascending=False)
        most_dep = theme_df.sort_values(by='Value_Change', ascending=True)
        print("\n" + "=" * 70)
        print(f"THEME: {theme.upper()}")
        print("=" * 70)
        print(f"\nMOST APPRECIATED {theme.upper()} SETS:")
        print(most_app[columns_to_print].head(5).to_string(index=False))
        print(f"\nLEAST APPRECIATED {theme.upper()} SETS:")
        print(most_dep[columns_to_print].head(5).to_string(index=False))

#last 10 years appreciate
print("TOP 5 PERFORMERS FROM THE LAST 10 YEARS (Released 2013-2023)")
last_10_years = df_clean[df_clean['Year'] >= 2013]
top_recent = last_10_years.sort_values(by='ROI_Percent', ascending=False)
print(top_recent[columns_to_print].head(5).to_string(index=False))

#top 5 depreciated
print("TOP 5 MOST DEPRECIATED LEGO SETS (Loss in Value)")
most_depreciated = df_clean.sort_values(by='Value_Change', ascending=True)
print(most_depreciated[columns_to_print].head(5).to_string(index=False))

print("POINT 1: THE 'IP TAX' (Licensed vs Original)")
#this looks at licensed vs orignal ideas by lego and their prices
licensed_themes = 'Star Wars|Harry Potter|Marvel|DC|Lord of the Rings|Indiana Jones|Disney|Jurassic'
original_themes = 'City|Creator|Ninjago|Technic|Friends|Castle|Space|Bionicle'

df_licensed = df_ppp[df_ppp['Theme'].str.contains(licensed_themes, case=False, na=False, regex=True)]
df_original = df_ppp[df_ppp['Theme'].str.contains(original_themes, case=False, na=False, regex=True)]

print(f"Licensed Themes - Avg Price/Piece: ${df_licensed['PPP'].mean():.2f}")
print(f"Licensed Themes - Avg ROI: {df_licensed['ROI_Percent'].mean():.2f}%\n")

print(f"Original Themes - Avg Price/Piece: ${df_original['PPP'].mean():.2f}")
print(f"Original Themes - Avg ROI: {df_original['ROI_Percent'].mean():.2f}%")

print("POINT 2: THE MINIFIGURE PREMIUM")
#this code looks at minifures and their impact on the rate of return in a set's price overtime
df_minifigs = df_clean.dropna(subset=['Minifigures']).copy()

correlation = df_minifigs['Minifigures'].corr(df_minifigs['ROI_Percent'])
print(f"Correlation between Minifigure Count and ROI: {correlation:.4f}")
print("(A positive number means more minifigures = higher return on investment)\n")

small_sets = df_minifigs[(df_minifigs['Pieces'] < 150) & (df_minifigs['Minifigures'] >= 3)]
top_small_sets = small_sets.sort_values(by='ROI_Percent', ascending=False).head(3)

print("Top Appreciating Small Sets (Driven by Minifigures):")
columns_mini = ['Name', 'Theme', 'Pieces', 'Minifigures', 'USD_MSRP', 'Current_Price', 'ROI_Percent']
print(top_small_sets[columns_mini].to_string(index=False))

print("POINT 3: HISTORICAL PRICE-PER-PIECE (Check the charts!)")
#this looks at the price per piece over time, which is what PPP stands for.
#It compares the MSRP to the current day price of the set
yearly_ppp = df_ppp.groupby('Year')['PPP'].mean()

print(f"Avg Price-Per-Piece in 1990: ${yearly_ppp.get(1990, 0):.2f}")
print(f"Avg Price-Per-Piece in 2005: ${yearly_ppp.get(2005, 0):.2f}")
print(f"Avg Price-Per-Piece in 2020: ${yearly_ppp.get(2020, 0):.2f}")

print("POINT 4: ROI BY DECADE")
#goes throgh and looks at the different decades, and their rate of return in terms of percentages
df_clean['Decade'] = (df_clean['Year'] // 10) * 10
decade_roi = df_clean.groupby('Decade')['ROI_Percent'].mean()

for decade, roi in decade_roi.items():
    if int(decade) >= 1980:
        print(f"{int(decade)}s Average ROI: {roi:.2f}%")

print("POINT 5: RATING VS. FINANCIAL RETURN")
df_rating = df_clean.dropna(subset=['Rating']).copy()
rating_corr = df_rating['Rating'].corr(df_rating['ROI_Percent'])

print(f"Correlation between Set Rating and ROI: {rating_corr:.4f}")
print("If this is near 0, it means set quality/reviews don't drive secondary market value—scarcity and IPs do!")
