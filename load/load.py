"""The load.py file can be used to load Product_Information.xlsx by
calling upon the run_edge_tests(PATH) function where PATH is the path to 
an xlsx file. For use in project the run_edge_tests function returns a
dataframe of product information. However, for the edge tests we use an
unassigned function call.

The test file test_edge contains 16 edge tests which work in conjuction
with this file. Sometimes strings are converted to NaNs when uploaded,
so we raise TypeErrors for strings and NaNs in columns.

The first function, load_products, was taken from the draft app.py file."""

import pandas as pd

def load_products(product_path):
    """This is lifted from the draft app.y streamlit test that uploads and 
    generates a list of products. This was used to keep input file formats 
    comparable. It returns a loaded df."""
    df = pd.read_excel(product_path)
    #df = pd.read_excel("data/Product_Information_Price_Ounce_Negative_.xlsx")

    df["tags_clean"] = df["tags"].fillna("").apply(
        lambda x: [t.strip().lower() for t in str(x).split(",") if t.strip()]
    )

    df["roast_type"] = df["roast_type"].fillna("Unknown")
    df["origin"] = df["origin"].fillna("Unspecified")

    df["price_numeric"] = pd.to_numeric(df["price_numeric"], errors="coerce")
    df["price_per_oz"] = pd.to_numeric(df["price_per_oz"], errors="coerce")

    for col in ["decaf", "blend", "single_origin", "available_ground",
                "has_reviews"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    return df

### Check Price Type

def check_price_type(df):
    """This function checks type entries for price related columns.
    Sometimes strings are converted to NaNs on the upload, so we
    check that both are not contained in the column. No return."""
    for i in range(0,len(df)):
        if type(df['price'][i])==str:
            raise TypeError("price column cannot have string.")
        if type(df['price_numeric'][i])==str:
            raise TypeError("price_numeric column cannot have string.")
        if type(df['price_per_oz'][i])==str:
            raise TypeError("price_per_oz column cannot have string.")
        if pd.isna(df['price'][i]):
            raise TypeError("price column contains a NaN or string")
        if pd.isna(df['price_numeric'][i]):
            raise TypeError("price_numeric column contains a NaN or" \
            "string")
        if pd.isna(df['price_per_oz'][i]):
            raise TypeError("price_per_oz column contains a NaN or" \
            "string")

### Check Price Value

def check_price(df):
    """This function checks the three price related columns to ensure 
    that are not zero or negative. It returns nothing, but can raise
    a value error. No return."""
    for col in ['price', 'price_numeric', 'price_per_oz']:
        if sum(df[col]<=0)>0:
            check=f"'{col}'"
            raise ValueError(({check}),"column - and perhaps other price" \
            " columns - cannot be 0 or less than 0")


### Check Size

def check_size_type(df):
    """This checks for strings or NaNs in the size_oz column.
    No return."""
    for i in range(0,len(df)):
        if type(df['size_oz'][i])==str:
            raise TypeError("size_oz column cannot have string.")
        if pd.isna(df['size_oz'][i]):
            raise TypeError("size_oz column contains a NaN or string")


def take_two(string):
    """This function checks the first three characters of the size field
    for numeracy raising errors if first two are alphabetical or
    if the size in ounces is greater than 100. It returns a two digit
    integer, if possible. No return."""
    count=0
    link="" #repository for strings that can be converted to int
    for char in string:
        if count==0:
            try:
                int(char) #attempt conversion
                link = char
                count=count+1
            except:
                raise TypeError("First character is not an integer.")
        elif count==1:
            try:
                int(char)
                link = link + char
                count=count+1
            except:
                count=count+1
        elif count==2:
            try:
                int(char)
                link = link + char
                count=count+1
            except:
                count=count+1
    link = int(link)
    if link > 99:
        raise ValueError("Bulk package over 6.25 lbs.")
    return link


def check_size(df):
    """This function checks the columns size and size_oz to ensure
    they are between 0 and 100, positive, and equal each other. No return.
    It relies upon the function take_two. No return."""
    for i in range(0,len(df)):
        if take_two(df['size'][i])==0:
            raise ValueError("Size column cannot equal zero.")
        if df['size_oz'][i]<=0:
            raise ValueError("size_oz column cannot be less than or equal"\
            "to zero.")
        if take_two(df['size'][i])!=df['size_oz'][i]:
            raise ValueError("Size column doesn't equal size_oz column.")

### check reviews

def check_reviews_type(df):
    """This function checks quantitiative review results for type errors.
    No retrun."""
    for i in range(0,len(df)):
        if type(df['hearts'][i])==str:
            raise TypeError("hearts column cannot have string.")
        if type(df['total_reviews'][i])==str:
            raise TypeError("total_reviews column cannot have string.")
        if type(df['heart_percentage'][i])==str:
            raise TypeError("heart_percentage column cannot have string.")
        if pd.isna(df['hearts'][i]):
            raise TypeError("hearts column contains a NaN or string")
        if pd.isna(df['total_reviews'][i]):
            raise TypeError("total_reviews column contains a NaN or string")
        if pd.isna(df['heart_percentage'][i]):
            raise TypeError("heart_percentage column contains a NaN or string")


def check_numeric_reviews(df):
    """This function rolls through review columns looking for
     negative values. No return."""
    for col in ['hearts', 'total_reviews', 'heart_percentage']:
        if sum(df[col]<0)>0:
            check=f"'{col}'"
            raise ValueError(({check}),"column - and perhaps other price"\
            " columns - cannot be 0 or less than 0")


def run_edge_tests(path):
    """After loading products this function aggregates each of the checks
    and provides a return of the loaded dataframe. As a result, this
    function can be called upon by other modules to load the
    Product_Information.xlsx file."""
    df=load_products(path)
    check_price_type(df)
    check_price(df)
    check_size_type(df)
    check_size(df)
    check_reviews_type(df)
    check_numeric_reviews(df)
    return df
