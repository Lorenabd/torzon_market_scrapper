from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import regex as re
import time
from pop_up_continue import WindowContinue
from info_window import WindowInfo
import json
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


class ElementsScrapper:
    def __init__(self):
        pass

    def get_name_product(self, row):
        matches = row.xpath(".//td/table/tbody/tr[1]/td/h6//text()")
        matches = [t.strip() for t in matches if t.strip()]
        print(f"Extracting {matches}")
        return matches

    def get_user(self, row):
        matches_user = None
        matches_user = row.xpath(".//td/table/tbody/tr[2]/td[2]/h6/a/font/text()")
        matches_user = [
            re.match(r"^[^(]+", elem).group().strip()
            for elem in matches_user
            if re.match(r"^[^(]+", elem)
        ]
        clean_matches_user = [item for item in matches_user if item != ")"]
        return clean_matches_user

    def get_place(self, row):
        place_match = None
        place_match = row.xpath(".//td/table/tbody/tr[2]/td[2]/h6/text()")
        place_match = [t.strip() for t in place_match if t.strip()]
        if len(place_match) < 5:
            filtered_place = [place_match[1]]
        else:
            filtered_place = [place_match[1], place_match[4]]
        return filtered_place

    def get_price(Self, row):
        price_match = row.xpath(".//td/table/tbody/tr[2]/td[2]/h6/b/font/font/text()")
        price_match = [t.strip() for t in price_match if t.strip()]
        return price_match

    def get_payment_method(self, row):
        payment_method_match = row.xpath(
            ".//td/table/tbody/tr[2]/td[1]/center/button/text()"
        )
        payment_method_match = [t.strip() for t in payment_method_match if t.strip()]
        return payment_method_match

    def get_market(self, main_driver):
        market = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/h6/font",
        ).text
        return market

    def get_user_level(self, main_driver):
        user_level_match = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button",
        ).text
        user_level_match = re.search(r"\d+", user_level_match)
        if user_level_match:
            user_level_match = user_level_match.group()
        return user_level_match

    def get_join_date_user(self, main_driver):
        join_date_user = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/h6",
        ).text
        return join_date_user

    def get_user_rating(self, main_driver):
        user_rating = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/h6/b",
        ).text
        user_rating = re.search(r"[\d.]+", user_rating)
        if user_rating:
            user_rating = user_rating.group()
        return user_rating

    def get_user_trust_level(self, main_driver):
        user_trust_level = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/button",
        ).text

        user_trust_level = re.search(r"\d+", user_trust_level)
        if user_trust_level:
            user_trust_level = user_trust_level.group()
        return user_trust_level

    def get_total_sales(self, main_driver):
        total_sales = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/center/h6/font[1]/b/button",
        ).text
        total_sales = total_sales.strip()
        return total_sales

    def get_reviews_user(self, main_driver):
        reviews_user = main_driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr[1]/td[1]/center/table/tbody/tr[2]/td/h6/a",
        ).text

        reviews_user = re.search(r"\d+", reviews_user)
        if reviews_user:
            reviews_user = reviews_user.group()
        return reviews_user

    def get_total_products(self, main_driver):
        tbody_struct = main_driver.find_elements(
            By.XPATH,
            "/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[2]/tbody/tr[2]/td/table/tbody/tr",
        )

        total_products = 0
        for tr in tbody_struct:
            td_struct = tr.find_elements(By.XPATH, "./td")
            contador = 0
            for td in td_struct:
                contador = contador + 1
                num_product_selling = td.text
                num_product_selling = re.search(r"\d+", num_product_selling)
                if num_product_selling:
                    num_product_selling = num_product_selling.group()
                total_products = total_products + int(num_product_selling)
        return total_products
