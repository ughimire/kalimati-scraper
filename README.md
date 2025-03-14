# Kalimati Market Scraper

A Python script to scrape commodity price data from the [Kalimati Market website](https://kalimatimarket.gov.np/) and save it to a JSON file with standardized English field names.

## Features

- Scrapes the commodityDailyPrice table from the Kalimati Market website
- Creates and maintains a product mapping file for Nepali to English translations
- Preserves product varieties and origins in the product names
- Properly extracts and standardizes unit types from Nepali to English
- Transforms Nepali headers to standardized English field names
- Extracts numeric values from price strings and removes currency symbols
- Identifies and categorizes unit types (kg, pcs, dozen, bundle, sack, crate)
- Handles Nepali language content with proper UTF-8 encoding
- Saves data in a well-formatted JSON file with timestamp
- Includes fallback mechanisms to find the table if the ID changes
- Containerized with Docker for easy deployment and isolation
- Automated daily runs with GitHub Actions at 12:00 PM Nepal time

## Requirements

### Option 1: Using Docker (Recommended)
- Docker
- Docker Compose (optional, but recommended)

### Option 2: Direct Installation
- Python 3.6 or higher
- Required packages: requests, beautifulsoup4

## Installation & Usage

### Using Docker (Recommended)

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd kalimati-market-scraper
   ```

2. Run the scraper using the provided shell script (easiest):
   ```bash
   ./run.sh
   ```
   
   This script will:
   - Check if Docker and Docker Compose are installed
   - Use Docker Compose if available, or fall back to Docker
   - Build the Docker image and run the container
   - Mount the data directory to save the scraped data

   **Alternatively, you can use Docker Compose directly:**
   ```bash
   docker-compose up
   ```

   **Or use Docker directly:**
   ```bash
   # Build the Docker image
   docker build -t kalimati-scraper .
   
   # Run the container
   docker run -v $(pwd)/data:/app/data kalimati-scraper
   ```

3. The scraped data will be saved to the `./data` directory on your host machine.

### Direct Installation

1. Clone this repository or download the script files
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script with Python:
   ```bash
   python kalimati_scraper.py
   ```

## Automated GitHub Workflow

This repository includes a GitHub Actions workflow that automatically:

1. Runs the scraper daily at 12:00 PM Nepal time (6:15 AM UTC)
2. Commits any new data files to the repository
3. Pushes the changes to GitHub

To use this feature:

1. Fork or clone this repository to your GitHub account
2. Enable GitHub Actions for your repository
3. The scraper will run automatically according to the schedule
4. You can also manually trigger the workflow from the Actions tab

### Manual Run with Git Commit

You can also run the scraper locally and commit the changes to GitHub using the provided script:

```bash
./run_and_commit.sh
```

This script will:
1. Run the scraper using Docker
2. Commit any new data files to your local Git repository
3. Ask if you want to push the changes to GitHub

## How It Works

The script will:
1. Scrape the commodityDailyPrice table from the Kalimati Market website
2. Extract product names and unit information from the raw data
3. Create or update a product mapping file (`product_mapping.json`) for Nepali to English translations
4. Transform the Nepali headers to standardized English field names
5. Extract numeric values from price strings and remove currency symbols
6. Identify and standardize unit types from Nepali to English
7. Create a 'data' directory if it doesn't exist
8. Save the transformed data to a JSON file in the 'data' directory with a timestamp in the filename

## Unit Mapping

The scraper automatically maps Nepali unit types to standardized English units:

| Nepali Unit | English Unit |
|-------------|--------------|
| के.जी., के.जी, केजी, के जी, किलो | kg |
| गोटा, पिस | pcs |
| दर्जन, दर्जन. | dozen |
| मुठा, बन्डल | bundle |
| बोरा | sack |
| क्रेट | crate |

## Output Files

### Market Data JSON

The script generates a JSON file with the following standardized format:

```json
[
    {
        "nepali_name": "गोलभेडा ठूलो(नेपाली)",
        "english_name": "Tomato Large (Nepali)",
        "minimum": 20,
        "maximum": 25,
        "average": 22.33,
        "unit_type": "kg",
        "unit_nepali": "के.जी.",
        "currency": "npr"
    },
    {
        "nepali_name": "सिताके च्याउ",
        "english_name": "Shiitake Mushroom",
        "minimum": 250,
        "maximum": 300,
        "average": 275,
        "unit_type": "kg",
        "unit_nepali": "के.जी.",
        "currency": "npr"
    }
]
```

Note: 
- The Nepali names preserve variety/origin information (e.g., "नेपाली" for Nepali, "भारतीय" for Indian)
- The unit information is extracted and standardized (e.g., "के.जी." → "kg")
- The original Nepali unit is preserved in the `unit_nepali` field
- English names will be empty until you fill in the mapping file
- All price values are converted to numeric format (without currency symbols)
- Currency is set to "npr" (Nepalese Rupee)

### Product Mapping JSON

The script also creates and maintains a product mapping file (`data/product_mapping.json`) with the following format:

```json
{
    "गोलभेडा ठूलो(नेपाली)": "Tomato Large (Nepali)",
    "गोलभेडा ठूलो(भारतीय)": "Tomato Large (Indian)",
    "आलु रातो": "Potato Red",
    "प्याज सुकेको": "Onion Dry",
    "सिताके च्याउ": "Shiitake Mushroom",
    ...
}
```

You can manually edit this file to add English translations for the Nepali product names. The scraper will:
1. Create this file on the first run with empty English translations
2. Add any new products found in subsequent runs
3. Preserve your manual translations between runs

## Customizing Product Translations

To add English translations for the products:

1. Run the scraper once to generate the initial `product_mapping.json` file
2. Edit the file to add English translations for each Nepali product name
3. Run the scraper again - it will use your translations in the output

Example of editing the mapping file:
```json
{
    "गोलभेडा ठूलो(नेपाली)": "Tomato Large (Nepali)",
    "गोलभेडा ठूलो(भारतीय)": "Tomato Large (Indian)",
    "आलु रातो": "Potato Red",
    "प्याज सुकेको": "Onion Dry",
    "सिताके च्याउ": "Shiitake Mushroom"
}
```

## Scheduling the Scraper

### Using GitHub Actions (Recommended)
The included GitHub Actions workflow will run the scraper daily at 12:00 PM Nepal time and commit the results.

### Using cron with Docker:
```bash
# Add to crontab (run every day at 8 AM)
0 8 * * * cd /path/to/kalimati-scraper && ./run.sh
```

### Using cron with Python directly:
```bash
# Add to crontab (run every day at 8 AM)
0 8 * * * cd /path/to/kalimati-scraper && python kalimati_scraper.py
```

## License

MIT 