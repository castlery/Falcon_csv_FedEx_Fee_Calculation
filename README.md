# Falcon_csv_FedEx_Fee_Calculation

waitress command: waitress-serve --port=8000 look.app:api


Using Falcon to create the api, input a json, format as :



{"length": 15.748, "width": 23.622, "height": 78.74,
 "weight": 66.1, "postcode": 94102, "irregular_shape": 1,
 "package_material": 0, "wooden_or_metal": 0,"IsResidential":1,
"ship_region":"NJ_DC"}
 
 
 
 
Output will be like:




{
    "weight(lbs)": 117,
    "additional_handing_fee(USD)": 7.2,
    "oversize_fee(USD)": 40,
    "ship_surcharge_fee(USD)": 41.72,
    "fuel_fee(USD)": 6.4064000000000005,
    "remote_area_charge(USD)": 0,
    "residential_surcharge_fee(USD)": 2.6,
    "total_fee(USD)": 97.9264,
    "shipping_region": "US East DC",
    "diesel_price_date": "20190722"
}




just use gunicorn in mac and waitress in windows to start the server locally
and use postman to test
