from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import json
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

driver.get(url)

time.sleep(1)


while True:
    form = driver.find_element(By.TAG_NAME, "form")
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
            entry.send_keys(answers.pop(0))

    try:
        next = form.find_element(By.CSS_SELECTOR, "div[jsname=\"OCpkoe\"]")
    except:
        print("completed successfully")
        break

    next.click()
    time.sleep(1)

while True:
    1