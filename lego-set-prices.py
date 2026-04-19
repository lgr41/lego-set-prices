import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import time
import os

load_dotenv()

df = pd.read_csv('sets.csv')
#check required columns exist before plotting
if 'Current_Price' in df.columns and 'Year' in df.columns:
    yearly_avg = df.groupby('Year')['Current_Price'].mean()
    #plot yearly average
    yearly_avg.plot(figsize=(10, 6))
    plt.title('LEGO Average Current Price Trends Over Time') #Chart title
    plt.xlabel('Year') #X-axis label
    plt.ylabel('Average Current Price (USD)') #Y-axis label
    plt.show() #display the plot
print(f"\nHighest priced set: ${df['Current_Price'].max()}") #maximum price
print(f"Lowest priced set: ${df['Current_Price'].min()}")#minimum price
print(f"Average price: ${df['Current_Price'].mean():.2f}")#mean price
#remove rows missing MSRP or Current Price values
df_clean = df.dropna(subset=['USD_MSRP', 'Current_Price']).copy()
#calculate value change (profit or loss)
df_clean['Value_Change'] = df_clean['Current_Price'] - df_clean['USD_MSRP']
#calculate return on investment percentage
df_clean['ROI_Percent'] = (df_clean['Value_Change'] / df_clean['USD_MSRP']) * 100
most_appreciated = df_clean.sort_values(by='Value_Change', ascending=False)#sort sets by highest appreciation
most_depreciated = df_clean.sort_values(by='Value_Change', ascending=True)#sort sets by highest depreciation
columns_to_print = ['Name', 'Theme', 'USD_MSRP', 'Current_Price', 'Value_Change', 'ROI_Percent']#columns we want displayed in outputs
print("\n" + "="*50)

#top 5 most appreciated
print("TOP 5 MOST APPRECIATED LEGO SETS (By Dollar Amount)")
print("="*50)
#display top 5 sets with largest price increases
print(most_appreciated[columns_to_print].head(5).to_string(index=False))

#top themes
print("\n" + "="*80)
print("TOP 10 MOST PROFITABLE THEMES (By Average % ROI)")
print("="*80)
#calculate average ROI per theme
theme_stats = df_clean.groupby('Theme')['ROI_Percent'].mean().sort_values(ascending=False)
#select top 10 themes
top_10_themes = theme_stats.head(10)
#print results
print(top_10_themes.to_string())
#plot bar chart of theme ROI
plt.figure(figsize=(12, 6))
top_10_themes.plot(kind='bar', color='skyblue')
plt.title('Top 10 LEGO Themes by Average ROI %')#title
plt.xlabel('Theme')#X-axis label
plt.ylabel('Average Return on Investment (%)')#y-axis label
plt.xticks(rotation=45) #rotate labels for readability
plt.tight_layout()
plt.show()
target_themes = ['Advanced Models', 'Minecraft', 'Harry Potter', 'Star Wars', 'Lord of the Rings', 'Indiana Jones']
for theme in target_themes:
    theme_df = df_clean[df_clean['Theme'].str.contains(theme, case=False, na=False)]
    if not theme_df.empty:
        most_app = theme_df.sort_values(by='Value_Change', ascending=False)
        most_dep = theme_df.sort_values(by='Value_Change', ascending=True)
        print("\n" + "= 70")
        print(f"THEME: {theme.upper()}")
        print("=70")
        print(f"\nMOST APPRECIATED {theme.upper()} SETS:")
        print(most_app[columns_to_print].head(5).to_string(index=False))
        print(f"\nLEAST APPRECIATED {theme.upper()} SETS:")
        print(most_dep[columns_to_print].head(5).to_string(index=False))

#last 10 years appreciate
print("\n" + "="*80)
print("TOP 5 PERFORMERS FROM THE LAST 10 YEARS (Released 2013-2023)")
print("="*80)
last_10_years = df_clean[df_clean['Year'] >= 2013]
top_recent = last_10_years.sort_values(by='ROI_Percent', ascending=False)
print(top_recent[columns_to_print].head(5).to_string(index=False))

#top 5 depreciated print("\n" + "="*80)
print("TOP 5 MOST DEPRECIATED LEGO SETS (Loss in Value)")
print("="*80)
most_depreciated = df_clean.sort_values(by='Value_Change', ascending=True)
print(most_depreciated[columns_to_print].head(5).to_string(index=False))


df = pd.read_csv('sets.csv')

df_clean = df.dropna(subset=['USD_MSRP', 'Current_Price']).copy()

df_clean['Value_Change'] = df_clean['Current_Price'] - df_clean['USD_MSRP']
df_clean['ROI_Percent'] = (df_clean['Value_Change'] / df_clean['USD_MSRP']) * 100

df_ppp = df_clean.dropna(subset=['Pieces']).copy()
df_ppp = df_ppp[df_ppp['Pieces'] > 0]
df_ppp['PPP'] = df_ppp['USD_MSRP'] / df_ppp['Pieces']

print("\n" + "="*50)
print("POINT 1: THE 'IP TAX' (Licensed vs Original)")
print("="*50)
#this looks at licensed vs orignal ideas by lego and their prices
licensed_themes = 'Star Wars|Harry Potter|Marvel|DC|Lord of the Rings|Indiana Jones|Disney|Jurassic'
original_themes = 'City|Creator|Ninjago|Technic|Friends|Castle|Space|Bionicle'

