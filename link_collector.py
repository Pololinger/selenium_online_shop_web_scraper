import time
import pandas as pd
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException   ### braucht mer net
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By





keyword = 'bambus socken' #### enter search keyword here e.g. 'duftkerzen', 'bambus socken' 

url = 'https://www.dm.de/search?query='+keyword+'&searchType=product'

drogerie_links = []


driver = webdriver.Chrome(executable_path=r"") #### specify path to your chromedriver.exe 
driver.get(url)



cookie = driver.find_element_by_id('cookiebar-ok').click()
time.sleep(10)

while True:
    try:
        next_link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "load-more-products-button")))
        next_link.click()
        driver.implicitly_wait(5)
    except StaleElementReferenceException:
        break
    except TimeoutException:
        break 
        
time.sleep(5)
listing = driver.find_elements_by_class_name('dv')[-1]
a_elements = listing.find_elements_by_tag_name('a')
    
    
for e in a_elements:
    drogerie_links.append(e.get_attribute('href'))
    


print('Link collection completed')
drogerie_links = list(set(drogerie_links)) #### keep unique links 

print('Number of links collected: ', len(drogerie_links))