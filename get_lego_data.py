#Import required libraries
import requests
import os
load_dotenv()


#Setup for getting the data from BrickSet API
API_KEY = os.getenv('BRICKSET_API_KEY')
BASE_URL = 'https://brickset.com/api/v3.asmx'

def fetch_page(query_params):
    payload = {'apiKey': API_KEY, 'userHash': '', 
               'params': json.dumps(query_params)}
    
    try:
        # Update Base URL to use the getSets method by BrickSet
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
    """
    Flattens the complex JSON response into a list of simplified dictionaries.
    Specifically extracts nested US retail pricing for market analysis.
    """
    extracted_data = []
    for s in raw_sets:
        # Navigate nested dicts safely to avoid NoneType errors
        legocom = s.get('LEGOCom', {}) or {}
        us_details = legocom.get('US', {}) or {}
        row = {
            # Identification & Taxonomy
            'setID': s.get('setID'),
            'number': s.get('number'),
            'numberVariant': s.get('numberVariant'),
            'name': s.get('name'),
            'year': s.get('year'),
            'theme': s.get('theme'),
            'subtheme': s.get('subtheme'),
            'themeGroup': s.get('themeGroup'),
            'category': s.get('category'),
            
            # Pricing & Physical Specs
            'US_retailPrice': us_details.get('retailPrice'),
            'pieces': s.get('pieces'),
            'weight_kg': s.get('weight'),
            'availability': s.get('availability'),
            
            # Community Metrics
            'rating': s.get('rating'),
            'reviewCount': s.get('reviewCount')
        }
        extracted_data.append(row)
    return extracted_data

def get_lego_data_range(start_year, end_year):
    """
    Main loop to iterate through years and handle pagination for large datasets.
    Implements rate limiting to respect API guidelines.
    """
    all_final_data = []
    
    for year in range(start_year, end_year + 1):
        print(f'Fetching {year}...', end=' ')
        page = 1
        year_sets = []
        
        while True:
            # Set query parameters for current page
            params = {'year': str(year), 'pageSize': 500,
                      'pageNumber': page, 'extendedData': '1'}
            
            result = fetch_page(params)

            if not result or not result.get('sets'):
                break

            # Process batch and add to current year list
            batch = process_sets(result['sets'])
            year_sets.extend(batch)
            
            if len(year_sets) >= result.get('matches', 0) or len(result['sets']) < 500:
                break
            
            page += 1
            time.sleep(0.7)
            
        print(f'found {len(year_sets)} sets.')
        all_final_data.extend(year_sets)

    # Return as a Pandas DataFrame for easy cleaning and SQL insertion
    return pd.DataFrame(all_final_data)
