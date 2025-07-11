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
import re
import time

load_dotenv("user-profile.env")

driver = webdriver.Chrome()

with open("answers.txt", encoding="utf-8") as f:
    lines = f.readlines()
lines = [line.strip() for line in lines]
url = lines.pop(0)
answers = [
    " ".join(answer.split(" ")[1:])
    for answer in lines
    if re.match(r"^\(.+\) .+$", answer)
]

# ()なしでもanswersを取得する ("# "で始まる行は除外)
print("answers:", answers)
if len(answers) <= 0:
    answers = [
        answer for answer in lines if answer != "" and not answer.startswith("# ")
    ]

answers.insert(0, os.getenv("ID"))
answers.insert(1, os.getenv("NAME"))

print("answers:", answers)

wait = WebDriverWait(driver, 10)

try:
    driver.get(url)

    while True:
        try:
            form = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            time.sleep(0.1)
            entries = form.find_elements(
                By.CSS_SELECTOR,
                'input[class="whsOnd zHQkBf"], textarea[class="KHxj8b tL9Q4c"], div[class="Y6Myld"] > div[role="list"], div[role="listbox"], div[role="radiogroup"]',
            )
        except StaleElementReferenceException:
            continue
        has_listboxes = False
        has_invalid_entry = False
        for entry in entries:
            is_invalid_entry = True
            while True:
                try:
                    if entry.get_attribute("role") == "listbox":
                        # 選択の場合はスキップ
                        print("選択: ", answers.pop(0))
                        has_listboxes = True
                        is_invalid_entry = False
                except StaleElementReferenceException:
                    continue
                try:
                    if entry.get_attribute("role") == "radiogroup":
                        choice = json.loads(answers.pop(0))
                        radio_buttons = entry.find_elements(
                            By.CSS_SELECTOR, 'div[role="radio"]'
                        )
                        texts = [
                            item.text
                            for item in entry.find_elements(
                                By.CSS_SELECTOR, 'span[dir="auto"]'
                            )
                        ]
                        # choiceが文字列の場合は、choiceに一致するtextsのインデックスを取得
                        if isinstance(choice, str):
                            choice = texts.index(choice)
                        radio_buttons[choice].click()
                        is_invalid_entry = False
                except StaleElementReferenceException:
                    continue
                try:
                    if entry.get_attribute("role") == "list":
                        choices = json.loads(answers.pop(0))
                        # choicesが整数の場合はリストに変換
                        if isinstance(choices, int):
                            choices = [choices]
                        checkboxes = entry.find_elements(
                            By.CSS_SELECTOR, 'div[role="checkbox"]'
                        )
                        texts = [
                            item.text
                            for item in entry.find_elements(
                                By.CSS_SELECTOR, 'span[dir="auto"]'
                            )
                        ]
                        for choice in choices:
                            # choiceが文字列の場合は、choiceに一致するtextsのインデックスを取得
                            if isinstance(choice, str):
                                choice = texts.index(choice)
                            checkboxes[choice].click()
                        is_invalid_entry = False
                except StaleElementReferenceException:
                    continue
                try:
                    if entry.tag_name == "input" or entry.tag_name == "textarea":
                        element = wait.until(EC.element_to_be_clickable(entry))
                        element.send_keys(answers.pop(0))
                        is_invalid_entry = False
                except StaleElementReferenceException:
                    continue
                if is_invalid_entry:
                    has_invalid_entry = True
                break
            if has_invalid_entry:
                print("invalid entry found")
                break

        try:
            send = form.find_element(By.CSS_SELECTOR, 'div[jsname="M2UYVd"]')
            print("completed successfully")
            break
        except:
            pass
        try:
            next = form.find_element(By.CSS_SELECTOR, 'div[jsname="OCpkoe"]')
        except:
            print("no next button found")

        if has_listboxes:
            input("press enter to continue")
        try:
            next.click()
        except:
            print("next button not clickable")
finally:
    os.kill(driver.service.process.pid, signal.SIGTERM)
