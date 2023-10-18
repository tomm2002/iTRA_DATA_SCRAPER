# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import urllib.request
from time import sleep
from selenium.webdriver.common.keys import Keys
import urllib.request
from icecream import ic
import pandas as pd
from random import randint

def check_internet():
    while True:
        try:
            urllib.request.urlopen('http://google.com') 
            return True
        except:
            return False

def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            #check for internet
            while True:
                if check_internet():
                    print("Internet is available")
                    break
                else:
                    print("No internet. Waiting for connection...")
                    sleep(5)  # Wait for 5 seconds before checking again
            
    return wrapper

class Bot:
    """
    Bot that scrapes the ITRA page for iTRA points using selenium
    """
    def __init__(self):

        self.options = webdriver.EdgeOptions()
        self.options.add_argument('--log-level=3')          #Disable warnigs from web console
        self.driver = webdriver.Edge(options=self.options)  #apply options
        self.driver.maximize_window()                       # Some buttons can't be located if the window is not maximized
        os.system('cls' if os.name == 'nt' else 'clear')    #clear console
        #self.__open_tabs()
        pass
        
    @handle_exceptions
    def __click_by_id(self, id_name:str, wait_time=10):
        """
        Click a button that has 'id' element
        """
        wait = WebDriverWait(self.driver, wait_time)
        login_button = wait.until(EC.element_to_be_clickable((By.ID, id_name)), message="Couldn't find the button. Try using to disable headles mode or maximize the window " )
        login_button.click()
     
    def __insert_text_by_id(self, id_name: str, text: str):
        """
        Insert text into field that has 'id'
        """
        box = self.driver.find_element(By.ID, id_name)
        box.send_keys(text)   
      
    def __find_elements(self):
        """ 
        We wait for elements to load. If page not loaded, it sleeps and tries again. If text '0 RUNNERS FOUND', returns None and error
        """

        max_tries = 4
        
        for _ in range(max_tries):
            try:
                scraped_data = self.driver.find_elements(By.CSS_SELECTOR, '.col-md-10.p-2')
            except StaleElementReferenceException:
                print("Stale element encountered. Retrying...")
                continue
            
            #return good data
            if len(scraped_data) > 0:
                return scraped_data, 'ok'
            else:
                #try to find text "0 runners found", meaning account doesn't excist. We check for 'RUNNERS FOUND' and for duble securety we check how many runners (it happed that there was 1 found)
                elements = self.driver.find_elements(By.TAG_NAME, "h3")
                for element in elements:
                    text = element.text
                    if 'RUNNERS FOUND' in text:
                        # split the text by spaces and remove empty strings
                        words = [word for word in text.split(' ') if word]
                        runners_found = int(words[0])  # assuming the number is always the first word in the text
                        if runners_found:
                            #rare error happened, when page loaded just the wrong time (after search for data, but before  search for RUNNERS FOUND)
                            continue
                        else:
                            return None, 'not_excisting'
                sleep(2)
                    
            return None, 'error'
      
    def __insert_and_click(self, name):

        self.__insert_text_by_id('runnername', name)
        
        for _ in range(4):
            
            try:
                element = (self.driver.find_element(By.ID, 'runnername'))
                element.click()
                element.send_keys(Keys.ENTER)
                self.driver.execute_script("window.scrollTo(0,0)")
            except:
                #User has problalby scroled down, so scroll to top of webpage
                self.driver.execute_script("window.scrollTo(0,0)")
                
            # Click the button 'Find'
            buttons = self.driver.find_elements(By.CSS_SELECTOR,'.btn.btn-itra-green-black')
            for button in buttons:
                try:
                    button.click()
                except:
                    pass
      
    def __collect_data(self):
        """
        Collects data from the current tab we are on. Returns ARRAY of dictionaries and success status
        """        

        # scrape for data
        scraped_data, status = self.__find_elements()
        if not scraped_data:
            return None, status 
        
        #define the keys and array where we will store the dicts
        athletes = []
        keys = ['Full_Name', 'Country', 'Age_Group', 'iTRA_Index', 'Races']
        
        #This for loop if more runners found with the same name
        for athlete_data_from_scrape in scraped_data:

            # Create an empty dictionary
            athlete_dict = {key: None for key in keys}            

            #by calling .txt, we get one string with data, seperated by \n
            lines = athlete_data_from_scrape.text.split('\n')

            #some data is in format -> name:___, or without the "name:" labels
            for key,atribute in zip(keys,lines):

                #we split the data with :
                splited_data = atribute.split(':')

                try:
                    #some lines have extra labes with :  We use the right ([1]) part of the string
                    athlete_dict[key] = splited_data[1]
                except IndexError:
                    #if there is no label followed by :, we just use the original text
                    athlete_dict[key] = splited_data[0]
                    
            athletes.append(athlete_dict)
            
        return athletes, status    

    def get_runner_data(self, names, time_wait):
        """
        From array "names" takes a chunk of 10 names and does the scraping
        """
        
        #based on succes, we store the nam into array or store the data to array
        no_excisting_accounts = []
        failed_names = [] 
        data = []
        
        #removes empty strings -> none
        names = [name for name in names if name]
        
        #always switch to defoult first tab. It will be "data;"
        self.driver.switch_to.window(self.driver.window_handles[0])
        
        #open all tabs
        for _ in range(len(names)):
            self.driver.execute_script(f"window.open('{'https://itra.run/Runners/FindARunner'}');")
            
        sleep(2) #safety sleep

        #insert names 
        for i,name in enumerate(names):
            self.driver.switch_to.window(self.driver.window_handles[i+1]) #+1 bc first tab is empty
            self.__insert_and_click(name)

        #go to first tab and collect data
        for j,name in enumerate(names):
            
            # wait for pages to load
            sleep(time_wait)
            self.driver.switch_to.window(self.driver.window_handles[0+1])#+1 bc first tab is empty, -> "data;"
            athlete_data, status = self.__collect_data()
            self.driver.close()
            
            #error handeling
            if status == 'ok':
                print("Scraped data for name: ", name)
                data.extend(athlete_data)
            elif status == 'not_excisting':
                print("Coulnd't find runner by the name of: ", name)
                no_excisting_accounts.append(name)

            elif status == 'error':
                print(f"Error when searching name {name}. Will try again later")
                failed_names.append(name)

        return data, no_excisting_accounts, failed_names

    def read_names_from_txt(self):
        # Get the directory where the script (exe) is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        #join the file path from exe to txt document
        file_path = os.path.join(script_dir, 'imena.txt')
        names = []
        
        try: 
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read each line of the text document
                lines = file.readlines()
                # Split each line by newline character '\n' and append to the names list
                names = [line.strip() for line in lines]
                
                return names


        except FileNotFoundError:
            print(f"File '{file_path}' not found. Make sure to place 'imena' in the same folder as the exe file.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
        return 0
    
    def save_to_excel(self, data, no_excisting_accounts, failed_names, file_name = 'podatki_tekacev.csv'):
        """
        Saves to .csv file (excel)
        """
        
        ic(data)
        
        df3 = pd.DataFrame(data)
        df2 = pd.DataFrame(failed_names, columns=["Error when searching for:"])
        df1 = pd.DataFrame(no_excisting_accounts, columns=["Data couln't be found for:"])

        df = pd.concat([df1, df2, df3], axis=1)

        try:
            df.to_csv(file_name, index=False, encoding='utf-8-sig') #encoding='utf-8-sig' insures for special characters used in Slovan nations
        except PermissionError:   #If excel is open we save with random int
            df.to_csv(file_name + str(randint(0,100)), index=False, encoding='utf-8-sig')
        print(df)
        print(f"Saved data to excel format with name {file_name} ")

def data_scraping_routine(bot, names):
    """
    Routine for collecting data
    """
    no_excisting_accounts = []
    failed_names = []
    data = []
    
    #we take 10 names and scrape the data
    for i in range(0, len(names), 10):
        chunk = names[i:i+10]
        scraped_data, no_acc, failed_acc = bot.get_runner_data(names = chunk, time_wait = 1)

        data.extend(scraped_data)
        no_excisting_accounts.extend(no_acc)
        failed_names.extend(failed_acc)  

    ic(data)
    return remove_none_and_emptylists(data), remove_none_and_emptylists(no_excisting_accounts), remove_none_and_emptylists(failed_names)

def remove_none_and_emptylists(data):
    """
    Removes None from array. 
    """    
    return [item for item in data if item is not None and item != []]



def main():    
    bot = Bot()
    
    # gets names that user wants data
    names = bot.read_names_from_txt() 

    # 1.iterration over names. 
    data, no_excisting_accounts, failed_names = data_scraping_routine(bot, names)

    # Failed names are tried again 
    if failed_names:
        more_data, no_excisting_accounts, failed_names = data_scraping_routine(bot, failed_names )
        data.extend(more_data)
        
    # Fix data and save
    bot.save_to_excel(remove_none_and_emptylists(data), remove_none_and_emptylists(no_excisting_accounts), remove_none_and_emptylists(failed_names))
    print(f'failed names: {failed_names}')
    print(f'accounts that do not excist: {no_excisting_accounts}')

    sleep(5)   
        
if __name__ == "__main__":
    main()




