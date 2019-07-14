# Falcon_csv_FedEx_Fee_Calculation
Using Falcon to create the api, input a json, format as :



{"length": 15.748, "width": 23.622, "height": 78.74,
 "weight": 66.1, "postcode": 94102, "irregular_shape": 1,
 "package_material": 0, "wooden_or_metal": 0,"residential_surcharge":1,
 "ground_residential_surcharge":0}
 
 
 
 
Output will be like:




{
    "weight": 117,
    "additional_handing_fee": 7.2,
    "oversize_fee": 40,
    "ship_fee": 29.23,
    "fuel_fee": 5.532100000000001,
    "remote_area_charge": 0,
    "residential_surcharge_fee": 2.6,
    "total_fee": 84.5621,
    "shipping_region": "US West DC",
    "diesel_price_date": "20190708"
}




just use gunicorn in mac and waitress in windows to start the server locally
and use postman to test
