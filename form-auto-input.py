from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import os
import json
import signal
from dotenv import load_dotenv

load_dotenv("user-profile.env")

driver = webdriver.Chrome()

with open("answers.txt", encoding="utf-8") as f:
    answers = f.readlines()
answers = [answer.strip() for answer in answers]
url = answers.pop(0)
answers = [" ".join(answer.split(" ")[1:]) for answer in answers if answer.startswith("(")]
answers.insert(0, os.getenv("ID"))
answers.insert(1, os.getenv("NAME"))

wait = WebDriverWait(driver, 10)

try:
    driver.get(url)

    while True:
        try: 
            form = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            entries = form.find_elements(By.CSS_SELECTOR, "input[class=\"whsOnd zHQkBf\"], div[class=\"Y6Myld\"] > div[role=\"list\"], div[role=\"listbox\"]")
        except StaleElementReferenceException:
            continue
        if len(entries) > len(answers):
            print("not enough answers")
            break
        has_listboxes = False
        for entry in entries:
            if entry.get_attribute("role") == "listbox":
                # 選択の場合はスキップ
                print("選択: ", answers.pop(0))
                has_listboxes = True
            elif entry.get_attribute("role") == "list":
                choices = json.loads(answers.pop(0))
                checkboxes = entry.find_elements(By.CSS_SELECTOR, "div[role=\"checkbox\"]")
                for choice in choices:
                    checkboxes[choice-1].click()
            elif entry.tag_name == "input":
                element = wait.until(EC.element_to_be_clickable(entry))
                element.send_keys(answers.pop(0))
            else:
                print("invalid entry")
                break

        try:
            next = form.find_element(By.CSS_SELECTOR, "div[jsname=\"OCpkoe\"]")
        except:
            print("completed successfully")
            break
        
        if has_listboxes:
            input("press enter to continue")
        next.click()
finally:
    os.kill(driver.service.process.pid, signal.SIGTERM)