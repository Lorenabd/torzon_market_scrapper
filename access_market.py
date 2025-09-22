from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QLineEdit,
)
from lxml import html
from market_scraping import ScrapingMarket
import os


class AccessMarket:
    def __init__(self):
        options = self.set_options()
        self.execute_browser(options)

    def set_options(self):
        options = Options()
        options.binary_location = f"{os.getenv('BROWSER')}/tor-browser/Browser/firefox"
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", 9051)
        options.set_preference("network.proxy.socks_remote_dns", True)
        options.set_preference("javascript.enabled", False)
        return options

    def execute_browser(self, options):
        main_driver = webdriver.Firefox(options=options)
        connect_button = main_driver.find_element(By.XPATH, '//*[@id="connectButton"]')
        connect_button.click()
        time.sleep(10)
        url = "http://torzon4kv5swfazrziqvel2imhxcckc4otcvopiv5lnxzpqu4v4m5iyd.onion"  # Torzon URL
        main_driver.get(url)

        WebDriverWait(main_driver, 300).until(  # 5 minutes
            EC.presence_of_element_located((By.XPATH, "/html/body/nav[1]/div/a[1]/img"))
        )
        self.pop_up_info(main_driver)

    def pop_up_info(self, main_driver):
        app = QApplication(sys.argv)
        window = QWidget()
        window.setWindowTitle("Important information!")

        message = QLabel(
            "Navigate to the category where you want to start\n scrapping and press CONTINUE to start."
        )
        input_label = QLabel("Enter the name of the output file:")
        input_field = QLineEdit()
        continue_button = QPushButton("Continue")

        continue_button.clicked.connect(
            lambda: self.close_pop_up_info(window, main_driver, input_field.text())
        )

        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addWidget(input_field)
        layout.addWidget(message)
        layout.addWidget(continue_button)

        window.setLayout(layout)
        window.setGeometry(400, 400, 300, 150)
        window.show()

        app.exec_()

    def close_pop_up_info(self, window, main_driver, file_output):
        window.close()
        print("Starting extraction...")
        ScrapingMarket(main_driver, file_output)


if __name__ == "__main__":
    market = AccessMarket()
