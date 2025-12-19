import time
import random
import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.models.lead import Lead
from src.agent.sources.base_source import BaseSource

class GoogleMapsScraper(BaseSource):
    """
    A class to scrape Google Maps for business information.
    """
    def __init__(self, query: str, num_pages: int = 1):
        """
        Initializes the scraper and sets up the Selenium WebDriver.
        """
        self.query = query
        self.num_pages = num_pages
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()

    def scrape(self) -> List[Lead]:
        """
        Scrapes Google Maps for a given query.
        """
        self.driver.get("https://www.google.com/maps")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )

        search_box = self.driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(self.query)
        search_box.send_keys(Keys.ENTER)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
            )
        except TimeoutException:
            logging.warning("Timed out waiting for search results to load.")
            return []

        results = []
        feed = self.driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        for i in range(self.num_pages):
            links = [el.get_attribute('href') for el in feed.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")]

            for link in links:
                original_window = self.driver.current_window_handle
                self.driver.execute_script("window.open(arguments[0]);", link)
                WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))

                for window_handle in self.driver.window_handles:
                    if window_handle != original_window:
                        self.driver.switch_to.window(window_handle)
                        break

                lead_details = self._scrape_place_details()
                if lead_details:
                    results.append(Lead(**lead_details))

                self.driver.close()
                self.driver.switch_to.window(original_window)
                time.sleep(random.uniform(1, 2))

            if i < self.num_pages - 1:
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next page']"))
                    )
                    next_button.click()
                    WebDriverWait(self.driver, 10).until(
                        EC.url_changes(self.driver.current_url)
                    )
                    time.sleep(random.uniform(1, 3))
                except TimeoutException:
                    break

        return results

    def _scrape_place_details(self):
        """
        Scrapes business details from the current Google Maps place page.
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
            )
        except TimeoutException:
            logging.warning(f"Timed out waiting for details to load for {self.driver.current_url}")
            return None

        try:
            name = self.driver.find_element(By.CSS_SELECTOR, "h1").text
        except NoSuchElementException:
            name = None

        def extract_aria_label_info(label):
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, f"[aria-label*='{label}']")
                full_label = element.get_attribute("aria-label")
                return full_label.split(label, 1)[1].strip()
            except (NoSuchElementException, IndexError):
                return None

        address = extract_aria_label_info("Address:")
        website = extract_aria_label_info("Website:")
        phone = extract_aria_label_info("Phone:")

        city = None
        if address:
            # A simple way to get the city, might need to be more robust
            city = address.split(',')[-2].strip() if ',' in address else None


        try:
            category = self.driver.find_element(By.XPATH, "//button[contains(@jsaction, 'category')]").text
        except NoSuchElementException:
            category = None

        return {
            "name": name,
            "company": name,
            "city": city,
            "website": website,
            "phone": phone,
            "notes": f"Category: {category}",
            "source": "Google Maps"
        }
