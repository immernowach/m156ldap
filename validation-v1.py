import pandas as pd

def load_cleaned_data(file_path, encoding='ISO-8859-1'):
    """
    Load cleaned data from a CSV file.

    Parameters:
    - file_path (str): The path to the cleaned CSV file.
    - encoding (str): The character encoding for reading the CSV file.

    Returns:
    - pandas.DataFrame: The cleaned data.
    """
    try:
        return pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        print(f"Error loading cleaned data: {e}")
        return None

def validate_ou_structure(data):
    """
    Validate the organizational unit (OU) structure in the cleaned data.

    Parameters:
    - data (pandas.DataFrame): The cleaned data.

    Returns:
    - bool: True if the OU structure is valid, False otherwise.
    """
    if 'OU' not in data.columns or data['OU'].isnull().any():
        print("OU structure validation failed: Missing or empty OU values found.")
        return False
    print("OU structure validation passed.")
    return True

def validate_email_addresses(data):
    """
    Validate email addresses in the cleaned data to ensure they follow the correct format.

    Parameters:
    - data (pandas.DataFrame): The cleaned data.

    Returns:
    - bool: True if email addresses are valid, False otherwise.
    """
    if 'email' not in data.columns or not data['email'].str.contains('@').all():
        print("Email address validation failed: Incorrect email formats found.")
        return False
    print("Email address validation passed.")
    return True

def validate_user_naming_conventions(data):
    """
    Check if user naming conventions are consistent in the cleaned data.

    Parameters:
    - data (pandas.DataFrame): The cleaned data.

    Returns:
    - bool: True if naming conventions are consistent, False otherwise.
    """
    required_columns = ['first_name', 'last_name']
    for column in required_columns:
        if column not in data.columns or data[column].isnull().any():
            print(f"User naming conventions validation failed: Missing or empty {column} values.")
            return False
    print("User naming conventions validation passed.")
    return True

def validate_no_duplicates(data):
    """
    Check if the cleaned data contains any duplicate entries.

    Parameters:
    - data (pandas.DataFrame): The cleaned data.

    Returns:
    - bool: True if no duplicates are found, False otherwise.
    """
    if data.duplicated().sum() > 0:
        print("Duplicate entries validation failed: Duplicate entries found.")
        return False
    print("Duplicate entries validation passed.")
    return True

def run_validations(file_path):
    """
    Run a series of validations on the cleaned data.

    Parameters:
    - file_path (str): The path to the cleaned CSV file.
    """
    data = load_cleaned_data(file_path)
    if data is None:
        return

    validations = [
        validate_ou_structure,
        validate_email_addresses,
        validate_user_naming_conventions,
        validate_no_duplicates
    ]

    all_valid = True
    for validation in validations:
        if not validation(data):
            all_valid = False

    if all_valid:
        print("All validations passed: The cleaned data is ready for migration.")
    else:
        print("Some validations failed: Review and correct the cleaned data before migration.")

# Example usage:
# Ensure to replace 'path/to/cleaned_data.csv' with the actual path to your cleaned data file.
run_validations('export.csv')
