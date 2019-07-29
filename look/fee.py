import json
#import the required packages
import psycopg2
import math
import requests
import falcon
import pandas as pd



class Resource(object):

    def on_post(self, req, resp):
        
        filename = "look/ship_fee_sheet.csv"
        csv_data = pd.read_csv(filename) 
        ship_fee_list=csv_data.values.tolist()
        #get the data of the zone list(similar procedure as above)
        filename2 = "look/zone_sheet.csv"
        csv_data2 = pd.read_csv(filename2) 
        zone_list=csv_data2.values.tolist()

        #get the data of the fuel list() (similar procedure as above)
        filename3 = "look/fuel_sheet.csv"
        csv_data3 = pd.read_csv(filename3,encoding = "ISO-8859-1") 
        fuel_list=csv_data3.values.tolist()

        #get the remote zipcode list
        filename4 = "look/remote_sheet.csv"
        csv_data4 = pd.read_csv(filename4) 
        remote_list=csv_data4.values.tolist()
        #get the super remote zipcode list
        filename5 = "look/super_remote_sheet.csv"
        csv_data5 = pd.read_csv(filename5) 
        super_remote_list=csv_data5.values.tolist()

        def binary_search(list1, item):
            n = len(list1)
            if 0 == n:
                return False
            mid = n // 2
            if (int(list1[mid][0]) >= item and int(list1[mid][0])<=item) :
                return True
            elif item < int(list1[mid][0]):
                return binary_search(list1[:mid], item)
            else:
                return binary_search(list1[mid + 1:], item)

        #get the diese price from the official website by calling the api accordingly
        def Current_High_Way_Diesel_Price():
            """
            This function will send a request to the EIA website to get the JSON response
            The api_key is just regitered with your email(this one is from ethan.gan@castlery.com)
            """
            url_r='http://api.eia.gov/series/?'
            param={'api_key':'977fd4f82792b03545caaf61ffde535e','series_id':'PET.EMD_EPD2DXL0_PTE_NUS_DPG.W'}
            request=requests.get(url=url_r,params=param)
            response= request.json()#this response will contain the json values which can be analyzed
            high_way_price=response['series'][0]['data'][0]#this high_way_price is actually a tuple like('date','price')
            date=high_way_price[0]
            price=float(high_way_price[1])# remember to convert the number string into float
            return date,price
        #use the diesel_price to get the fuel_rate according to the sheet
        def fuel_rate(diesel_price,fuel_list):
            """
            input:the diesel_price(get by Current_High_Way_Diesel_Price(), and the fuel_list get from database)
            output: The fuel_rate for today(or you can say: this week
            """
            fuel_rate=-1
            for i in fuel_list:
                if (diesel_price>=float(i[0]) and diesel_price<float(i[1])):
                    fuel_rate=float(i[2])
            if (fuel_rate==-1):
                fuel_rate=7.5
            return fuel_rate*0.01
        #check whether the item is authorized
        def authorization_check(length,width,height,weight):

            """
            This function use the box's information to check whether this item is authorized to ship
            output:1 for unauthorized, 0 for authorized
            """
            if (weight>150 or max(length,width,height)>108 or (2*(length+width+height)-max(length,width,height))>165):
                return 1
            else:
                return 0
        #calculate the additional_handing fee
        def additional_handing(length,width,height,weight,irregular_shape,package_material,wooden_or_medal):
            """
            aim is to calculate the additional_handing fee
            input: the box's info and the special conditions of the item
            output: the sum of additional handing fee(weight:12 and size:7.2)
            """
            if(weight>70):
                size_add=12
            else:
                size_add=0
            is_packaging_in_irregular_shape=irregular_shape
            is_no_packaging_material=package_material
            is_packaging_wooden_or_metal=wooden_or_medal
        ##    is_packaging_in_irregular_shape=int(input("Is this items in irregular shape?: (1 for yes and 0 for no)"))
        ##    is_no_packaging_material=int(input("No package material ?: (1 for yes and 0 for no)"))
        ##    is_packaging_wooden_or_metal=int(input("Is packaging wooden or metal ?: (1 for yes and 0 for no)"))
            x= is_packaging_in_irregular_shape or is_no_packaging_material or is_packaging_wooden_or_metal
            if (x== 1):
                size_add=size_add+7.2
            elif (x== 0):
                list_box=[]
                list_box.append(length)
                list_box.append(width)
                list_box.append(height)
                list_box.sort(reverse=True)
                if ((list_box[0]>48 and list_box[0]<96) or list_box[1]>30):
                    size_add=size_add+7.2
                else:
                    size_add=size_add+0
            else:
                size_add=size_add+0
            return size_add
        #calculate the oversize fee
        def oversize(length,width,height,weight):
            """
            input: box's info
            output: the weight(this is because when the weight is less than 90 but oversized, the weight
            been charged will be 90 instead) and the oversize fee
            Note: condition of larger than 165 is checked by authorization 
            """
            if (2*(length+width+height)-max(length,width,height)>130):
                if weight<90:
                    weight=90
                return 40,weight
            else:
                return 0,weight

        def search_zone(zipcode,zone_list,ship_region):
            """
            This function use the zipcode and the zone_list(from database) to compare between Western and Eastern,
            get the smaller zone then return both the region info(Eastern or Western) and zone number 
            """
            if ship_region=='':
                result_list=[]
                for i in zone_list:
                    if(zipcode>=int(i[1]) and zipcode<=int(i[2])):
                        result_list.append(i)
                        
                print(result_list)
                if(math.isnan(result_list[0][3]) and math.isnan(result_list[1][3])):
                    return 'NA','NA'
                elif (math.isnan(result_list[0][3])):
                    return result_list[1][0],int(result_list[1][3])
                elif (math.isnan(result_list[1][3])):
                    return result_list[0][0],int(result_list[0][3])
                else:
                    if(result_list[0][3]<result_list[1][3]):
                        return result_list[0][0],int(result_list[0][3])
                    else:
                        return result_list[1][0],int(result_list[1][3])
            elif ship_region=='LA_DC':
                for i in zone_list:
                    if(zipcode>=int(i[1]) and zipcode<=int(i[2]) and i[0]=='W'):
                        print(i)
                        if(math.isnan(i[3])):
                            return i[0],'NA'
                        else:
                            return i[0],int(i[3])
            elif ship_region=='NJ_DC':
                for i in zone_list:
                    if(zipcode>=int(i[1]) and zipcode<=int(i[2]) and i[0]=='E'):
                        print(i)
                        if(math.isnan(i[3])):
                            return i[0],'NA'
                        else:
                            return i[0],int(i[3])
        #calculate the normal shipping fee
        def shipping_fee(zone,weight,ship_fee_list):
            """
            input:zone number, chargeable weight, ship_fee_list(from database)
            output: normal shipping fee
            """
            for i in ship_fee_list:
                if (weight==int(i[0])):
                    return float(i[zone-1])
        #calculate the fuel_fee
        def fuel_fee_charge(additional,oversize,ship_fee,remote_charge,residential_charge,rate):
            """This function calculate the fuel fee"""
            return (additional+oversize+ship_fee+remote_charge+residential_charge)*rate
        #get the volumetric_weight according to the box size
        def volumetric_weight(length,width,height):
            """This function is for getting the volumetric weight of the item"""
            return length*width*height/250
        #output the region according to the format
        def region_change(region):
            """
            This function just convert the string of E and W
            to increase the readability of the result
            """
            if (region=='W'):
                return 'US West DC'
            elif (region=='E'):
                return 'US East DC'

            
        #determine the region: normal, remote or super_remote.
        #charge accordingly
        def remote_charge(zipcode,remote_list,super_remote_list):
            """
            this function determines the region category
            and return the remote area charge
            """
            if (binary_search(super_remote_list,zipcode)):
                return 4.65
            elif (binary_search(remote_list,zipcode)):
                return 4.20
            else:
                return 0
        #calculate (ground) residential surcharge
        def residential_surcharge(IsResidential,weight):
            if (IsResidential !=1):
                return 0
            elif (weight<70):
                return 2.6
            else:
                return 4.4

        def final(INPUT,ship_fee_list,zone_list,fuel_list,remote_list,super_remote_list):
            length=INPUT['length']
            width=INPUT['width']
            height=INPUT['height']
            weight=INPUT['weight']
            try:
                zipcode_whole=int(INPUT['postcode'])
            except:
                OUTPUT['status']="Invalid: Postcode is not a number"
                return OUTPUT
            #get the first 3 digit of zipcode to get the region
            zipcode_region=int(str(INPUT['postcode'])[0:3])
            irregular_shape=INPUT['irregular_shape']
            package_material=INPUT['package_material']
            wooden_or_metal=INPUT['wooden_or_metal']
            residential_surcharge_status=INPUT['IsResidential']
            
            ship_region=INPUT["ship_region"]
            #calculate residential surcharge fee
            residential_surcharge_fee=residential_surcharge(residential_surcharge_status,weight)
            #calculate the remote area charge fee
            remote_charge_fee=remote_charge(zipcode_whole,remote_list,super_remote_list)
            #get the region and zone from zipcode
            region,zone=search_zone(zipcode_region,zone_list,ship_region)
            #change the region into more readable string
            region=region_change(region)

            #get diesel price and calculate fuel rate
            current_date,diesel_price=Current_High_Way_Diesel_Price()
            fuel_surcharge_rate=fuel_rate(diesel_price,fuel_list)
            # check authorization, if unauthorized, just quit
            OUTPUT={}
            
            authorization_status=authorization_check(length,width,height,weight)
            if (authorization_status==1):

                OUTPUT['status']="Invalid: Item Unauthorized"
                return OUTPUT
            if (zone=='NA'):
                OUTPUT['status']="Invalid: Postcode not Supported"
                return OUTPUT
            #calculate additional and oversize fees
            additional=additional_handing(length,width,height,weight,irregular_shape,package_material,wooden_or_metal)
            #check the oversize fee and whether weight need to be updated
            oversize_fee,weight=oversize(length,width,height,weight)   

            #get the chargeable weight
            weight=max(volumetric_weight(length,width,height),weight)
            weight=math.ceil(weight)
            #calculate ship_fee and fuel_fee
            ship_fee=shipping_fee(zone,weight,ship_fee_list)
            fuel_fee=fuel_fee_charge(additional,oversize_fee,ship_fee,remote_charge_fee,residential_surcharge_fee,fuel_surcharge_rate)
            #add up fees
            total=additional+oversize_fee+ship_fee+fuel_fee+remote_charge_fee+residential_surcharge_fee
            #output as JSON
            output={}
            output['weight(lbs)']=weight
            output['additional_handing_fee(USD)']=additional
            output['oversize_fee(USD)']=oversize_fee
            output['ship_surcharge_fee(USD)']=ship_fee
            output['fuel_fee(USD)']=fuel_fee
            output['remote_area_charge(USD)']=remote_charge_fee
            output['residential_surcharge_fee(USD)']=residential_surcharge_fee
            output['total_fee(USD)']=total
            output['shipping_region']=region
            output['diesel_price_date']=current_date
            return output
#input units: length,width,height: inch
#weightL lbs
#condition checking :1 for yes, 0 for no
        result_json=json.loads(req.stream.read().decode('utf-8'))
        output=final(result_json,ship_fee_list,zone_list,fuel_list,remote_list,super_remote_list)
        print(result_json)
        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output)
# import falcon

# import msgpack


# class Resource(object):

#     def on_get(self, req, resp):
#         doc = {
#             'images': [
#                 {
#                     'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
#                 }
#             ]
#         }

#         resp.data = msgpack.packb(doc, use_bin_type=True)
#         resp.content_type = falcon.MEDIA_MSGPACK
#         resp.status = falcon.HTTP_200