#!/usr/bin/env python3
"""
Kalimati Market Scraper

This script scrapes the commodityDailyPrice table from the Kalimati Market website
and saves the data to a JSON file with standardized English field names.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import logging
import re
from datetime import datetime
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('kalimati_scraper')

# Define unit mappings from Nepali to English
UNIT_MAPPINGS = {
    'के.जी.': 'kg',
    'के.जी': 'kg',
    'केजी': 'kg',
    'के जी': 'kg',
    'किलो': 'kg',
    'गोटा': 'pcs',
    'पिस': 'pcs',
    'दर्जन': 'dozen',
    'दर्जन.': 'dozen',
    'मुठा': 'mutha',
    'बन्डल': 'bundle',
    'बोरा': 'sack',
    'क्रेट': 'crate'
}

def scrape_kalimati_market():
    """
    Scrape the commodityDailyPrice table from the Kalimati Market website.
    
    Returns:
        list: List of dictionaries containing the scraped data.
    """
    # URL of the Kalimati Market website
    url = "https://kalimatimarket.gov.np/"
    
    try:
        # Send a GET request to the website with a timeout
        logger.info(f"Fetching data from {url}")
        response = requests.get(url, timeout=30)
        
        # Check if the request was successful
        response.raise_for_status()
    except RequestException as e:
        logger.error(f"Failed to fetch the website: {e}")
        return []
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with id 'commodityDailyPrice'
    table = soup.find('table', id='commodityDailyPrice')
    
    # If table is not found, try finding it by class or other attributes
    if not table:
        logger.warning("Table with id 'commodityDailyPrice' not found. Trying alternative methods...")
        
        # Try to find tables and see if any contains price data
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        for i, t in enumerate(tables):
            # Look for tables that might contain price data
            if t.find('th') and any(keyword in t.text.lower() for keyword in ['commodity', 'price', 'कृषि उपज', 'मूल्य']):
                logger.info(f"Found potential price table at index {i}")
                table = t
                break
    
    if not table:
        logger.error("Could not find the commodityDailyPrice table.")
        return []
    
    logger.info("Successfully found the price table")
    
    # Extract table headers
    headers = []
    header_row = table.find('tr')
    if header_row:
        headers = [header.text.strip() for header in header_row.find_all(['th', 'td'])]
        logger.info(f"Extracted headers: {headers}")
    
    # Extract table data
    data = []
    rows = table.find_all('tr')[1:]  # Skip the header row
    logger.info(f"Found {len(rows)} data rows")
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if cells:
            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    # Clean the data - remove extra whitespace and newlines
                    value = cell.text.strip().replace('\n', ' ').replace('\r', '')
                    # Remove multiple spaces
                    while '  ' in value:
                        value = value.replace('  ', ' ')
                    row_data[headers[i]] = value
                else:
                    # Handle case where there might be more cells than headers
                    row_data[f"column_{i}"] = cell.text.strip()
            data.append(row_data)
    
    logger.info(f"Successfully extracted {len(data)} items")
    return data

def extract_product_info(item_text):
    """
    Extract product name and unit from the item text.
    
    Args:
        item_text (str): The raw item text from the website.
        
    Returns:
        tuple: (product_name, unit_type_nepali, unit_type_english)
    """
    # Clean up the item text
    clean_text = item_text.strip()
    
    # Default values
    product_name = clean_text
    unit_type_nepali = ""
    unit_type_english = "kg"  # Default unit
    
    # Try to extract the unit part (usually in parentheses at the end)
    unit_pattern = r'\(([^)]+)\)$'
    unit_match = re.search(unit_pattern, clean_text)
    
    if unit_match:
        unit_type_nepali = unit_match.group(1).strip()
        # Remove the unit part from the product name
        product_name = clean_text[:unit_match.start()].strip()
        
        # Map the Nepali unit to English
        unit_type_english = "kg"  # Default if not found
        for nepali_unit, english_unit in UNIT_MAPPINGS.items():
            if nepali_unit in unit_type_nepali:
                unit_type_english = english_unit
                break
    
    return product_name, unit_type_nepali, unit_type_english

def create_product_mapping(data):
    """
    Create or update a product mapping file for Nepali to English translations.
    
    Args:
        data (list): List of dictionaries containing the scraped data with Nepali headers.
        
    Returns:
        dict: Dictionary mapping Nepali product names to English translations.
    """
    mapping_file = os.path.join('data', 'product_mapping.json')
    product_mapping = {}
    
    # Check if mapping file already exists
    if os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                product_mapping = json.load(f)
            logger.info(f"Loaded existing product mapping with {len(product_mapping)} items")
        except Exception as e:
            logger.error(f"Failed to load existing product mapping: {e}")
    
    # Extract unique product names from the data
    new_products_added = 0
    unique_products = set()
    
    # First, collect all unique product names without the unit part
    for item in data:
        if 'कृषि उपज' in item:
            item_text = item['कृषि उपज']
            product_name, _, _ = extract_product_info(item_text)
            unique_products.add(product_name)
    
    logger.info(f"Found {len(unique_products)} unique products in the data")
    
    # Then add them to the mapping if not already present
    for product_name in unique_products:
        if product_name not in product_mapping:
            # Initialize with empty English translation
            product_mapping[product_name] = ""
            new_products_added += 1
            logger.debug(f"Added new product to mapping: {product_name}")
    
    # Save the updated mapping
    if new_products_added > 0:
        try:
            os.makedirs('data', exist_ok=True)
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(product_mapping, f, ensure_ascii=False, indent=4, sort_keys=True)
            logger.info(f"Updated product mapping with {new_products_added} new products")
        except Exception as e:
            logger.error(f"Failed to save product mapping: {e}")
    
    # Also save a debug file with raw product names for analysis
    try:
        debug_file = os.path.join('data', 'product_names_debug.json')
        raw_products = [item.get('कृषि उपज', '') for item in data if 'कृषि उपज' in item]
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(raw_products, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved raw product names to {debug_file} for debugging")
    except Exception as e:
        logger.error(f"Failed to save debug file: {e}")
    
    return product_mapping

def transform_data(data, product_mapping=None):
    """
    Transform the scraped data to standardized English format.
    
    Args:
        data (list): List of dictionaries containing the scraped data with Nepali headers.
        product_mapping (dict, optional): Dictionary mapping Nepali product names to English translations.
        
    Returns:
        list: List of dictionaries with standardized English headers and formatted values.
    """
    transformed_data = []
    
    # Define header mappings from Nepali to English
    header_mapping = {
        'कृषि उपज': 'item',
        'न्यूनतम': 'minimum',
        'अधिकतम': 'maximum',
        'औसत': 'average'
    }
    
    for item in data:
        transformed_item = {
            'nepali_name': '',
            'english_name': '',
            'minimum': 0,
            'maximum': 0,
            'average': 0,
            'unit_type': 'kg',
            'unit_nepali': '',
            'currency': 'npr'
        }
        
        # Extract item name and unit
        if 'कृषि उपज' in item:
            item_text = item['कृषि उपज']
            
            # Extract product name and unit
            product_name, unit_nepali, unit_english = extract_product_info(item_text)
            
            transformed_item['nepali_name'] = product_name
            transformed_item['unit_type'] = unit_english
            transformed_item['unit_nepali'] = unit_nepali
            
            # Add English name if available in the mapping
            if product_mapping and product_name in product_mapping and product_mapping[product_name]:
                transformed_item['english_name'] = product_mapping[product_name]
        
        # Extract and clean price values
        for nepali_key, english_key in header_mapping.items():
            if nepali_key in item and nepali_key != 'कृषि उपज':
                # Extract numeric value from the price string
                price_text = item[nepali_key]
                # Extract numbers from the price text (remove "रू" and other non-numeric characters)
                price_match = re.search(r'(\d+(?:\.\d+)?)', price_text.replace(',', ''))
                if price_match:
                    transformed_item[english_key] = float(price_match.group(1))
        
        transformed_data.append(transformed_item)
    
    logger.info(f"Transformed {len(transformed_data)} items to standardized format")
    return transformed_data

def save_to_json(data, filename=None):
    """
    Save the scraped data to a JSON file.
    
    Args:
        data (list): List of dictionaries containing the scraped data.
        filename (str, optional): Name of the JSON file. Defaults to None.
    
    Returns:
        str: Path to the saved JSON file.
    """
    if not filename:
        # Generate a filename with the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kalimati_market_data_{timestamp}.json"
    
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    file_path = os.path.join('data', filename)
    
    try:
        # Save the data to a JSON file with proper formatting and UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Data saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save data to {file_path}: {e}")
        return None

def main():
    """Main function to run the scraper."""
    logger.info("Starting Kalimati Market scraper...")
    
    try:
        # Scrape the raw data
        raw_data = scrape_kalimati_market()
        
        if raw_data:
            logger.info(f"Successfully scraped {len(raw_data)} items.")
            
            # Create or update product mapping
            product_mapping = create_product_mapping(raw_data)
            
            # Transform the data to standardized English format
            transformed_data = transform_data(raw_data, product_mapping)
            
            # Save the transformed data
            save_to_json(transformed_data)
        else:
            logger.warning("No data was scraped.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 