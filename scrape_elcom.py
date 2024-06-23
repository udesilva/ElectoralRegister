import sys
import urllib.parse
import time  # Import if you plan to use time.sleep()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Create a Service object using ChromeDriverManager to manage the driver installation
service = Service(ChromeDriverManager().install())

# Now, instead of using desired_capabilities, you initialize the WebDriver with the Service object
driver = webdriver.Chrome(service=service)

def wait_for_xpath(url, xpath):
    global driver

    driver.get(url)

    try:
        wait_for_xpath = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return True

    except Exception as e:
        print(f"Exception {e} waiting for {xpath} in {url}")
        # logs = driver.get_log('browser')
        # for log in logs:
        #     print(log,file=sys.stderr)
        return None


def match_address(address):

    addresses = driver.find_elements_by_class_name('polling-station__list')

    if len(addresses) == 0:
        print("No addresses found for {postcode}!")
        return None
    
    if len(addresses) > 1:
        raise LookupError("Multiple address sections found for {postcode}!")


    address_html = addresses[0].get_attribute('innerHTML')

    soup = BeautifulSoup(address_html, 'html.parser')

    a_elements = soup.find_all('a')
    for a in a_elements:
        print(a.text.strip())

    pass



def lookup_address(postcode, address):

    global driver

    aa = address.casefold().replace("  "," ").replace(",","")

    done = False

    # Load the webpage
    wait_for_xpath(f'https://www.electoralcommission.org.uk/polling-stations'
                f'?postcode-search={postcode}&Submit+Postcode=',
                '/html/head/title')
        

    while not done:

        # Find the constituency element
        try:
            constituency_elems = driver.find_element_by_id('date-2024-07-04')
            done = True
            break

        except Exception as e:
            # print("Exception {e} looking for date-2024-07-04 element")
            # print("Need to lookup address")

            try:
                address_elems = driver.find_element_by_class_name("polling-station__list")
            except Exception as e:
                print(f"Exception {e} looking for polling-station__list element")
                print("SOMETHING BORKED!")

            addresses = [i for i in address_elems.find_elements_by_tag_name('li')]
            
            matches = [i for i in addresses 
                       if i.text.replace(",","").casefold()[:len(aa)] == aa]
            if len(matches) == 0:
                print(f"Failed to match address '{address}'")
                return None
            elif len(matches) > 1:
                print(f"Multiple matches for address '{address}'")
                for i in matches:
                    print(f"  {i.text.strip()}")            
                return None
            
            print(f"Matched address '{matches[0].text.strip()}'")
            wait_for_xpath(matches[0].find_element_by_tag_name('a')
                           .get_attribute('href'),
                            '/html/head/title')
            time.sleep(1)


    if constituency_elems is None:
        print("No constituency elements found!")
        return None
    if 'Thursday 04 July 2024: ' not in constituency_elems.text:

        print("No 2024 election date found!")
        if match_address(address) is None:
            print("Failed to match address!")
            return None



    constituency = constituency_elems.text.split(': ')[1]
    print("Constituency: ", constituency,end="\t")

    links = driver.find_elements_by_tag_name('a')
    emails = [link.get_attribute('href') for link in links if link.get_attribute('href').startswith('mailto:')]
    if len(emails) == 0:
        print("No email addresses found!")
        return None
    else:
        for email in [ e.replace('mailto:', '') for e in emails]:
            print("Email: ", email)
            return constituency,email
    

    #driver.quit()
    # Continue with the rest of your function...

# postcode = "SW1A 1AA"
# address = "10 Downing Street"

# a = lookup_address(postcode, address)
