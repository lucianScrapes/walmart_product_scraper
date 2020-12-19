from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import time
import xlsxwriter
import zipfile
import requests
import json
from sqllitelib import *
import pandas as pd

walmart_start_page = sys.argv[1]
filename = sys.argv[2]
file_type = None


#if we're storing in xlsx/csv, file will be created at the end
if '.xlsx' in filename:
    file_type = 'xlsx'
elif '.db' in filename:
    file_type = 'sqllite'
    sql_db_name = filename
elif '.csv' in filename:
    file_type = 'csv'

if file_type is None:
    print("please specify a filename with file extension")
    exit()

if len(sys.argv) > 3:
    proxy = sys.argv[3]
else:
    proxy = None


with open("2CAPTCHA_API.txt",'r') as f:
    _2CAPTCHA_API_KEY = f.read().strip()

def check_exists_by_xpath(webdriver,xpath):
    try:
        webdriver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def click_on(selenium_driver,XPATH):
    print("Clicking on -> " + XPATH + "\n")
    try:
        element_present = EC.presence_of_element_located((By.XPATH, XPATH))
        WebDriverWait(selenium_driver, 5).until(element_present)
    except TimeoutException:
        print ("Timed out waiting for page to load\n")
        return -1
    tries = 3
    if element_present is not None:
        while(tries!=0):
            tries = tries - 1
            try:
                selenium_driver.find_element_by_xpath(XPATH).click()
                time.sleep(1)
                return 1
            except:
                time.sleep(5)
                print("RETRYING \n")
                try:
                    element = selenium_driver.find_element_by_xpath(XPATH)
                    selenium_driver.execute_script("arguments[0].click();", element)
                    return 1
                except:
                    time.sleep(5)
                    print("Click not working\n")
        print("Other error \n")

def reCaptcha(url,googlkey,_2CAPTCHA_API_KEY,method,invisible):
    ENDPOINT = 'http://2captcha.com/in.php'
    payload = {
        'key': _2CAPTCHA_API_KEY,
        'method': method,
        'googlekey': googlkey,
        'pageurl': url,
        'invisible' : invisible,
        'json' : '1'
    }
    fail = 1
    tries = 0
    while(fail == 1 and tries < 5):
        response = requests.get(ENDPOINT, params=payload)
        result = response.json()
        print (result['status'])
        print (result['request'])
        if result['status'] == 1:
            fail = 0
        else:
            fail = 1
            tries = tries + 1
    if result['status'] == 0:
        return 0

    req_id = result['request']
    time.sleep(20)
    fail = 1
    tries = 0
    while(fail == 1 and tries < 50):
        ENDPOINT2 = 'http://2captcha.com/res.php'
        payload2 = {
            'key': _2CAPTCHA_API_KEY,
            'action': 'get',
            'id': req_id,
            'json' : '1'
        }
        response2 = requests.get(ENDPOINT2, params=payload2)
        result2 = response2.json()
        print (result2['status'])
        print (result2['request'])
        if result2['status'] == 0:
            fail = 1
            tries = tries + 1
            time.sleep(5)
        if 'UNSOLVABLE' in result2['request']:
            return 0
        if result2['status'] == 1:
            token = result2['request']
            fail = 0
            return token
    return 0

def driver_captcha_support(driver,url):
    driver.get(url)
    time.sleep(4)
    if 'Verify your identity' in driver.title:
        token = reCaptcha(driver.current_url,'6Lcj-R8TAAAAABs3FrRPuQhLMbp5QrHsHufzLf7b',_2CAPTCHA_API_KEY,'userrecaptcha',0)
        if token == 0:
            print("Error Handling Captcha, Stopping Program")
            driver.quit()
            exit()
        #driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % token)
        #time.sleep(1)
        driver.execute_script('handleCaptcha("%s")' % token)
        time.sleep(3)
        driver_captcha_support(driver,url)
    else:
        return 1

