# -*- coding: utf-8 -*-

from _pytest.legacypath import Node_fspath
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import pyautogui
from time import sleep
from selenium.webdriver.common.keys import Keys

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
        We wait for elements to load. If there are 0, we go sleep again and search
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
                #try to find text "0 runners found", meaning account doesn't excist

                # Find the h3 elements
                elements = self.driver.find_elements(By.TAG_NAME, "h3")

                # Iterate over the elements
                for el in elements:
                # Check if 'RUNNERS FOUND' is in the element text
                    if 'RUNNERS FOUND' in el.text:
                        return None, 'not_excisting'

                    else:
                        #wait and try again
                        sleep(3) 
                    
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
        Collects data from the current tab we are on. Returns dictionary of athletes data
        """
        
        scraped_data, status = self.__find_elements()
        if not scraped_data:
            return None, status 
        
        #define the keys and array where we will store the dicts
        athletes = []
        keys = ['Full_Name', 'Country', 'Age_Group', 'iTRA_Index', 'Races']
        
        # Create an empty dictionary with default values: None
        athlete_dict = {key: None for key in keys}

        for athlete_data_from_scrape in scraped_data:

            lines = athlete_data_from_scrape.text.split('\n')

            for key,atribute in zip(keys,lines):
                
                #some lines have extra labes with : . We use the right ([1]) part of the string
                splited_data = atribute.split(':')

                try:
                    athlete_dict[key] = splited_data[1]
                except IndexError:
                    #if there is no label, we just use the original text
                    athlete_dict[key] = splited_data[0]
                    
                    athletes.append(athlete_dict)
         
        return athletes, status    

    def get_runner_data(self, names):
    
        no_excisting_accounts = []
        failed_names = [] 
        data = []
        
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
            self.driver.switch_to.window(self.driver.window_handles[0+1])#+1 bc first tab is empty
            athlete_data, status = self.__collect_data()
            self.driver.close()
            
            #error handeling
            if status == 'ok':
                print("Scraped data for name: ", name)
                data.append(athlete_data)
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
    
    def test(self):
        self.driver.get('https://itra.run/Runners/FindARunner')
        self.__insert_and_click('anze sobocan')   
        athlete_data,status = self.__collect_data()

def main():
    no_excisting_accounts = []
    failed_names = []
    
    bot = Bot()
    
    names = bot.read_names_from_txt() 
    
    for i in range(0, len(names), 10):
        chunk = names[i:i+10]
        data, no_acc, failed_acc = bot.get_runner_data(chunk)

        no_excisting_accounts.append(no_acc)
        failed_names.append(failed_acc)
        
    print(f'failed names: {failed_names}')
    print(f'accounts that do not excist: {no_excisting_accounts}')

    sleep(5)   
        
if __name__ == "__main__":
    main()




