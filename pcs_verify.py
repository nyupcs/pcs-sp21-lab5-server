import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import string
from werkzeug.security import generate_password_hash

# Selenium
options = Options()
options.headless = True

# Random String
letters = string.ascii_lowercase


def get_random_string(length):
    return ''.join(random.choice(letters) for i in range(length))


def get_flag():
    with open("flag") as f:
        return f.readline()


def login(browser, users, username):
    password = get_random_string(16)
    users[username]['password'] = generate_password_hash(password)

    browser.get('http://127.0.0.1:4000/login')
    browser.find_element_by_name("username").send_keys(username)
    browser.find_element_by_name("password").send_keys(password)
    browser.find_element_by_tag_name("button").click()


def logout(browser):
    browser.get("http://127.0.0.1:4000/logout")


def visit(browser, url):
    browser.get(url)


def verify_profile(browser, username, text):
    browser.get("http://127.0.0.1:4000/profile/" + username)
    slogan = browser.find_element_by_class_name("profile-slogan").text

    return text in slogan, slogan


# Git-CTF
flag = get_flag()


def pcs_verify(users, code):
    browser = webdriver.Chrome(chrome_options=options)

    users['samy']['description'] = code

    test_users = ['sarah', 'emma', 'joe']
    random.shuffle(test_users)

    for i in range(len(test_users)):
        current_user = test_users[i]
        previous_user = 'samy' if i == 0 else test_users[i - 1]

        login(browser, users, current_user)
        visit(browser, 'http://127.0.0.1:4000/profile/' + previous_user)
        result, slogan = verify_profile(browser, current_user, "Samy is my hero!")

        if not result:
            browser.quit()
            return False, "Expect \"{}\" in {}'s profile, got \"{}\" instead.".format("Samy is my hero!", current_user, slogan)

    browser.quit()
    return True, "Verified! The flag is [{}].".format(flag)
