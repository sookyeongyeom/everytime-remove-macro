from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import UnexpectedAlertPresentException
import time

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.implicitly_wait(5)
driver.maximize_window()
driver.get("https://everytime.kr/login")

id = driver.find_element(By.CSS_SELECTOR, "#container > form > p:nth-child(1) > input")
id.click()
id.send_keys("likeaboat")

pw = driver.find_element(By.CSS_SELECTOR, "#container > form > p:nth-child(2) > input")
pw.click()
pw.send_keys("sk7173")

submit = driver.find_element(By.CSS_SELECTOR, "#container > form > p.submit > input")
submit.click()

try:
    driver.find_element(
        By.CSS_SELECTOR,
        "#container > div.leftside > div:nth-child(2) > div > a.myarticle",
    )
except:
    print("로그인 실패!")
    driver.quit()

driver.get("https://everytime.kr/mycommentarticle")
driver.implicitly_wait(5)

cnt = 0
after_question = 0

while True:
    cnt += 1
    if cnt == 3:  # 2개 삭제
        break

    try:
        article = driver.find_elements(By.TAG_NAME, "article")[after_question]
    except:
        print("작성하신 댓글이 없습니다.")
        break

    link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
    driver.get(link)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "del"))
    )

    deletes = driver.find_elements(By.CLASS_NAME, "del")

    for delete in deletes:
        try:
            delete.click()
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(1)
            driver.find_element(By.CLASS_NAME, "article").click()
        except UnexpectedAlertPresentException:
            print("이 글은 나의 질문글입니다")
            after_question = 0

    driver.get("https://everytime.kr/mycommentarticle")
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#container > div.wrap.title > h1"), "댓글 단 글"
        )
    )

driver.quit()
