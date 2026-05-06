import pandas as pd
import logging
from datetime import datetime
from typing import Optional

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: For other loading errors
    """
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} rows")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the data by removing duplicates and handling missing values.
    
    Args:
        df (pd.DataFrame): Raw data
        
    Returns:
        pd.DataFrame: Cleaned data
    """
    logger.info("Starting data cleaning")
    
    # Remove duplicates
    initial_rows = len(df)
    df_cleaned = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df_cleaned)
    
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    # Handle missing values
    df_cleaned['quantity'] = df_cleaned['quantity'].fillna(1)
    df_cleaned['price'] = df_cleaned['price'].fillna(0)
    
    # Fill missing values in other columns with 'Unknown'
    categorical_cols = ['product', 'category']
    for col in categorical_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].fillna('Unknown')
    
    logger.info(f"Data cleaning completed. Final rows: {len(df_cleaned)}")
    return df_cleaned


def transform_data(df: pd.DataFrame, start_date: Optional[str] = None, end_date: Optional[str] = None) -> tuple:
    """
    Transform the data by creating derived metrics and aggregations.
    
    Args:
        df (pd.DataFrame): Clean data
        start_date (str, optional): Filter start date (YYYY-MM-DD)
        end_date (str, optional): Filter end date (YYYY-MM-DD)
        
    Returns:
        tuple: (transformed_df, revenue_by_category, daily_sales_count)
    """
    logger.info("Starting data transformation")
    
    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Optional date filtering
    if start_date:
        start_date = pd.to_datetime(start_date)
        df = df[df['order_date'] >= start_date]
        logger.info(f"Filtered data from {start_date}")
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        df = df[df['order_date'] <= end_date]
        logger.info(f"Filtered data until {end_date}")
    
    # Create total column
    df['total'] = df['price'] * df['quantity']
    
    # Optimization: Filter rows where price > 0
    df_filtered = df[df['price'] > 0]
    logger.info(f"Filtered {len(df) - len(df_filtered)} rows with price <= 0")
    
    # Calculate revenue per category
    revenue_by_category = df_filtered.groupby('category')['total'].sum().reset_index()
    revenue_by_category.columns = ['category', 'revenue']
    
    # Calculate daily sales count
    daily_sales_count = df_filtered.groupby(df_filtered['order_date'].dt.date).size().reset_index()
    daily_sales_count.columns = ['date', 'sales_count']
    
    logger.info("Data transformation completed")
    return df_filtered, revenue_by_category, daily_sales_count


def save_data(df: pd.DataFrame, path: str) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df (pd.DataFrame): Data to save
        path (str): Output file path
    """
    try:
        logger.info(f"Saving data to {path}")
        df.to_csv(path, index=False)
        logger.info(f"Successfully saved {len(df)} rows to {path}")
    except Exception as e:
        logger.error(f"Error saving data to {path}: {str(e)}")
        raise


def run_pipeline(input_file: str = "orders.csv", 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None) -> None:
    """
    Run the complete ETL pipeline.
    
    Args:
        input_file (str): Input CSV file path
        start_date (str, optional): Filter start date (YYYY-MM-DD)
        end_date (str, optional): Filter end date (YYYY-MM-DD)
    """
    logger.info("Starting ETL Pipeline")
    
    try:
        # Load data
        raw_data = load_data(input_file)
        
        # Clean data
        clean_df = clean_data(raw_data)
        
        # Transform data
        transformed_df, revenue_by_category, daily_sales_count = transform_data(
            clean_df, start_date, end_date
        )
        
        # Save results
        save_data(revenue_by_category, "revenue.csv")
        save_data(daily_sales_count, "daily_sales.csv")
        save_data(transformed_df, "transformed_orders.csv")
        
        logger.info("ETL Pipeline completed successfully!")
        logger.info(f"Generated files: revenue.csv, daily_sales.csv, transformed_orders.csv")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage
    run_pipeline()
    
    # Example with date filtering
    # run_pipeline(start_date="2024-01-20", end_date="2024-01-25")
