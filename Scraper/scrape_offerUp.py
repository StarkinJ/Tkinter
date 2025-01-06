from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
import logging
from bs4 import BeautifulSoup
import time
import re
import sqlite3


def initialization(search):
    print('initialization started')
    all_data = []
    price_list = []
    item_list = []
    miles_list = []
    links = []

    search = search.lower()
    search_keywords = search.rsplit(' ')
    search = search.replace(" ", "+")

    find_category_keyword = search_keywords[0]

    # Connect to the database
    con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
    con.execute('PRAGMA journal_mode=WAL;')
    cur = con.cursor()

    # Query to find the category
    query = """
            SELECT c.name
            FROM items_in_categories i
            JOIN categories c ON i.category_id = c.id
            WHERE LOWER(i.name) = LOWER(?);
        """

    cur.execute(query, (find_category_keyword,))
    category = cur.fetchone()
    con.close()

    print(f'{search} is in {category} category')
    try:

        logging.basicConfig(level=logging.DEBUG)  # new
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU (recommended for headless)
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        # new
        chrome_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://offerup.com/search?q=" + search)

        start_time = time.time()
        scroll_pause_time = 0.5  # Time to wait between scrolls (in seconds)
        scroll_height = 300  # Number of pixels to scroll each time

        while time.time() - start_time < 5:
            # Scroll down by the set scroll height
            driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
            time.sleep(scroll_pause_time)

        # Now scrape the items and split them into relevant categories
        price_list, item_list, miles_list, links, brand_list, model_list, year_list, is_car = scrape_items(
            driver, price_list, item_list, miles_list, links, search_keywords, category
        )
        print('scrape finished')

        # Close the driver
        driver.quit()

        # Add data to SQL
        add_data_to_sql(brand_list, model_list, year_list, price_list, miles_list, links, is_car, item_list, category)
        print('add data to sql finished')

    except WebDriverException as e:
        print(f"an error occured {e}")
        raise

def scrape_items(driver, price_list, item_list, miles_list, Links, search_keywords, category):
    print('start scraping')
    # Initialize additional lists
    brand_list = []
    model_list = []
    year_list = []
    is_car = []  # Boolean list to determine if the item is a car

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Define regex patterns for classes
    item_name_find_class = re.compile(
        r'MuiTypography-root.*jss\d+.*MuiTypography-subtitle1 MuiTypography-colorTextPrimary '
        r'MuiTypography-noWrap MuiTypography-alignLeft')
    price_name_find_class = re.compile(
        r'MuiTypography-root.*jss\d+.*MuiTypography-body1 MuiTypography-colorTextPrimary MuiTypography-noWrap '
        r'MuiTypography-alignLeft')
    miles_class = re.compile('MuiTypography-root MuiTypography-body1 MuiTypography-colorTextPrimary '
                             'MuiTypography-noWrap')

    li_containers = soup.find_all('li')

    for li in li_containers:
        try:
            # Extract item name
            item_name = li.find('span', class_=item_name_find_class)
            item_text = item_name.get_text().strip() if item_name else None

            if not item_text:
                continue  # Skip if item name is missing

            # Match the item against search keywords
            search_matched = all(keyword in item_text.lower() for keyword in search_keywords)
            if not search_matched:
                continue  # Skip items that don't match the search query

            # Extract price
            item_price = li.find('span', class_=price_name_find_class)
            price_text = item_price.get_text().strip() if item_price else None

            # Extract mileage
            miles_entry = li.find('span', class_=miles_class)
            miles_text = miles_entry.get_text().strip() if miles_entry else None

            # Process price
            if price_text and '$' in price_text:
                clean_price_text = price_text.replace('$', '').replace(',', '').strip()
                price_value = float(clean_price_text)

                # Add price and item to respective lists
                price_list.append(price_value)
                item_list.append(item_text)

                if category[0] != 'cars':
                    print(f"Item classified as {category}: {item_text}")
                    brand_list.append(None)
                    model_list.append(None)
                    year_list.append(None)
                    miles_list.append(None)
                    is_car.append(False)
                else:
                    # Specific logic for cars
                    if category[0] == 'cars':
                        print('category found')
                        brand, model, year = split_item_details(item_text)
                        brand_list.append(brand)
                        model_list.append(model)
                        year_list.append(year)

                        # Process mileage
                        if miles_text:
                            miles_text = miles_text.replace(' miles', '').replace(' km', '').replace(',',
                                                                                                     '').lower()
                            miles_value = float(
                                miles_text.replace('k', '').strip()) * 1000 if 'k' in miles_text else float(
                                miles_text)
                        else:
                            miles_value = None
                        miles_list.append(miles_value)
                        is_car.append(True)
                    else:
                        print(f"Uncategorized item: {item_text}")
                        brand_list.append(None)
                        model_list.append(None)
                        year_list.append(None)
                        miles_list.append(None)
                        is_car.append(False)

                # Append links
                link_tag = li.find('a', href=True)
                full_link = "https://offerup.com" + link_tag['href'] if link_tag else "No Link"
                Links.append(full_link + ' ')

        except Exception as e:
            print(f"Error processing an item: {e}")
        print('end scraping')

    return price_list, item_list, miles_list, Links, brand_list, model_list, year_list, is_car


def split_item_details(item_text):
    print('splitting item started')
    parts = item_text.split()

    if parts[0].isdigit():  # Year comes first
        year = parts[0]
        brand = parts[1]
        model = " ".join(parts[2:])
    else:  # Brand comes first
        year = parts[-1]
        brand = parts[0]
        model = " ".join(parts[1:-1])

    return brand, model, year


def add_data_to_sql(brand_list, model_list, year_list, price_list, miles_list, Links, is_car, item_list, category):
    print('add data to sql started')
    print(is_car)

    con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
    con.execute('PRAGMA journal_mode=WAL;')
    cur = con.cursor()

    for i, (item, price, link) in enumerate(zip(item_list, price_list, Links)):
        # Skip items with mileage < 2000 and price < $350
        if category[0] == 'cars' and (miles_list[i] is not None and miles_list[i] < 2000 and price < 350):
            print(f"Skipped due to low mileage and price: {item} - {price}$, {miles_list[i]} miles")
            continue  # Skip this iteration

        cur.execute("SELECT item_id FROM Items WHERE Link = ?", (link,))
        result = cur.fetchone()
        print('insertion to Items table started')

        if result is None:
            cur.execute("""INSERT INTO Items(name, Link) VALUES(?, ?)""", (item, link))
            item_id = cur.lastrowid

            if category[0] != 'cars':
                print('inserting into ItemDetails Table')
                cur.execute("""INSERT INTO ItemDetails(item_id, category, price)
                               VALUES(?, ?, ?)""", (item_id, category[0], price))
            elif category[0] == 'cars':  # Only process cars
                brand, model, year = brand_list[i], model_list[i], year_list[i]
                miles = miles_list[i]

                # Ensure data is valid
                if miles is not None and miles > 0:
                    print('inserting into CarDetails Table')
                    cur.execute("""INSERT INTO CarDetails(item_id, make, model, year, price, miles)
                                   VALUES(?, ?, ?, ?, ?, ?)""", (item_id, brand, model, year, price, miles))
                    print(f"Inserted as car: {brand} {model} {year} with {miles} miles")
                else:
                    print(f"Skipped car: {brand} {model} {year} due to missing or invalid mileage")
        else:
            print(f"This link exists: {link}")

    con.commit()
    con.close()
    print('add data to sql finished')