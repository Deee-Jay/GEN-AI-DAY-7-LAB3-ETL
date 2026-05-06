import pytest
import pandas as pd
import os
from main import load_data, clean_data, transform_data, save_data, run_pipeline


class TestETLPipeline:
    """Test suite for the ETL pipeline functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'order_id': [1, 2, 3, 4],
            'customer_id': [101, 102, 103, 104],
            'product': ['Laptop', 'T-shirt', 'Coffee Maker', 'Headphones'],
            'category': ['Electronics', 'Clothing', 'Home', 'Electronics'],
            'price': [899.99, 29.99, 79.99, 199.99],
            'quantity': [1, 2, 1, 1],
            'order_date': ['2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16']
        })
    
    @pytest.fixture
    def sample_data_with_duplicates(self):
        """Create sample data with duplicates for testing."""
        return pd.DataFrame({
            'order_id': [1, 1, 2, 3],
            'customer_id': [101, 101, 102, 103],
            'product': ['Laptop', 'Laptop', 'T-shirt', 'Coffee Maker'],
            'category': ['Electronics', 'Electronics', 'Clothing', 'Home'],
            'price': [899.99, 899.99, 29.99, None],
            'quantity': [1, 1, 2, None],
            'order_date': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-16']
        })
    
    def test_load_data_file_exists(self, sample_data, tmp_path):
        """Test loading data when file exists."""
        # Create temporary CSV file
        csv_file = tmp_path / "test_orders.csv"
        sample_data.to_csv(csv_file, index=False)
        
        # Test loading
        loaded_data = load_data(str(csv_file))
        
        # Assertions
        assert not loaded_data.empty
        assert len(loaded_data) == 4
        assert list(loaded_data.columns) == ['order_id', 'customer_id', 'product', 'category', 'price', 'quantity', 'order_date']
    
    def test_load_data_file_not_exists(self):
        """Test loading data when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent_file.csv")
    
    def test_clean_data_no_duplicates(self, sample_data):
        """Test cleaning data without duplicates."""
        cleaned_data = clean_data(sample_data)
        
        # Should remain the same
        assert len(cleaned_data) == len(sample_data)
        assert not cleaned_data.empty
    
    def test_clean_data_removes_duplicates(self, sample_data_with_duplicates):
        """Test that cleaning removes duplicates."""
        cleaned_data = clean_data(sample_data_with_duplicates)
        
        # Should remove one duplicate
        assert len(cleaned_data) == 3
        
        # Check no duplicates remain
        assert len(cleaned_data.drop_duplicates()) == len(cleaned_data)
    
    def test_clean_data_handles_missing_values(self, sample_data_with_duplicates):
        """Test that cleaning handles missing values correctly."""
        cleaned_data = clean_data(sample_data_with_duplicates)
        
        # Check missing values are filled
        assert cleaned_data['price'].isnull().sum() == 0
        assert cleaned_data['quantity'].isnull().sum() == 0
        
        # Check specific filled values
        assert cleaned_data.loc[cleaned_data['product'] == 'Coffee Maker', 'price'].iloc[0] == 0
        assert cleaned_data.loc[cleaned_data['product'] == 'Coffee Maker', 'quantity'].iloc[0] == 1
    
    def test_transform_data_creates_total_column(self, sample_data):
        """Test that transform_data creates total column."""
        transformed_df, revenue_df, daily_df = transform_data(sample_data)
        
        # Check total column exists and is calculated correctly
        assert 'total' in transformed_df.columns
        assert transformed_df.loc[0, 'total'] == 899.99 * 1  # Laptop
        assert transformed_df.loc[1, 'total'] == 29.99 * 2  # T-shirt
    
    def test_transform_data_revenue_by_category(self, sample_data):
        """Test revenue calculation by category."""
        _, revenue_df, _ = transform_data(sample_data)
        
        # Check structure
        assert list(revenue_df.columns) == ['category', 'revenue']
        assert len(revenue_df) == 3  # Electronics, Clothing, Home
        
        # Check calculations
        electronics_revenue = revenue_df[revenue_df['category'] == 'Electronics']['revenue'].sum()
        assert electronics_revenue == 899.99 + 199.99  # Laptop + Headphones
    
    def test_transform_data_daily_sales_count(self, sample_data):
        """Test daily sales count calculation."""
        _, _, daily_df = transform_data(sample_data)
        
        # Check structure
        assert list(daily_df.columns) == ['date', 'sales_count']
        assert len(daily_df) == 2  # Two distinct dates
        
        # Check counts
        jan_15_count = daily_df[daily_df['date'].astype(str) == '2024-01-15']['sales_count'].sum()
        assert jan_15_count == 2  # Two orders on Jan 15
    
    def test_transform_data_filters_price_gt_zero(self):
        """Test that transform_data filters out rows with price <= 0."""
        data_with_zero_price = pd.DataFrame({
            'order_id': [1, 2, 3],
            'product': ['Product1', 'Product2', 'Product3'],
            'category': ['A', 'B', 'C'],
            'price': [10.0, 0.0, -5.0],
            'quantity': [1, 1, 1],
            'order_date': ['2024-01-15', '2024-01-15', '2024-01-15']
        })
        
        transformed_df, _, _ = transform_data(data_with_zero_price)
        
        # Should only keep the row with price > 0
        assert len(transformed_df) == 1
        assert transformed_df['price'].iloc[0] == 10.0
    
    def test_transform_data_date_filtering(self, sample_data):
        """Test date filtering functionality."""
        transformed_df, revenue_df, daily_df = transform_data(
            sample_data, start_date="2024-01-16", end_date="2024-01-16"
        )
        
        # Should only include Jan 16 data
        assert len(transformed_df) == 2  # Coffee Maker, Headphones
        assert len(daily_df) == 1  # Only one date
    
    def test_save_data(self, sample_data, tmp_path):
        """Test saving data to CSV."""
        output_file = tmp_path / "test_output.csv"
        
        save_data(sample_data, str(output_file))
        
        # Check file exists
        assert os.path.exists(output_file)
        
        # Check content
        saved_data = pd.read_csv(output_file)
        assert len(saved_data) == len(sample_data)
        assert list(saved_data.columns) == list(sample_data.columns)
    
    def test_dataset_not_empty_after_loading(self):
        """Test that dataset is not empty after loading."""
        # Using the actual orders.csv file
        if os.path.exists("orders.csv"):
            loaded_data = load_data("orders.csv")
            assert not loaded_data.empty
            assert len(loaded_data) > 0
    
    def test_no_null_values_in_price_after_cleaning(self):
        """Test that there are no null values in price after cleaning."""
        # Create data with null price
        data_with_null_price = pd.DataFrame({
            'order_id': [1, 2],
            'product': ['Product1', 'Product2'],
            'category': ['A', 'B'],
            'price': [10.0, None],
            'quantity': [1, 1],
            'order_date': ['2024-01-15', '2024-01-15']
        })
        
        cleaned_data = clean_data(data_with_null_price)
        
        # Check no null values in price
        assert cleaned_data['price'].isnull().sum() == 0
        assert cleaned_data.loc[1, 'price'] == 0  # Should be filled with 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
