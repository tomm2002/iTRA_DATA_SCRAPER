from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import pyautogui
from time import sleep


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
        
    def __find_itra_points(self, link_to_athlete:str):
        pass
        
    def find_runner(self, name:str):
        
        self.driver.get('https://itra.run/Runners/FindARunner')
        
        self.__insert_text_by_id('runnername', name)
        for _ in range(5):
            pyautogui.press('enter')
            
        sleep(5)        

        try:
           scraped_data = self.driver.find_elements(By.CSS_SELECTOR, '.col-md-10.p-2')
        except StaleElementReferenceException:
            print("Stale element")
            
        print(f'Found {len(scraped_data )} people with input as "{name}"')
            
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
         
        return athletes
                
    





        

                









            

                            
                            






        
if __name__ == "__main__":
    bot = Bot()
    a = [1,2]

    bot.find_runner('tomaz miklavcic')
    sleep(5)




