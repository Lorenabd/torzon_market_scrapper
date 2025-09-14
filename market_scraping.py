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
from elements_scrapper import ElementsScrapper
import os


class ScrapingMarket:
    def __init__(self, main_driver, file_output_name):
        self.main_driver = main_driver
        self.file_output_name = file_output_name
        self.elements_scrapper = ElementsScrapper()
        self.config = self.read_json("./variables.json")
        self.window_continue = WindowContinue()
        self.window_info = WindowInfo()
        self.accept = self.window_info.get_result()
        if self.accept == True:
            self.get_data()

    def read_json(self, variables_file):
        with open(variables_file, "r") as file:
            config = json.load(file)
        return config

    def clear_dict_list_variables(self):
        self.config["user_info"]["user_level"] = []
        self.config["user_info"]["user_trust_level"] = []
        self.config["market_info"]["specialized"] = []
        self.config["user_info"]["join_year_user"] = []
        self.config["user_info"]["user_rating"] = []
        self.config["market_info"]["total_product"] = []
        self.config["sales_info"]["total_sales"] = []
        self.config["quality_info"]["total_reviews"] = []
        self.config["text"]["all"] = []
        self.config["user_info"]["user"] = []
        self.config["place_info"]["place"] = []
        self.config["market_info"]["price"] = []
        self.config["market_info"]["payment_method"] = []

        self.config["user_info"]["dict_user_level"] = {}
        self.config["user_info"]["dict_trust_user_level"] = {}
        self.config["user_info"]["dict_join_year_user"] = {}
        self.config["user_info"]["dict_user_rating"] = {}
        self.config["market_info"]["dict_total_product"] = {}
        self.config["sales_info"]["dict_total_sales"] = {}
        self.config["quality_info"]["dict_total_reviews"] = {}

    def continue_scrapping(self):
        result = self.window_continue.get_result()
        if result is None:
            print("Extraction finished.")
        else:
            print(f"Saving extracted data to “{result}”…\n")
            self.file_output_name = result
            self.get_data()

    def click_order_button(self, row_iteration, column_iteration):
        button = self.main_driver.find_element(
            By.XPATH,
            f".//tr[{row_iteration}]/td[{column_iteration}]/table/tbody/tr[2]/td[2]/a",
        )  # "ORDER" button
        self.main_driver.execute_script("arguments[0].scrollIntoView();", button)
        ActionChains(self.main_driver).key_down(Keys.CONTROL).click(button).key_up(
            Keys.CONTROL
        ).perform()

    def point_to_latest_opened_page(self):
        windows = self.main_driver.window_handles
        self.main_driver.switch_to.window(windows[-1])
        return windows

    def go_to_main_window(self, windows):
        self.main_driver.close()
        self.main_driver.switch_to.window(windows[0])

    def save_order_data(self, user_level_match, user_trust_level, market):
        self.config["user_info"]["user_level"].append(user_level_match)
        self.config["user_info"]["user_trust_level"].append(user_trust_level)
        self.config["market_info"]["specialized"].append(market)

    def click_profile_button(self, row_iteration, column_iteration):
        boton_user_profile = self.main_driver.find_element(
            By.XPATH,
            f".//tr[{row_iteration}]/td[{column_iteration}]/table/tbody/tr[2]/td[2]/h6/a",
        )
        self.main_driver.execute_script(
            "arguments[0].scrollIntoView();", boton_user_profile
        )
        ActionChains(self.main_driver).key_down(Keys.CONTROL).click(
            boton_user_profile
        ).key_up(Keys.CONTROL).perform()

    def save_user_data(
        self, join_date_user, user_rating, total_sales, reviews_user, total_products
    ):
        self.config["user_info"]["join_year_user"].append(join_date_user)
        self.config["user_info"]["user_rating"].append(user_rating)
        self.config["sales_info"]["total_sales"].append(total_sales)
        self.config["quality_info"]["total_reviews"].append(reviews_user)
        self.config["market_info"]["total_product"].append(total_products)

    def save_user_data_in_dicts(
        self,
        user_level_match,
        user_trust_level,
        user_rating,
        join_date_user,
        total_products,
        total_sales,
        reviews_user,
        username,
    ):
        if user_level_match is None:
            self.config["user_info"]["dict_user_level"][username] = "None"
        else:
            self.config["user_info"]["dict_user_level"][username] = user_level_match
        self.config["user_info"]["dict_trust_user_level"][username] = user_trust_level
        self.config["user_info"]["dict_user_rating"][username] = user_rating
        self.config["user_info"]["dict_join_year_user"][username] = join_date_user
        self.config["market_info"]["dict_total_product"][username] = total_products
        self.config["sales_info"]["dict_total_sales"][username] = total_sales
        self.config["quality_info"]["dict_total_reviews"][username] = reviews_user

    def get_data_from_dicts(self, username, market):
        self.config["user_info"]["user_level"].append(
            self.config["user_info"]["dict_user_level"].get(username)
        )
        self.config["user_info"]["user_trust_level"].append(
            self.config["user_info"]["dict_trust_user_level"].get(username)
        )
        self.config["market_info"]["specialized"].append(market)
        self.config["user_info"]["join_year_user"].append(
            self.config["user_info"]["dict_join_year_user"].get(username)
        )
        self.config["user_info"]["user_rating"].append(
            self.config["user_info"]["dict_user_rating"].get(username)
        )
        self.config["market_info"]["total_product"].append(
            self.config["market_info"]["dict_total_product"].get(username)
        )
        self.config["sales_info"]["total_sales"].append(
            self.config["sales_info"]["dict_total_sales"].get(username)
        )
        self.config["quality_info"]["total_reviews"].append(
            self.config["quality_info"]["dict_total_reviews"].get(username)
        )

    def save_product_info(
        self,
        product,
        clean_matches_user,
        index,
        filtered_place,
        price_match,
        payment_method_match,
    ):
        self.config["text"]["all"].append(product)
        self.config["user_info"]["user"].append(clean_matches_user[index])
        self.config["place_info"]["place"].append(filtered_place[index])
        self.config["market_info"]["price"].append(price_match[index])
        self.config["market_info"]["payment_method"].append(payment_method_match[index])

    def get_data(self):
        self.clear_dict_list_variables()
        matches = None
        price_match = None
        payment_method_match = None
        market = None
        user_level_match = None
        user_trust_level = None
        join_date_user = None
        user_rating = None
        total_sales = None
        reviews_user = None

        last_page = False

        user_name_row = []
        first_scrapping = True

        while True:

            tree = html.fromstring(self.main_driver.page_source)
            old_text = self.main_driver.find_element(
                By.XPATH, ".//td[1]/table/tbody/tr[1]/td/h6"
            ).text

            path_expression = (
                "/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr"
            )
            rows = tree.xpath(path_expression)
            row_iteration = 1
            column_iteration = 1

            for row in rows:
                matches = self.elements_scrapper.get_name_product(row)
                clean_matches_user = self.elements_scrapper.get_user(row)
                filtered_place = self.elements_scrapper.get_place(row)
                price_match = self.elements_scrapper.get_price(row)
                payment_method_match = self.elements_scrapper.get_payment_method(row)

                try:
                    if not last_page:
                        self.main_driver.find_element(By.LINK_TEXT, "NEXT")
                except NoSuchElementException as e:
                    print(f"Error: {e}")
                    print("----------------------------------------------")
                    print("Processing last page or the only one available")
                    last_page = True

                user_name_row = []

                for index, username in enumerate(
                    clean_matches_user
                ):  # goes through both users extracted
                    if (
                        matches[index] not in self.config["text"]["all"]
                    ):  # checks if prooduct has already been extracted
                        if not any(
                            username in sublist
                            for sublist in self.config["user_info"]["user"]
                        ):  # if user is not already saved
                            if (
                                username not in user_name_row
                            ):  # if user is duplicated in same row
                                self.click_order_button(row_iteration, column_iteration)
                                windows = self.point_to_latest_opened_page()
                                WebDriverWait(self.main_driver, 200).until(
                                    EC.presence_of_element_located(
                                        (
                                            By.XPATH,
                                            "/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button",
                                        )
                                    )
                                )

                                try:
                                    if first_scrapping:
                                        market = self.elements_scrapper.get_market(
                                            self.main_driver
                                        )

                                    user_level_match = (
                                        self.elements_scrapper.get_user_level(
                                            self.main_driver
                                        )
                                    )
                                    user_trust_level = (
                                        self.elements_scrapper.get_user_trust_level(
                                            self.main_driver
                                        )
                                    )
                                    self.go_to_main_window(windows)

                                except NoSuchElementException as e:
                                    print(f"Error: {e}")
                                    print(
                                        "----------------------------------------------"
                                    )
                                    self.go_to_main_window(windows)

                                time.sleep(1)
                                if not last_page:
                                    WebDriverWait(self.main_driver, 200).until(
                                        EC.presence_of_element_located(
                                            (By.LINK_TEXT, "NEXT")
                                        )
                                    )
                                self.save_order_data(
                                    user_level_match, user_trust_level, market
                                )
                                user_name_row.append(username)

                                self.click_profile_button(
                                    row_iteration, column_iteration
                                )
                                windows = self.point_to_latest_opened_page()
                                WebDriverWait(self.main_driver, 200).until(
                                    EC.presence_of_element_located(
                                        (
                                            By.XPATH,
                                            "/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr[1]/td[1]/font",
                                        )
                                    )
                                )
                                if column_iteration == 2:
                                    row_iteration += 1
                                    column_iteration = 1
                                else:
                                    column_iteration = 2
                                try:
                                    join_date_user = (
                                        self.elements_scrapper.get_join_date_user(
                                            self.main_driver
                                        )
                                    )
                                    user_rating = (
                                        self.elements_scrapper.get_user_rating(
                                            self.main_driver
                                        )
                                    )
                                    total_sales = (
                                        self.elements_scrapper.get_total_sales(
                                            self.main_driver
                                        )
                                    )
                                    reviews_user = (
                                        self.elements_scrapper.get_reviews_user(
                                            self.main_driver
                                        )
                                    )
                                    total_products = (
                                        self.elements_scrapper.get_total_products(
                                            self.main_driver
                                        )
                                    )
                                    self.go_to_main_window(windows)
                                except:
                                    self.go_to_main_window(windows)
                                    break
                                time.sleep(1)
                                self.save_user_data(
                                    join_date_user,
                                    user_rating,
                                    total_sales,
                                    reviews_user,
                                    total_products,
                                )

                                if (
                                    username
                                    not in self.config["user_info"][
                                        "dict_user_level"
                                    ].keys()
                                ):
                                    self.save_user_data_in_dicts(
                                        user_level_match,
                                        user_trust_level,
                                        user_rating,
                                        join_date_user,
                                        total_products,
                                        total_sales,
                                        reviews_user,
                                        username,
                                    )

                            else:
                                if column_iteration == 2:
                                    row_iteration += 1
                                    column_iteration = 1
                                else:
                                    column_iteration = 2
                                self.get_data_from_dicts(username, market)

                        else:
                            if column_iteration == 2:
                                row_iteration += 1
                                column_iteration = 1
                            else:
                                column_iteration = 2
                            self.get_data_from_dicts(username, market)

                    else:
                        print(
                            f"Product {matches[index]} is duplicated and won't be saved again"
                        )

                for index, product in enumerate(matches):
                    if product not in self.config["text"]["all"]:
                        self.save_product_info(
                            product,
                            clean_matches_user,
                            index,
                            filtered_place,
                            price_match,
                            payment_method_match,
                        )

            try:

                if first_scrapping:
                    first_scrapping = False
                    try:
                        self.main_driver.find_element(By.LINK_TEXT, "NEXT")
                    except NoSuchElementException:
                        print("There is only one page")
                        break

                if last_page:
                    print("No more available pages")
                    break
                next_page = WebDriverWait(self.main_driver, 200).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "NEXT"))
                )
                next_page = WebDriverWait(self.main_driver, 200).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "NEXT"))
                )
                next_page.click()
                time.sleep(5)
                WebDriverWait(self.main_driver, 200).until(
                    lambda driver: driver.find_element(
                        By.XPATH, ".//td[1]/table/tbody/tr[1]/td/h6"
                    ).text
                    != old_text
                )
                time.sleep(5)
                print("Next page loaded...")

                try:
                    self.main_driver.find_element(By.LINK_TEXT, "NEXT")
                except NoSuchElementException:
                    print("Processing last page or the only one available")
                    last_page = True

            except:
                print("No more avaialable pages")
                break

        df_data_extracted = pd.DataFrame(
            {
                "Name Product": self.config["text"]["all"],
                "Seller": self.config["user_info"]["user"],
                "Origin": self.config["place_info"]["place"],
                "Price": self.config["market_info"]["price"],
                "Payment Method": self.config["market_info"]["payment_method"],
                "User Level": self.config["user_info"]["user_level"],
                "User Trust Level": self.config["user_info"]["user_trust_level"],
                "User Reviews": self.config["quality_info"]["total_reviews"],
                "Specialized": self.config["market_info"]["specialized"],
                "Join Date": self.config["user_info"]["join_year_user"],
                "User Rating": self.config["user_info"]["user_rating"],
                "User Products": self.config["market_info"]["total_product"],
                "Total Sales": self.config["sales_info"]["total_sales"],
            }
        ).sort_values(by="Seller")
        os.makedirs("DATA_EXTRACTED", exist_ok=True)
        df_data_extracted.to_excel(
            os.path.join("DATA_EXTRACTED", f"{self.file_output_name}.xlsx"), index=True
        )
        df_data_extracted.to_csv(
            os.path.join("DATA_EXTRACTED", f"{self.file_output_name}.csv"),
            index=False,
            sep=",",
        )
        self.continue_scrapping()
