#!/usr/bin/env python3
"""
Test script to verify the fix for the Series formatting error
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

def flatten_columns(data):
    """
    Flatten hierarchical column names from yfinance data.
    Converts columns like ('Close', 'MSFT') to 'Close'
    Also removes the first row of data after flattening
    """
    if isinstance(data.columns, pd.MultiIndex):
        # Flatten multi-level columns by taking the first level (the metric name)
        data.columns = data.columns.get_level_values(0)
        data.columns.name = None
        data.index.name = "Date"
    # Remove the first row of data
    #if len(data) > 0:
    #data = data.iloc[1:].reset_index(drop=True)
    
    return data

def extract_scalar(value):
    """Extract scalar value from pandas Series or scalar"""
    if hasattr(value, 'iloc') and len(value) > 0:
        return value.iloc[0]
    elif hasattr(value, 'values') and len(value.values) > 0:
        return value.values[0]
    elif hasattr(value, 'item'):
        return value.item()
    else:
        return value

def process_data(data):
    """Process data like in the main script"""
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('US/Eastern')
    data.reset_index(inplace=True)
    
    # Handle potential hierarchical column names after reset_index
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # Rename the date column to Datetime
    if 'Date' in data.columns:
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
    elif data.columns[0] == 'Date':  # In case the first column is the date
        data.rename(columns={data.columns[0]: 'Datetime'}, inplace=True)
    
    return data

def test_column_flattening():
    """Test the column flattening function"""
    print("Testing column flattening function...")
    
    try:
        # Try multiple symbols in case some are having issues
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        data = None
        
        for symbol in symbols:
            try:
                print(f"Trying to fetch {symbol} data...")
                end_date = datetime.now()
                start_date = end_date - timedelta(days=5)  # Use 5 days for more reliable data
                
                data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
                
                if not data.empty:
                    print(f"✅ Successfully retrieved {symbol} data: {data.shape}")
                    break
                else:
                    print(f"❌ No data for {symbol}")
                    
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {e}")
                continue
        
        if data is None or data.empty:
            print("❌ Could not retrieve any data from any symbol")
            return False
            
        print(f"Original columns: {list(data.columns)}")
        print(f"Column type: {type(data.columns)}")
        
        # Show first few rows to see the hierarchical structure
        print("\nFirst 3 rows of original data:")
        print(data.head(3))
        
        # Flatten the columns
        data_flattened = flatten_columns(data.copy())
        print(f"\nFlattened columns: {list(data_flattened.columns)}")
        
        # Show first few rows after flattening
        print("\nFirst 3 rows after flattening:")
        print(data_flattened.head(3))
        
        # Test that we can access columns by simple names
        try:
            close_data = data_flattened['Close']
            open_data = data_flattened['Open']
            high_data = data_flattened['High']
            low_data = data_flattened['Low']
            volume_data = data_flattened['Volume']
            
            print(f"\n✅ Successfully accessed columns:")
            print(f"  Close: {len(close_data)} values")
            print(f"  Open: {len(open_data)} values")
            print(f"  High: {len(high_data)} values")
            print(f"  Low: {len(low_data)} values")
            print(f"  Volume: {len(volume_data)} values")
            
            return True
            
        except KeyError as e:
            print(f"❌ Failed to access column: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fix():
    """Test the fix with stock data"""
    print("Testing the fix for Series formatting error...")
    
    try:
        # Try multiple symbols in case some are having issues
        symbols = ['GOOGL']
        data = None
        
        for symbol in symbols:
            try:
                print(f"Trying to fetch {symbol} data...")
                end_date = datetime.now()
                start_date = end_date - timedelta(days=5)  # Use 5 days for more reliable data
                
                data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
                
                if not data.empty:
                    print(f"✅ Successfully retrieved {symbol} data: {data.shape}")
                    break
                else:
                    print(f"❌ No data for {symbol}")
                    
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {e}")
                continue
        
        if data is None or data.empty:
            print("❌ Could not retrieve any data from any symbol")
            return False
            
        print(f"✅ Data retrieved: {data.shape}")
        
        # Flatten columns first
        data = flatten_columns(data)
        print(f"✅ Columns flattened")
        
        # Process data
        data = process_data(data)
        print(f"✅ Data processed: {data.shape}")
        print(f"Final column names: {list(data.columns)}")
        print(f"Column types: {[type(col) for col in data.columns]}")
        
        # Check for any remaining hierarchical columns
        if any(isinstance(col, tuple) for col in data.columns):
            print("❌ Still has hierarchical columns!")
            return False
        
        # Test the problematic operations
        last_price = extract_scalar(data['Close'].iloc[-1])
        first_open = extract_scalar(data['Open'].iloc[0])
        change = last_price - first_open
        pct_change = (change / first_open) * 100
        
        print(f"Values extracted:")
        print(f"  last_price: {last_price} (type: {type(last_price)})")
        print(f"  first_open: {first_open} (type: {type(first_open)})")
        print(f"  change: {change} (type: {type(change)})")
        print(f"  pct_change: {pct_change} (type: {type(pct_change)})")
        
        # Test formatting (this was failing before)
        try:
            formatted_price = f"{last_price:.2f} USD"
            formatted_change = f"{change:.2f} ({pct_change:.2f}%)"
            print(f"✅ Formatting successful:")
            print(f"  Price: {formatted_price}")
            print(f"  Change: {formatted_change}")
            return True
        except Exception as e:
            print(f"❌ Formatting still fails: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING COLUMN FLATTENING FUNCTION")
    print("=" * 60)
    
    flattening_success = test_column_flattening()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE FIX")
    print("=" * 60)
    
    fix_success = test_fix()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if flattening_success and fix_success:
        print("🎉 Both tests passed! The column flattening function works correctly.")
        print("✅ The dashboard should now work without the hierarchical column issues.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        if not flattening_success:
            print("  - Column flattening test failed")
        if not fix_success:
            print("  - Complete fix test failed")
