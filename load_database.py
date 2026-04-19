import sqlite3
import pandas as pd
from lego_set_prices import get_lego_data_range

def initialize_database():
    # Fetch and Prep Data
    print("Fetching LEGO data from Brickset...")
    df_lego = get_lego_data_range(2015, 2026)
    
    if df_lego is None or df_lego.empty:
        print("No data retrieved. This might be due to the API limit.")
        return

    # Clean duplicates before SQL insertion
    df_lego.drop_duplicates(subset=['setID'], inplace=True)
    df_lego.reset_index(drop=True, inplace=True)

    # Database Creation
    conn = None
    try:
        conn = sqlite3.connect('legos.db')
        cursor = conn.cursor()

        # Resetting the table for a fresh start
        cursor.execute("DROP TABLE IF EXISTS legos")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS legos (
            setID INTEGER PRIMARY KEY,
            number VARCHAR(20),
            numberVariant SMALLINT,
            name TEXT,
            year SMALLINT,
            theme VARCHAR(100),
            subtheme VARCHAR(100),
            themeGroup VARCHAR(50),
            category VARCHAR(50),
            msrp_usd FLOAT,
            pieces INTEGER,
            weight_kg FLOAT,
            availability VARCHAR(50),
            rating FLOAT,
            reviewCount INTEGER
        );""")
        
        # Create rows using .get() to avoid KeyErrors if columns are missing
        rows = [(
            r.get('setID'), r.get('number'), r.get('numberVariant'), r.get('name'), r.get('year'),
            r.get('theme'), r.get('subtheme'), r.get('themeGroup'), r.get('category'),
            r.get('US_retailPrice'), r.get('pieces'), r.get('weight_kg'), r.get('availability'), 
            r.get('rating'), r.get('reviewCount')
        ) for r in df_lego.to_dict('records')]
        
        cursor.executemany("""
            INSERT INTO legos 
            (setID, number, numberVariant, name, year, 
            theme, subtheme, themeGroup, category, msrp_usd, 
            pieces, weight_kg, availability, rating, reviewCount) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            ON CONFLICT(setID) DO NOTHING;
        """, rows)

        conn.commit()
        print(f"Database 'legos.db' initialized successfully with {len(rows)} sets!")

    # Catch any errors that may arise
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
