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
        
        sleep(3)
        max_tries = 4
        
        for _ in range(max_tries):
            try:
                scraped_data = self.driver.find_elements(By.CSS_SELECTOR, '.col-md-10.p-2')
            except StaleElementReferenceException:
                break
            
            if len(scraped_data) != None:
                return scraped_data
                print(_)
                
    def __insert_and_click(self, name):
        self.driver.get('https://itra.run/Runners/FindARunner')

        self.__insert_text_by_id('runnername', name)

        # Click the button 'Find'
        buttons = self.driver.find_elements(By.CSS_SELECTOR,'.btn.btn-itra-green-black')
        for button in buttons:
            try:
                button.click()
            except:
                pass

    def get_runner_data(self, name:str):

        self.__insert_and_click(name)
        scraped_data = self.__find_elements()
        
        if scraped_data == None:
            #If we couln't get runners info, we try again with the search
            self.__insert_and_click(name)
            scraped_data = self.__find_elements() 
            
            if scraped_data == None:
                print("Coulnd't find runner by the name of: ", name)


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

    print(bot.get_runner_data('tomaz miklavcic'))
    sleep(5)




