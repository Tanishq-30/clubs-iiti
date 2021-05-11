import unittest
from app import app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from secret import email, password
class FlaskTestCase(unittest.TestCase):

    def test_club_admim_login(self):
        "make sure club admin can sign in"
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        driver.get("http://localhost:5000/login")
        try:
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="identifierId"]'))
            )
            input_field.send_keys(email)
            input_field.send_keys(Keys.RETURN)
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            )
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div/div/div[1]/h1'))
            )
            self.assertTrue('Successfully signed in as' in driver.page_source)
        except:
            driver.quit()

    def test_details_visibility_to_non_admin_users(self):
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        driver.get("http://localhost:5000/login")
        try:
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="identifierId"]'))
            )
            input_field.send_keys(email)
            input_field.send_keys(Keys.RETURN)
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            )
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div/div/div[1]/h1'))
            )
            self.assertTrue('Successfully signed in as' in driver.page_source)
            driver.get("http://localhost:5000/clubs/cinephiles")
            member_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="members"]/div/div[2]/table/tbody/tr[2]/td[1]/a'))
            )
            member_name.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="body-top"]/div[1]/p[1]'))
            )
            self.assertTrue(
                'Only Club Head can continue further' in driver.page_source)
        except:
            driver.quit()

    def test_join_button_visible(self):
        "make sure club admin can sign in"

            #    tester = app.test_client(self)
            #    response = tester.get('/clubs/avana', content_type='html/text')
            #    self.assertFalse(b'join' in response.data)

        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        driver.get("http://localhost:5000/login")
        try:
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]'))
            )
            input_field.send_keys(email)
            input_field.send_keys(Keys.RETURN)
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            )
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/h1'))
            )
            if('Successfully signed in as' in driver.page_source):
                tester = app.test_client(self)
                response = tester.get('/clubs/avana', content_type='html/text')
                self.assertTrue(b'join' in response.data)
            
        except:
            driver.quit()

if __name__ == '__main__':
    unittest.main()