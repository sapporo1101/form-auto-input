from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        form = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        entries = form.find_elements(By.CSS_SELECTOR, "input[class=\"whsOnd zHQkBf\"], div[class=\"Y6Myld\"] > div[role=\"list\"]")
        if len(entries) > len(answers):
            print("not enough answers")
            break
        for entry in entries:
            if entry.tag_name == "div":
                choices = json.loads(answers.pop(0))
                checkboxes = entry.find_elements(By.CSS_SELECTOR, "div[role=\"checkbox\"]")
                for choice in choices:
                    checkboxes[choice-1].click()
            else:
                element = wait.until(EC.element_to_be_clickable(entry))
                element.send_keys(answers.pop(0))

        try:
            next = form.find_element(By.CSS_SELECTOR, "div[jsname=\"OCpkoe\"]")
        except:
            print("completed successfully")
            break

        next.click()
finally:
    os.kill(driver.service.process.pid, signal.SIGTERM)