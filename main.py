import time
import pandas as pd
import json
import selenium
import re 
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException   
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By


import link_collector as lc


driver = webdriver.Chrome(executable_path=r"") #### specify path to your chromedriver.exe 


def get_review(link):
    driver.get(link)
    time.sleep(10)
    
    #### collect general data about the product 

    artikelnummer = driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div[2]/p').text   #### product id 
    artikelnummer = re.findall(r'\d+', artikelnummer)[0]

    overall_rating = driver.find_element_by_xpath('//*[@id="ratings-summary"]/div[2]').text                                                        #### overall product rating 
    category = driver.find_element_by_xpath('//*[@id="dm-view"]/div/div/span[2]/a').text                                                           #### product category  
                                                            
                                           
    price_digit = driver.find_element_by_css_selector('span[data-dmid = "price-digit"' ).text                                                      #### price digit before the delimiter
    price_cent = driver.find_element_by_css_selector('span[data-dmid = "price-cent"' ).text                                                        #### price digit after the delimiter
   
    price_euro = price_digit +'.'+price_cent        

    rating_list = []    
    author_list = []
    date_list = []  
    review_headline_list = []
    review_list = []



    #### collect the text reviews 

    condition = True
    while condition:
        driver.implicitly_wait(5)

        content_container = driver.find_element_by_class_name('bv-content-list-container')
        rating = content_container.find_elements_by_class_name('bv-content-rating.bv-rating-ratio')
        for e in rating:                                                                                       #### extract the first digit from the rating string, which is the actual rating (1-5 Stars)
            rating_list.append(re.search(r'\d', e.text).group()) 


        author = content_container.find_elements_by_class_name('bv-content-reference-data.bv-content-author-name')

        for e in author:
            author_list.append(e.text.split(' ·')[0])
            date_list.append(e.text.split('· ')[1])


        review_headline = content_container.find_elements_by_class_name('bv-content-title-container')

        for e in review_headline:
            review_headline_list.append(e.text)


        review_text = content_container.find_elements_by_class_name('bv-content-summary-body-text')

        for e in review_text: 
            review_list.append(e.text)

        try: 
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'cookiebar-ok'))).click()      ### click cookie banner if there, it might block going to the next review page

            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="BVRRContainer"]/div/div/div/div/div[3]/div/ul/li[2]/a'))).click()   #### click next review page button (if there)


  
       
        except StaleElementReferenceException:
            condition = False

        except TimeoutException:
            condition = False   
        
        except NoSuchElementException:
            condition = False 

    
        df = pd.DataFrame({'date': date_list, 'author': author_list, 'rating': rating_list,'review_text':review_list,                                                 #### store lists as pandas df 
                   'review_headline': review_headline_list,
                   'product_id': artikelnummer, 'category': category, 'price': price_euro, 'overall_rating': overall_rating})
     
    
        json_file = (df.groupby(['date','author','rating','review_headline','review_text'], as_index=False)                                                           #### pandas df to json
             .apply(lambda x: x[['product_id','category','price','overall_rating']].to_dict('r'))
             .reset_index()
             .rename(columns={0:'product_data'})
             .to_json(orient='records'))
        
        with open('json_files/'+artikelnummer+'_reviews.json', 'w') as f:
             json.dump(json_file, f, indent=2, sort_keys=False)






for e in lc.drogerie_links:

    get_review(e)