df_licensed = df_ppp[df_ppp['Theme'].str.contains(licensed_themes, case=False, na=False, regex=True)]
df_original = df_ppp[df_ppp['Theme'].str.contains(original_themes, case=False, na=False, regex=True)]

print(f"Licensed Themes - Avg Price/Piece: ${df_licensed['PPP'].mean():.2f}")
print(f"Licensed Themes - Avg ROI: {df_licensed['ROI_Percent'].mean():.2f}%\n")

print(f"Original Themes - Avg Price/Piece: ${df_original['PPP'].mean():.2f}")
print(f"Original Themes - Avg ROI: {df_original['ROI_Percent'].mean():.2f}%")

print("\n" + "="*50)
print("POINT 2: THE MINIFIGURE PREMIUM")
print("="*50)

df_minifigs = df_clean.dropna(subset=['Minifigures']).copy()

correlation = df_minifigs['Minifigures'].corr(df_minifigs['ROI_Percent'])
print(f"Correlation between Minifigure Count and ROI: {correlation:.4f}")
print("(A positive number means more minifigures = higher return on investment)\n")

small_sets = df_minifigs[(df_minifigs['Pieces'] < 150) & (df_minifigs['Minifigures'] >= 3)]
top_small_sets = small_sets.sort_values(by='ROI_Percent', ascending=False).head(3)

print("Top Appreciating Small Sets (Driven by Minifigures):")
columns_mini = ['Name', 'Theme', 'Pieces', 'Minifigures', 'USD_MSRP', 'Current_Price', 'ROI_Percent']
print(top_small_sets[columns_mini].to_string(index=False))

print("\n" + "="*50)
print("POINT 3: HISTORICAL PRICE-PER-PIECE (Check the charts!)")
print("="*50)

yearly_ppp = df_ppp.groupby('Year')['PPP'].mean()
yearly_msrp = df_ppp.groupby('Year')['USD_MSRP'].mean()
yearly_pieces = df_ppp.groupby('Year')['Pieces'].mean()

print(f"Avg Price-Per-Piece in 1990: ${yearly_ppp.get(1990, 0):.2f}")
print(f"Avg Price-Per-Piece in 2005: ${yearly_ppp.get(2005, 0):.2f}")
print(f"Avg Price-Per-Piece in 2020: ${yearly_ppp.get(2020, 0):.2f}")

print("\n" + "="*50)
print("POINT 4: ROI BY DECADE")
print("="*50)

df_clean['Decade'] = (df_clean['Year'] // 10) * 10
decade_roi = df_clean.groupby('Decade')['ROI_Percent'].mean()

for decade, roi in decade_roi.items():
    if int(decade) >= 1980:
        print(f"{int(decade)}s Average ROI: {roi:.2f}%")

print("\n" + "="*50)
print("POINT 5: RATING VS. FINANCIAL RETURN")
print("="*50)

df_rating = df_clean.dropna(subset=['Rating']).copy()
rating_corr = df_rating['Rating'].corr(df_rating['ROI_Percent'])

print(f"Correlation between Set Rating and ROI: {rating_corr:.4f}")
print("If this is near 0, it means set quality/reviews don't drive secondary market value—scarcity and IPs do!")

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





API_KEY = os.getenv('BRICKSET_API_KEY')
BASE_URL = 'https://brickset.com/api/v3.asmx'

def fetch_page(query_params):
    payload = {'apiKey': API_KEY, 'userHash': '', 
               'params': json.dumps(query_params)
    }
    
    try:
        response = requests.post((BASE_URL + '/getSets'), data=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data
            else:
                print(f'API Error: {data.get('message')}')
        else:
            print(f'HTTP Error: {response.status_code}')
            
    except Exception as e:
        print(f'Connection Error: {e}')
    return None

def process_sets(raw_sets):
    extracted_data = []
    for s in raw_sets:
        legocom = s.get('LEGOCom', {}) or {}
        us_details = legocom.get('US', {}) or {}
        row = {
            'setID': s.get('setID'),
            'number': s.get('number'),
            'numberVariant': s.get('numberVariant'),
            'name': s.get('name'),
            'year': s.get('year'),
            'theme': s.get('theme'),
            'subtheme': s.get('subtheme'),
            'themeGroup': s.get('themeGroup'),
            'category': s.get('category'),
            'US_retailPrice': us_details.get('retailPrice'),
            'pieces': s.get('pieces'),
            'weight_kg': s.get('weight'),
            'availability': s.get('availability'),
            'rating': s.get('rating'),
            'reviewCount': s.get('reviewCount')
        }
        extracted_data.append(row)
    return extracted_data

def get_lego_data_range(start_year, end_year):
    all_final_data = []
    
    for year in range(start_year, end_year + 1):
        print(f'Fetching {year}...', end=' ')
        page = 1
        year_sets = []
        
        while True:
            params = {'year': str(year), 'pageSize': 500,
                      'pageNumber': page, 'extendedData': '1'}
            
            result = fetch_page(params)
            
            if not result or not result.get('sets'):
                break
                
            batch = process_sets(result['sets'])
            year_sets.extend(batch)
            
            if len(year_sets) >= result.get('matches', 0) or len(result['sets']) < 500:
                break
            
            page += 1
            time.sleep(0.7)


        
            
        print(f'found {len(year_sets)} sets.')
        all_final_data.extend(year_sets)
            
    return pd.DataFrame(all_final_data)
