from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import UnexpectedAlertPresentException

import winsound


def beepsound():
    winsound.MessageBeep(type=-1)


def remove_articles(eta_id, eta_pw):

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(5)
    driver.maximize_window()
    driver.get("https://everytime.kr/login")

    id = driver.find_element(
        By.CSS_SELECTOR, "#container > form > p:nth-child(1) > input"
    )
    id.click()
    id.send_keys(eta_id)

    pw = driver.find_element(
        By.CSS_SELECTOR, "#container > form > p:nth-child(2) > input"
    )
    pw.click()
    pw.send_keys(eta_pw)

    submit = driver.find_element(
        By.CSS_SELECTOR, "#container > form > p.submit > input"
    )
    submit.click()

    try:
        driver.find_element(
            By.CSS_SELECTOR,
            "#container > div.leftside > div:nth-child(2) > div > a.myarticle",
        )
    except:
        # print("로그인 실패!")
        return -1, driver

    driver.get("https://everytime.kr/myarticle")
    driver.implicitly_wait(5)

    after_question = 0

    while True:
        try:
            article = driver.find_elements(By.TAG_NAME, "article")[after_question]
            link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "del"))
            )
        except:
            # print("작성하신 글이 없습니다.")
            break

        # print(
        #     driver.find_element(
        #         By.CSS_SELECTOR, "#container > div.wrap.articles > article > a > p"
        #     ).text
        #     + "\n"
        # )

        try:
            delete = driver.find_element(By.CLASS_NAME, "del")
            delete.click()
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(1)
            driver.find_element(By.TAG_NAME, "article").click()
        except UnexpectedAlertPresentException:
            # print("해당 글은 질문글이므로 삭제가 불가능합니다.")
            after_question += 1

        driver.get("https://everytime.kr/myarticle")
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#container > div.wrap.title > h1"), "내가 쓴 글"
            )
        )

    return 1, driver


def remove_comments(eta_id, eta_pw):

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(5)
    driver.maximize_window()
    driver.get("https://everytime.kr/login")

    id = driver.find_element(
        By.CSS_SELECTOR, "#container > form > p:nth-child(1) > input"
    )
    id.click()
    id.send_keys(eta_id)

    pw = driver.find_element(
        By.CSS_SELECTOR, "#container > form > p:nth-child(2) > input"
    )
    pw.click()
    pw.send_keys(eta_pw)

    submit = driver.find_element(
        By.CSS_SELECTOR, "#container > form > p.submit > input"
    )
    submit.click()

    try:
        driver.find_element(
            By.CSS_SELECTOR,
            "#container > div.leftside > div:nth-child(2) > div > a.myarticle",
        )
    except:
        # print("로그인 실패!")
        return -1, driver

    driver.get("https://everytime.kr/mycommentarticle")
    driver.implicitly_wait(5)

    while True:
        try:
            article = driver.find_element(By.TAG_NAME, "article")
            link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "del"))
            )
        except:
            # print("작성하신 댓글이 없습니다.")
            break

        deletes = driver.find_elements(By.CLASS_NAME, "del")

        for delete in deletes:
            try:
                delete.click()
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
                time.sleep(1)
                driver.find_element(By.TAG_NAME, "article").click()
            except UnexpectedAlertPresentException:
                # print("이 글은 나의 질문글입니다")
                pass

        driver.get("https://everytime.kr/mycommentarticle")
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#container > div.wrap.title > h1"), "댓글 단 글"
            )
        )

    return 1, driver


UI_PATH = "src/etabot.ui"


class MainDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(UI_PATH, self)
        self.setWindowIcon(QIcon("src/eta.png"))
        self.setWindowTitle("에브리타임 글/댓글 전체 삭제 매크로")
        self.articles.clicked.connect(self.rm_articles)
        self.comments.clicked.connect(self.rm_comments)

    def rm_articles(self):
        eta_id = self.id.text()
        eta_pw = self.pw.text()

        if eta_id == "" or eta_pw == "":
            beepsound()
            time.sleep(0.2)
            self.status.setText("❗ ID/PW를 모두 입력하세요.")
            return 0

        self.status.setText("🔊 전체 글 삭제 | 작업이 완전히 끝날 때까지 화면을 조작하지 마세요.")
        QApplication.processEvents()

        result, driver = remove_articles(eta_id, eta_pw)

        if result == -1:
            self.status.setText("❗ 로그인 실패! ID/PW를 다시 입력하세요.")
            driver.quit()
            beepsound()
            return 0
        elif result == 1:
            self.status.setText("🎉 전체 글 삭제 성공! 작업이 종료되었습니다.")
            driver.quit()
            beepsound()
            return 0

    def rm_comments(self):
        eta_id = self.id.text()
        eta_pw = self.pw.text()

        if eta_id == "" or eta_pw == "":
            beepsound()
            time.sleep(0.2)
            self.status.setText("❗ ID/PW를 모두 입력하세요.")
            return 0

        self.status.setText("🔊 전체 댓글 삭제 | 작업이 완전히 끝날 때까지 화면을 조작하지 마세요.")
        QApplication.processEvents()

        result, driver = remove_comments(eta_id, eta_pw)

        if result == -1:
            self.status.setText("❗ 로그인 실패! ID/PW를 다시 입력하세요.")
            driver.quit()
            beepsound()
            return 0
        elif result == 1:
            self.status.setText("🎉 전체 댓글 삭제 성공! 작업이 종료되었습니다.")
            driver.quit()
            beepsound()
            return 0


QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = MainDialog()
main_dialog.show()

sys.exit(app.exec_())
