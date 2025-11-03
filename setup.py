from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

def setup_driver():
    """Setup Chrome driver for Render"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Install and setup Chrome driver
    driver = webdriver.Chrome(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
        options=options
    )
    
    return driver

if __name__ == '__main__':
    driver = setup_driver()
    print("Chrome driver setup completed")
    driver.quit()
