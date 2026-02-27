"""Script taps King County health inspections API for addresses of recently
inspected caffes where specific coffees may be found. More elegent and automated
string methods could eliminate the need for hard coding some caffes such as 
CAFFE LADRO for "Ladro Roasting. Output file is address_out.csv"""
################################################################################
from sodapy import Socrata
import pandas as pd

PRODUCTS_PATH = "data/Product_Information.xlsx"

def load_products():
    """This is lifted from the draft app.y streamlit test that uploads and 
    generates a list of products. This was used to keep imput file formats 
    comparable"""
    df = pd.read_excel(PRODUCTS_PATH)

    df["tags_clean"] = df["tags"].fillna("").apply(
        lambda x: [t.strip().lower() for t in str(x).split(",") if t.strip()]
    )

    df["roast_type"] = df["roast_type"].fillna("Unknown")
    df["origin"] = df["origin"].fillna("Unspecified")

    df["price_numeric"] = pd.to_numeric(df["price_numeric"], errors="coerce")
    df["price_per_oz"] = pd.to_numeric(df["price_per_oz"], errors="coerce")

    for col in ["decaf", "blend", "single_origin", "available_ground", "has_reviews"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)

    return df

def freq_roasters(df):
    """ This function takes the products df of coffees produced by app.py and 
    produces a list of roasteries named in the file and the number of coffees sold."""
    products_roaster=products[['roaster']]
    df=products_roaster.groupby(['roaster']).agg({'roaster': 'count'})
    df['name']=df.index
    df=df.reset_index(drop=True)
    df=df[['name','roaster']]
    df['roaster_no_of_coffees']=df['roaster']
    df=df.drop(columns=['roaster'])
    return df # some duplicates exist: Tonys vs. Tony's

def county_api_call(list_of_roasteries):
    """This function makes loops a simple single api call of king county health
    inspections snagging address and city of the most recent health inspection
    the cafe has had. Comments mark where expansions could be made to return
    multiple address. Key sources listed below, starter sql code from socrata
    tutorials"""

    #https://dev.socrata.com/foundry/data.kingcounty.gov/f29f-zza5
    #https://kingcounty.gov/en/dept/dph/health-safety/food-safety/search-restaurant-safety-ratings#/
    #https://github.com/mebauer/sodapy-tutorial-nyc-opendata/blob/main/socrata-query-language.ipynb
    #https://mharty3.github.io/til/SQL/create-in-statement-with-python/#:~:text=When%20performing%20data%20analysis%20with,pd%20import%20pyodbc%20conn%20=%20pyodbc.

    #intitializations
    row=[]
    rows=[]
    row_nan=[]

    for i in list_of_roasteries:
        check=f"'{i}'"
        #print(check)
        socrata_domain = 'data.kingcounty.gov'
        socrata_dataset_identifier = 'f29f-zza5'
        client = Socrata(
            socrata_domain,
            app_token=None,
            timeout=100
        )
        # SoQL query string below:
        # select all columns, where the inspection_date
        # is within a data and present IN single record f'strng check.
        try:
            query = f"""SELECT *
                 WHERE inspection_date BETWEEN '2024-10-01' AND '2026-01-30'
                 AND name IN ({check})
                 ORDER BY
                     name
                 LIMIT
                     1
            """ #limit set to 1, i.e. most recent inspection, expanding finds
            #other locations.
            results = client.get(socrata_dataset_identifier, query=query)
            df = pd.DataFrame.from_records(results)
            row=df[['name','name', 'address', 'city']].values.tolist()[0]
            row[0]=check #shift first name to search name
            rows.append(row)
        # name not found in query
        except:
            row_nan=[check,'NaN','NaN','NaN']
            rows.append(row_nan)
    api_results=pd.DataFrame(rows,columns=['search_name','cafe_name', 'cafe_address', 'cafe_city'])
    return api_results

def cafe_override(df):
    """Takes a df list of roasteries and allows manual override of the names
    because cafes serving the roastery's coffee often have different names.
    Checks length of output list is the same as input df"""
    cafes = ['ANCHORHEAD COFFEE', 'Blossom Coffee Roasters','CAFFE VITA',
             'Camber Coffee', 'Kuma Coffee', 'CAFFE LADRO', 'OLYMPIA COFFEE', 
             'OLYMPIA COFFEE', 'SEVEN COFFEE ROASTERS MARKET & CAFE', 'LITTLE JAYE',
             "Tony's Coffee", 'Tonys Coffee','VICTROLA COFFEE','VICTROLA COFFEE']    
    if len(cafes)!=df.shape[0]:
        raise TypeError("Override roastery list doesn't match WA roasteries in products?")
    if [cafes[10]]!=df[10:11]['name'].values.tolist():
        raise ValueError("WA roasters file has changed.")
    return cafes

#function calls
products = load_products()
df_roaster=freq_roasters(products)
cafes_list=cafe_override(df_roaster)
api_roasteries=county_api_call(cafes_list)
address_out=pd.concat([df_roaster,api_roasteries],axis=1) #combines dfs side by side
address_out.to_csv('./data/address_out.csv', index=False)
