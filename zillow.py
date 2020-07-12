from datetime import datetime
from urllib.request import Request, urlopen
from re import sub
from lxml import html
import requests
import unicodecsv as csv
import argparse
import json
import re


def clean(text):
    if text:
        return ' '.join(' '.join(text).split())
    return None


def get_headers():
    # Creating headers.
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'accept-encoding': 'gzip, deflate, sdch, br',
               'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
    return headers


def create_url(zipcode, status, filter):
    # Creating Zillow URL based on the filter.

    if filter == "newest":
        url = "https://www.zillow.com/homes/{0}/{1}/0_singlestory/days_sort/".format(status, zipcode)
    elif filter == "cheapest":
        if status == "for_rent":
            url = "https://www.zillow.com/homes/{0}/{1}/0_singlestory/paymenta_sort/".format(status, zipcode)
        else:
            url = "https://www.zillow.com/homes/{0}/{1}/0_singlestory/pricea_sort/".format(status, zipcode)
    else:
        url = "https://www.zillow.com/homes/{0}/{1}/0_singlestory/featured_sort/".format(status, zipcode)
    print(url)
    return url


def save_to_file(response):
    # saving response to `response.html`
    with open("response.html", 'w') as fp:
        fp.write(response.text)


def write_data_to_csv(data, status):
    # saving scraped data to csv.
    # heroku pg:psql -c "\copy listings_listing(title, address, city, state, zipcode, description, price, bedrooms, bathrooms, sqft, lot_size, photo_main, is_published, list_date, realtor_id) from 'rent-properties-07112-2020-03-25.csv' DELIMITER ',' CSV HEADER"

    with open("%s-properties-%s-%s.csv" % (status, zipcode, datetime.today().strftime('%Y-%m-%d')), 'wb') as csvfile:

        fieldnames = ['title', 'address', 'city', 'state', 'zipcode', 'facts and features', 'price', 'bedrooms', 'bathrooms', 'sqft',
            'lot_size', 'photo_main', 'is_published', 'list_date', 'realtor_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def get_response(url):
    # Getting response from zillow.com.

    for i in range(5):
        response = requests.get(url, headers=get_headers())
        print("status code received:", response.status_code)
        if response.status_code != 200:
            # saving response to file for debugging purpose.
            save_to_file(response)
            continue
        else:
            save_to_file(response)
            return response
    return None

def get_data_from_json(raw_json_data):
    # getting data from json (type 2 of their A/B testing page)
    cleaned_data = clean(raw_json_data).replace('<!--', "").replace("-->", "")
    properties_list = []

    try:
        json_data = json.loads(cleaned_data)
        search_results = json_data.get('searchResults').get('listResults', [])
        print(json_data.get('searchPageSeoObject'))
        total_listing = int(json_data.get('searchList').get('totalResultCount'))
        count = 0
        result_size = len(search_results)
        print("how many results are we processing?", result_size)

        for properties in search_results:
            #print("processing result", count, properties)
            zpid = properties.get('zpid')
            statusText = properties.get('statusText')
            if not zpid.isdigit() or statusText == 'Off market':
                print("bypassing zillow id:", zpid, "statusText:", statusText)
                continue
            address = properties.get('address')
            property_info = properties.get('hdpData', {}).get('homeInfo')
            city = property_info.get('city')
            state = property_info.get('state')
            zipcode = property_info.get('zipcode')
            lot_size = property_info.get('lotSize')
            try:
                price = int(property_info.get('price'))
            except:
                price = 0
            bedrooms = properties.get('beds')
            bathrooms = properties.get('baths')
            area = properties.get('area')
            property_url = properties.get('detailUrl')
            info = f'{bedrooms} bds,{bathrooms} ba,{area} sqft,{property_url}'
            title = properties.get('statusText')
            photo_main = properties.get('imgSrc')


            data = {'address': address,
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'price': price,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'sqft': area,
                    'lot_size': lot_size,
                    'facts and features': info,
                    'title': title,
                    'photo_main': photo_main,
                    'is_published': True, #set this as false for now
                    'list_date': datetime.today().strftime('%Y-%m-%d'),
                    'realtor_id': 3}
            properties_list.append(data)

            count = count + 1

        return total_listing, properties_list

    except ValueError:
        print("Invalid json", ValueError)
        return None


def parse(zipcode, status, filter=None):
    url = create_url(zipcode, status, filter)
    response = get_response(url)

    if not response:
        print("Failed to fetch the page, please check `response.html` to see the response received from zillow.com.")
        return None
    parser = html.fromstring(response.text)

    # replace the parser to take input added above if bot detection evolved again
    #req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    #webpage = urlopen(req).read()
    #parser = html.fromstring(webpage)

    search_results = parser.xpath("//div[@id='search-results']//article")

    if not search_results:
        print("parsing from json data")
        # identified as type 2 page
        raw_json_data = parser.xpath('//script[@data-zrr-shared-data-key="mobileSearchPageStore"]//text()')
        total_listing, prop_list = get_data_from_json(raw_json_data)
        print("total number of listing in this zipcode {0} is {1}".format(zipcode, total_listing))
        page_num = 2
        page_url = "{0}{1}_p/".format(url, page_num)
        while (page_num * 40 <= total_listing or ((page_num-1) * 40 < total_listing)) and requests.get(page_url, headers=get_headers()).status_code == 200:
            print("reading url:", page_url)
            response = get_response(page_url)
            parser = html.fromstring(response.text)
            # req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
            # webpage = urlopen(req).read()
            # parser = html.fromstring(webpage)
            raw_json_data = parser.xpath('//script[@data-zrr-shared-data-key="mobileSearchPageStore"]//text()')
            t, p_list = get_data_from_json(raw_json_data)
            prop_list.extend(p_list)
            page_num += 1
            page_url = "{0}{1}_p/".format(url, page_num)

        return prop_list


    print("parsing from html page")
    properties_list = []
    for properties in search_results:
        raw_address = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
        raw_city = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
        raw_state = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
        raw_postal_code = properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
        raw_price = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
        raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
        raw_broker_name = properties.xpath(".//span[@class='zsg-photo-card-broker-name']//text()")
        url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
        raw_title = properties.xpath(".//h4//text()")

        address = clean(raw_address)
        city = clean(raw_city)
        state = clean(raw_state)
        postal_code = clean(raw_postal_code)
        price = clean(raw_price)
        info = clean(raw_info).replace(u"\xb7", ',')
        broker = clean(raw_broker_name)
        title = clean(raw_title)
        property_url = "https://www.zillow.com" + url[0] if url else None
        is_forsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')

        properties = {'address': address,
                      'city': city,
                      'state': state,
                      'postal_code': postal_code,
                      'price': price,
                      'facts and features': info,
                      'real estate provider': broker,
                      'url': property_url,
                      'title': title}
        if is_forsale:
            properties_list.append(properties)
    return properties_list


if __name__ == "__main__":
    # Reading arguments

    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('zipcode', help='')
    sortorder_help = """
    available sort orders are :
    newest : Latest property details,
    cheapest : Properties with cheapest price
    """
    status_help = """
    available home statuses are :
    for_rent : homes for rent
    for_sale : homes for sale
    recently_sold : homes already sold
    """

    argparser.add_argument('sort', nargs='?', help=sortorder_help, default='Homes For You')
    argparser.add_argument('status', help=status_help)
    args = argparser.parse_args()
    zipcode = args.zipcode
    sort = args.sort
    status = args.status
    print ("Fetching data for %s" % (zipcode))
    scraped_data = parse(zipcode, status, sort)
    if scraped_data:
        print ("Writing data to output file")
        write_data_to_csv(scraped_data, status)
