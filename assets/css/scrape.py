import pprint
import requests
from bs4 import BeautifulSoup
from re import sub
import re
import pandas as pd
from datetime import datetime
from price_parser import Price
# function to grab ad prices from renthop manager page (single page only)
def get_info(url=None):
    
    page_apartments = []

    # start requests session
    with requests.Session() as s:

        # if url passed load remote html content
        if url:
            response = s.get(url)
        
            soup = BeautifulSoup(response.content, 'html.parser')
        else:
            # if no url, load test html from local file
            with open('sample_data/local.html', 'r') as html:
                soup = BeautifulSoup(html.read(), 'html.parser')
        
        #get listing divs
        listings = soup.find_all("div", {"class":"search-listing"})
        #get prices and add to price array
        for listing in listings:
            apart = {}
            apart['size'] = None
            apart['latitude'] = float(listing.get("latitude"))
            apart['longitude'] = float(listing.get("longitude"))
            apart['district'] = listing.find("div", {"class":"font-size-9 overflow-ellipsis"}).get_text()
            
            properties = []
            tr = listing.find('tr').find_all('td')
            for div in tr:
                properties.append(div.get_text().replace(' ','').replace('\n',''))
            apart['properties'] = properties
            
            
            properties2 = []
            tag = listing.find("div", {"style":"margin-top: 10px; position: relative;"}).find("div",{"class":"font-size-9"}).get_text()
            tag = str(tag)
            if 'ft' in tag:
                try:
                    size = re.findall("\d+\,\d+",tag)
                    apart['size'] = size
                except:
                    pass
                
            apart['properties2'] = tag
            #listing_coordinates = listing.find("div", {"class":"search-listing font-size-10 my-3 my-md-0 py-0 py-md-4"}).get('latitude')
            apart['address'] = listing.find("a",{"class":"font-size-11 listing-title-link b"}).get_text()
            listing_url = listing.find("a",{"class":"font-size-11 listing-title-link b"}).get('href')
            apart['url'] = listing_url
            print('\n')
            print(listing_url)
            with requests.Session() as listing_s:
                listing_response = listing_s.get(listing_url)
                listing_soup = BeautifulSoup(listing_response.content, 'html.parser')
                
                try:
                    apart['date_posted'] = listing_soup.find("div",{"class":"font-size-10 font-gray-1"}).get_text().replace('\n','')
                except:
                     apart['date_posted'] = None
                apart['hopscore'] = listing_soup.select('span.bold.font-blue')

                #apart['description'] = listing_soup.find("div", {"id":"description"}).find_next("div", {"class":"font-size-10"}).get_text()
                apart['description'] = listing_soup.select('div:nth-of-type(16) div.font-size-10')
                
                amenities = []
                try:
                    for div in listing_soup.find("div", {"class":"columns-2"}).findChildren("div"):
                        amenities.append(div.get_text().replace('\n', ''))
                except:
                    pass
                apart['amenities'] = amenities
                
                
                try:
                    apart['renthop_description'] = listing_soup.find_all("div",
                                                  {"id":"description", "class":"bold font-size-12"})[-1].find_next("div", 
                                                                                                                    {"class":"font-size-10"}).get_text()
                except:
                    apart['renthop_description'] = None

                apart['review'] = listing_soup.select('span.bold:nth-of-type(2)')[0].get_text()
                print(apart['review'])
                
                nearby_transportation = []
                try:
                    for station in listing_soup.find_all('div', {'class':"subway_boston"}):
                        distance = station.find_next("span", {"style":"color: black; font-weight: bold"})
                        nearby_transportation.append((station.get_text(), distance.get_text()))
                except:
                    pass
                apart['nearby_transporation'] = nearby_transportation
                
                
                nearby_schools = []
                try:
                    for school in listing_soup.find_all('a', {"class":"bold"}):
                        distance = school.find_next("span", {"class":"font-black"})
                        nearby_schools.append((school.get_text(), distance.get_text()))
                except:
                    pass
                apart['nearby_school'] = nearby_schools

               
                try:
                    apart['neighborhood_price'] = listing_soup.select('span.b:nth-of-type(3)')[0].get_text()
                except:
                    apart['neighborhood_price'] = []
                
                try:
                    apart['distance_to_avg'] = listing_soup.select('.font-size-10 span.b:nth-of-type(1)')[0].get_text()
                except:
                    apart['distance_to_avg'] = []
                    
                    
                try:
                    apart['neighborhood'] = listing_soup.select('div:nth-of-type(36) div.bold')[0].get_text()
                except:
                    apart['neighborhood'] = None
                
                try:
                    apart['neighborhood_description'] = listing_soup.select('div:nth-of-type(36) div:nth-of-type(4)')[0].get_text()
                except:
                    apart['neighborhood_description'] = None
                    
                apart['date_scraped'] = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
               
                page_apartments.append(apart)
       
        return pd.DataFrame(page_apartments)
boston_apartments = pd.DataFrame()


    


for page in range(1,300):
    if page%10 ==0:
        print(page)
    url = "https://www.renthop.com/search/boston-ma?location_search=&min_price=0&max_price=8000&q=&neighborhoods_str=&sort=hopscore&page="+str(page)
    apartments = get_info(url)
    boston_apartments = boston_apartments.append(apartments)

boston_apartments.to_csv('renthop1_300.csv')
    
    