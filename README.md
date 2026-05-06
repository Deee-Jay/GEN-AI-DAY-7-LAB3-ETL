# Retail ETL Pipeline

A beginner-friendly ETL pipeline for processing retail sales data using Python and pandas.

## Project Structure

```
├── main.py              # Main ETL pipeline script
├── test_pipeline.py     # Pytest test suite
├── orders.csv          # Sample input dataset
├── revenue.csv         # Output: Revenue by category
├── daily_sales.csv     # Output: Daily sales count
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Run the complete pipeline:
```bash
python main.py
```

### With Date Filtering
Run pipeline with date range:
```python
from main import run_pipeline

# Filter data between specific dates
run_pipeline(start_date="2024-01-20", end_date="2024-01-25")
```

## Pipeline Functions

### Core Functions
- `load_data(file_path)`: Load CSV data into pandas DataFrame
- `clean_data(df)`: Remove duplicates, handle missing values
- `transform_data(df, start_date, end_date)`: Create metrics and aggregations
- `save_data(df, path)`: Save DataFrame to CSV
- `run_pipeline()`: Orchestrate the complete ETL process

### Data Transformations
- **Total Calculation**: `total = price * quantity`
- **Revenue by Category**: Sum of totals grouped by category
- **Daily Sales Count**: Number of orders per day
- **Optimization**: Filter out rows with `price <= 0`

### Error Handling
- File not found errors during data loading
- Missing value handling (quantity → 1, price → 0)
- Comprehensive logging throughout the process

## Testing

Run the test suite:
```bash
python -m pytest test_pipeline.py -v
```

### Test Coverage
- ✅ Dataset loading validation
- ✅ Duplicate removal verification
- ✅ Missing value handling
- ✅ Total calculation accuracy
- ✅ Revenue aggregation correctness
- ✅ Daily sales counting
- ✅ Price filtering optimization
- ✅ Date filtering functionality
- ✅ File saving operations

## Input Data Format

The pipeline expects a CSV file with the following columns:
- `order_id`: Unique order identifier
- `customer_id`: Customer identifier
- `product`: Product name
- `category`: Product category
- `price`: Unit price
- `quantity`: Order quantity
- `order_date`: Order date (YYYY-MM-DD format)

## Output Files

1. **revenue.csv**: Category-wise revenue summary
   ```
   category,revenue
   Electronics,3219.90
   Clothing,939.87
   Home,2169.92
   ```

2. **daily_sales.csv**: Daily order counts
   ```
   date,sales_count
   2024-01-15,2
   2024-01-16,2
   ...
   ```

3. **transformed_orders.csv**: Full transformed dataset with total column

## Features

- **Beginner Friendly**: Simple, readable code with clear documentation
- **Modular Design**: Separate functions for each ETL step
- **Error Handling**: Robust error handling with informative messages
- **Logging**: Detailed logging for monitoring and debugging
- **Testing**: Comprehensive test suite with pytest
- **Optimization**: Price filtering and optional date filtering
- **Type Hints**: Python type hints for better code clarity

## Example Output

After running the pipeline, you'll see:
```
2026-05-06 13:05:51,540 - INFO - Starting ETL Pipeline
2026-05-06 13:05:51,540 - INFO - Loading data from orders.csv
2026-05-06 13:05:51,542 - INFO - Successfully loaded 25 rows
2026-05-06 13:05:51,542 - INFO - Starting data cleaning
2026-05-06 13:05:51,544 - INFO - Data cleaning completed. Final rows: 25
2026-05-06 13:05:51,544 - INFO - Starting data transformation
2026-05-06 13:05:51,546 - INFO - Filtered 0 rows with price <= 0
2026-05-06 13:05:51,548 - INFO - Data transformation completed
2026-05-06 13:05:51,548 - INFO - Saving data to revenue.csv
2026-05-06 13:05:51,550 - INFO - Successfully saved 3 rows to revenue.csv
2026-05-06 13:05:51,550 - INFO - Saving data to daily_sales.csv
2026-05-06 13:05:51,551 - INFO - Successfully saved 13 rows to daily_sales.csv
2026-05-06 13:05:51,551 - INFO - Saving data to transformed_orders.csv
2026-05-06 13:05:51,551 - INFO - Successfully saved 25 rows to transformed_orders.csv
2026-05-06 13:05:51,552 - INFO - ETL Pipeline completed successfully!
2026-05-06 13:05:51,552 - INFO - Generated files: revenue.csv, daily_sales.csv, transformed_orders.csv
```
