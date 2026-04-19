import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import time

df = pd.read_csv('sets.csv')
if 'Current_Price' in df.columns and 'Year' in df.columns:
    yearly_avg = df.groupby('Year')['Current_Price'].mean()
    yearly_avg.plot(figsize=(10, 6))
    plt.title('LEGO Average Current Price Trends Over Time')
    plt.xlabel('Year')
    plt.ylabel('Average Current Price (USD)')
    plt.show()
print(f"\nHighest priced set: ${df['Current_Price'].max()}")
print(f"Lowest priced set: ${df['Current_Price'].min()}")
print(f"Average price: ${df['Current_Price'].mean():.2f}")
df_clean = df.dropna(subset=['USD_MSRP', 'Current_Price']).copy()
df_clean['Value_Change'] = df_clean['Current_Price'] - df_clean['USD_MSRP']
df_clean['ROI_Percent'] = (df_clean['Value_Change'] / df_clean['USD_MSRP']) * 100
most_appreciated = df_clean.sort_values(by='Value_Change', ascending=False)
most_depreciated = df_clean.sort_values(by='Value_Change', ascending=True)
columns_to_print = ['Name', 'Theme', 'USD_MSRP', 'Current_Price', 'Value_Change', 'ROI_Percent']
print("\n" + "="*50)

#top 5 most appreciated
print("TOP 5 MOST APPRECIATED LEGO SETS (By Dollar Amount)")
print("="*50)
print(most_appreciated[columns_to_print].head(5).to_string(index=False))

#top themes
print("\n" + "="*80)
print("TOP 10 MOST PROFITABLE THEMES (By Average % ROI)")
print("="*80)
theme_stats = df_clean.groupby('Theme')['ROI_Percent'].mean().sort_values(ascending=False)
top_10_themes = theme_stats.head(10)
print(top_10_themes.to_string())
plt.figure(figsize=(12, 6))
top_10_themes.plot(kind='bar', color='skyblue')
plt.title('Top 10 LEGO Themes by Average ROI %')
plt.xlabel('Theme')
plt.ylabel('Average Return on Investment (%)')
plt.xticks(rotation=45)
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







API_KEY = '3-MFJx-H0V0-sjn4a'
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

df_lego = get_lego_data_range(2000, 2026)

df_lego.drop_duplicates(subset=['setID'], inplace=True)
df_lego.reset_index(drop=True, inplace=True)

print(f'\nSuccess! Total unique sets: {len(df_lego)}')
display(df_lego.head())
