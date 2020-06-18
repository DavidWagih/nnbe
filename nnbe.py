from selenium import webdriver
import csv
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
import base64
import re
import os
from os import listdir
import shutil


#default folder to save data to
DIR_PATH="ALL_FILES2"
try:
    os.mkdir(DIR_PATH)
except:
    pass

#Add chromedriver options and initialize it
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
  "download.default_directory": r"{}".format(os.getcwd()+"\\"+DIR_PATH),
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.default_content_setting_values.automatic_downloads": 1
})
driver = webdriver.Chrome(chrome_options=options)

#function to pass the captcha if appeard
# replace API_KEY with your key from the 2captcha site
def checker():
    try:
        WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'clntcap_frame')))
        
        # Add these values
        API_KEY = 'API_KEY'  # Your 2captcha API KEY
        
        base=driver.find_element_by_xpath('//*[@id="captchide"]/div[2]/div/p[2]/img').get_attribute("src")
        imgdata = base64.b64decode(base.split(",")[1]+"==")
        filename = 'imageToSave.png'
        with open(filename, 'wb') as f:
            f.write(imgdata)
            
        url = 'http://2captcha.com/in.php'
        files = {'file': open('imageToSave.png', 'rb')}
        data = {'key': API_KEY, 'method': 'post'}
        r = requests.post(url, files=files, data=data)
        if r.ok:
            pass

        s = requests.Session()
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, r.text.split('|')[1])).text

        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            time.sleep(5)
            recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, r.text.split('|')[1])).text.split('|')[1]
        print(recaptcha_answer)

        driver.find_element_by_xpath('//*[@id="ans"]').send_keys(recaptcha_answer)
        driver.find_element_by_xpath('//*[@id="jar"]').click()
        driver.get('https://cri.nbb.be/bc9/web/catalog?execution=e1s1')

    except:
        pass



inc=1

# read all numbers in the list one by one and do search
with open("numbers.txt") as fp: 
    Lines = fp.readlines() 
    for line in Lines:
        
        
        line=line.replace('\n','')

        print(str(inc))
        inc+=1
        
        driver.get('https://cri.nbb.be/bc9/web/catalog?execution=e1s1')

        #check for captcha page if appeared
        ## remove hashtag from next line so it can capture captcha and pass it,also make sure you added API_KEY previously
        ##checker() 
        
        driver.find_element_by_xpath('//*[@id="page_searchForm:j_id3"]/div[1]/ul/li[1]/a').click()
        driver.find_element_by_xpath('//*[@id="page_searchForm:j_id3:generated_number_2_component"]').clear()
        driver.find_element_by_xpath('//*[@id="page_searchForm:j_id3:generated_number_2_component"]').send_keys(line)
        search=driver.find_element_by_xpath('//*[@id="page_searchForm:actions:0:button"]/span').click()
        time.sleep(5)
        
        try:
            driver.find_element_by_xpath('//*[@id="j_idt131:j_idt165"]/div/div[1]/div/div[3]/select/option[4]').click()
        except:
            continue
        time.sleep(2)

        # loop over each download file link, click it and download to the default folder
        tbl2=driver.find_element_by_xpath('//*[@id="j_idt131:j_idt165_data"]')
        number_of_downloaded_files=0
        for n1,tr in enumerate(tbl2.find_elements_by_tag_name('tr')):
            td=tr.find_elements_by_tag_name('td')
            if td[7].text=="Download":
                number_of_downloaded_files+=1
                t=td[7].find_element_by_tag_name('a')
                driver.execute_script(t.get_attribute("onClick").split(';')[1])

        #make sure no files are still downloading
        while(1):
            l=[f for f in listdir(DIR_PATH) if "crdownload" in f]
            l2=[f for f in listdir(DIR_PATH) if "xbrl" in f]
            if len(l)>0 or len(l)+len(l2)<number_of_downloaded_files:
                time.sleep(5)
            elif len(l)==0:
                break
        # add all downloaded file in the subfolder with the name of its company number    
        while(1):
            l=[f for f in listdir(DIR_PATH) if "xbrl" in f]
            if len(l)>0:
                for f in l:
                #if "xbrl" in f:
                    try:
                        os.mkdir(DIR_PATH+"/"+line)
                    except:
                        pass
                    shutil.move(DIR_PATH+"/"+f,DIR_PATH+"/"+line+"/"+f)
            elif len(l)==0:
                break

