import re
from math import ceil
from random import randint
from time import sleep

import requests
from bs4 import BeautifulSoup

import pandas as pd

# Required Variables
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43"


def extract_info(info):
    """Extract all data in one full page"""
    business_name = info.select_one(".business-name").text
    category = [categories.text for categories in info.select(".categories a")]
    rating_tag = info.select_one(".result-rating")
    if rating_tag:
        word2num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        rating = word2num.get(rating_tag["class"][1])
        review = rating_tag.text.strip()
    else:
        rating, review = None, None
    phone = info.select_one(".phones")
    phone = phone.text.strip() if phone else None
    year = info.select_one(".number")
    year = year.text.strip() if year else None
    website = info.select_one(".links a")
    website = website["href"] if website else None
    street = info.select_one(".street-address")
    street = street.text.strip() if street else None
    city = info.select_one(".locality")
    city = city.text.strip() if city else None
    return {
        "business_name": business_name,
        "category": category,
        "rating": rating,
        "review": review,
        "year": year,
        "website": website,
        "phone": phone,
        "street": street,
        "city": city,
    }


def main(URL: str, FILE_PATH: str):
    """This function starts the scraping process with parameters:
    URL (e.g., yellowpages.com/) and FILE_PATH (e.g., D:/Python Pro/Output/output.csv)"""
    response = requests.get(URL, headers={"User-Agent": USER_AGENT})
    soup = BeautifulSoup(response.content, "html.parser")
    info_list = []
    page = 1
    index_tag = soup.select_one(".showing-count")
    if index_tag:
        total_index_text = index_tag.text
        print(f"Total index text: {total_index_text}")  # Debug print

        # Extract the number using regex
        match = re.search(r'of\s+(\d+)', total_index_text)
        if match:
            total_items = int(match.group(1).replace(',', ''))
            total_page = ceil(total_items / 30)
            print(f"Total items: {total_items}, Total pages: {total_page}")  # Debug print
        else:
            print("Error finding total number of items")
            return
    else:
        print("Could not find .showing-count element")
        return

    while page <= total_page:
        if page > 1:
            sleep(randint(10, 20))
            url = f"{URL}&page={page}"
            print(f"Opening page {page} with URL: {url}")
            response = requests.get(url, headers={"User-Agent": USER_AGENT})
            soup = BeautifulSoup(response.content, "html.parser")

        infos = soup.find_all("div", class_="result")
        if not infos:
            print("No more results found.")
            break

        info_list.extend(extract_info(info) for info in infos)
        print(f"Extracted {len(infos)} records from page {page}")

        # Save data every 5 pages and on the last page
        if page % 5 == 0 or page == total_page:
            print("Saving data to CSV")
            df = pd.DataFrame(info_list)
            df.to_csv(FILE_PATH, index=False, mode='a', header=not bool(page % 5))
            info_list = []

        page += 1

    # Save any remaining data
    if info_list:
        print("Saving final batch of data to CSV")
        df = pd.DataFrame(info_list)
        df.to_csv(FILE_PATH, index=False, mode='a', header=False)

    print("Data Extraction Complete")


if __name__ == "__main__":
    URL = input("Enter yellow_page URL: ")
    FILE_PATH = input("Enter file path with filename.csv: ")
    main(URL, FILE_PATH)