def proxy_extension(proxy):
    proxy_details = proxy.split(":")
    PROXY_HOST = proxy_details[0]
    PROXY_PORT = int(proxy_details[1])
    PROXY_USER = proxy_details[2]
    PROXY_PASS = proxy_details[3].replace("\n", "")
    print(PROXY_HOST)
    print(PROXY_PORT)
    print(PROXY_USER)
    print(PROXY_PASS)


    manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%(host)s",
                port: parseInt(%(port)d)
              },
              bypassList: ["foobar.com"]
            }
          };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%(user)s",
                password: "%(pass)s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
        """ % {
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "user": PROXY_USER,
            "pass": PROXY_PASS,
        }
    pluginfile = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return pluginfile

if __name__ == "__main__":
    if file_type == 'sqllite':
        if path.exists(sql_db_name) is False:
            conn = create_connection(sql_db_name)
        else:
            conn = sqlite3.connect(sql_db_name)

    products = {}
    co = Options()
    if proxy is not None:
        pluginfile = proxy_extension(proxy)
        co.add_extension(pluginfile)
    co.add_argument("--mute-audio")
    #co.add_extension(r'UBLOCK.crx')
    driver = webdriver.Chrome(options=co)
    driver.get('https://google.com/')
    driver.execute_script('''window.open("https://www.walmart.com/","_blank");''')
    time.sleep(5)
    driver.close()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)
    driver_captcha_support(driver,walmart_start_page)
    time.sleep(5)
    page_numbers = driver.find_element_by_xpath('//*[@id="mainSearchContent"]/div[3]/div[2]/ul/li[8]/a').text
    print(str(page_numbers) + " pages to scrape.")

    for page in range(1,int(page_numbers)+1):
        if '&povid' in walmart_start_page:
            walmart_start_page = walmart_start_page.replace('?page=' + str(int(page)-1),'?page=' + str(page))
            driver_captcha_support(driver,walmart_start_page)
        elif '?povid=' in walmart_start_page:
            url_list = walmart_start_page.split('?povid')
            walmart_start_page = url_list[0] + '?page=' + str(page) + '&povid' + url_list[1]
            driver_captcha_support(driver,walmart_start_page)
        elif '?query=' in walmart_start_page:
            url_list = walmart_start_page.split('?query=')
            walmart_start_page = url_list[0] + '?page=' + str(page) + '&ps=40&query='+ url_list[1]
            driver_captcha_support(driver,walmart_start_page)
        elif '&query=' in walmart_start_page:
            walmart_start_page = walmart_start_page.replace('?page=' + str(int(page)-1),'?page=' + str(page))
            driver_captcha_support(driver,walmart_start_page)
        else:
            driver_captcha_support(driver,walmart_start_page + '?page='  + str(page))
        time.sleep(5)
        for i in range(1,40):
            try:
                #product_title = driver.find_element_by_xpath('//*[@id="searchProductResult"]/ul/li['+ str(i) +']/div/div[2]/div[5]/div/a').get_attribute('href').split("/")[-2].replace("-"," ")
                product_id = driver.find_element_by_xpath('//*[@id="searchProductResult"]/ul/li['+ str(i) +']/div/div[2]/div[5]/div/a').get_attribute('href').split("/")[-1].split("?")[0]
                product_title = driver.find_element_by_xpath('//*[@id="searchProductResult"]/ul/li['+ str(i) +']/div/div[2]/div[2]/a/div/img').get_attribute('alt') #image alt contains the product title
                product_price = driver.find_element_by_xpath('//*[@id="searchProductResult"]/ul/li['+ str(i) +']/div/div[2]/div[7]/div/span/span/span[2]/span/span[1]').text.split("\n")
                if len(product_price) > 2:
                    product_price = product_price[1] + product_price[3]
                    product_price = product_price.replace(" -",' - ')
                else:
                    product_price = product_price[0]
                try:
                    print(product_id + " " + product_title + " " + product_price)
                except:
                    print("Error Printing Current Product Details")
                if file_type == 'sqllite':
                    insertProduct(conn,int(product_id),product_title,product_price)
                products[product_id] = [product_title,product_price]
            except:
                pass #less than 40 products on the page

    if file_type == 'xlsx':
        print("Creating Workbook")
        workbook = xlsxwriter.Workbook(xlsx_filename)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'Id')
        worksheet.write(0, 1, 'Name')
        worksheet.write(0, 2, 'Price')
        row = 1
        for key in products:
            worksheet.write(row, 0, key)
            worksheet.write(row, 1, products[key][0])
            worksheet.write(row, 2, products[key][1])
            row += 1

        workbook.close()
    if file_type == 'csv':
        print("Creating CSV File:")
        df = pd.DataFrame(products)
        df.T.reset_index().to_csv(filename,header=False,index=False)
    driver.quit()
    print("Done!")



#scrape_products.py https://www.walmart.com/browse/top-selling-items data.csv
