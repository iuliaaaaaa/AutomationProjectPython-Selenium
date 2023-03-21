from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import json


options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--disable-extensions")
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

chrome_driver_path="C:\chromedriver\chromedriver.exe"
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


driver.get("https://nvd.nist.gov/vuln/search")
predefined_keywords = "medical"
response = input("Do you want to search with the predefined keywords? Y/N: ")

if response == "Y":
    driver.find_element(by="id", value="Keywords").send_keys(predefined_keywords)
else:
    keyword = input("Enter keywords: ")
    driver.find_element(by="id", value="Keywords").send_keys(keyword)


driver.find_element(by="id", value="vuln-search-submit").click()

driver.implicitly_wait(2)

table = driver.find_element(By.CSS_SELECTOR, ".table.table-striped.table-hover")

a = table.find_elements(By.TAG_NAME, "a")

page_links = driver.find_element(By.CLASS_NAME, 'pagination')
pages = page_links.find_elements(By.TAG_NAME, 'a')
pages_list = []

for page in pages:
    if page.text.count('>') > 0:
        pages_list.append(page)

for page in pages_list:
    i = 0
    while i < len(a):
        driver.implicitly_wait(2)
        table = driver.find_element(By.CSS_SELECTOR, ".table.table-striped.table-hover")
        a = table.find_elements(By.TAG_NAME, "a")
        if a[i].text.count("CVE") > 0:
            a[i].click()
            driver.implicitly_wait(1)
            vuln_id = driver.find_element(By.XPATH, '//*[@id="vulnDetailTableView"]/tbody/tr/td/h2/span').text
            vuln_description = driver.find_element(By.XPATH, '//*[@id="vulnDetailTableView"]/tbody/tr/td/div/div[1]/p').text
            vuln_references_table = driver.find_element(By.XPATH, '//*[@id="vulnHyperlinksPanel"]/table')
            vuln_references_list = vuln_references_table.find_elements(By.TAG_NAME, 'a')
            vuln_references = ''
            for ref in vuln_references_list:
                vuln_references += f'{ref.text} '

            vuln_impact = driver.find_element(By.ID, 'Vuln3CvssPanel')

            driver.implicitly_wait(1)

            try:
                vuln_cpe = driver.find_element(By.XPATH, '//*[@id="config-div-1"]/table/tbody/tr/td/b').text
            except NoSuchElementException:
                vuln_cpe = "There is no CPE specification here"

            vuln_cwe = driver.find_element(By.XPATH, '//*[@id="vulnTechnicalDetailsDiv"]/table/tbody/tr/td[1]').text

            try:
                impact_links = vuln_impact.find_elements(By.TAG_NAME, "a")
                driver.implicitly_wait(1)
                if impact_links[0].text == 'N/A' and len(impact_links) > 1:
                    impact_links[1].click()
                else:
                    impact_links[0].click()
                driver.implicitly_wait(3)
                impact_score = driver.find_element(By.ID, 'cvss-impact-score-cell').text
            except NoSuchElementException:
                impact_score = "There is no recorded score of the impact."

            driver.implicitly_wait(2)
            driver.back()
            driver.implicitly_wait(2)
            driver.back()
            driver.implicitly_wait(2)

            data = [
                {'id': f'{vuln_id}',
                 'description': f'{vuln_description}',
                 'impact': f'{impact_score}',
                 'references': f'{vuln_references}',
                 'cpe': f'{vuln_cpe}',
                 'cwe': f'{vuln_cwe}'},
            ]

            with open("data_output.json", "a") as file:
                json.dump(data, file, indent=4, sort_keys=True)

            i += 1
        else:
            i += 1
