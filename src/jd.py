import re
import ddddocr
import numpy as np
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from base64 import standard_b64decode
from time import sleep
from difflib import SequenceMatcher
from datetime import datetime


def get_src_base64(driver, css):
    slider_vcode_img = driver.find_element(By.CSS_SELECTOR, css)
    img_src_base64 = slider_vcode_img.get_attribute("src")
    result = re.match("data:image/(?P<ext>.*?);base64,(?P<data>.*)", img_src_base64, re.DOTALL)
    assert result, "获取滑块验证码失败"
    ext = result.groupdict().get("ext")
    data = result.groupdict().get("data")
    img_src_byte = standard_b64decode(data)
    return img_src_byte


def ease_out_expo(x):
    if x == 1:
        return 1
    else:
        return 1 - pow(2, -10 * x)


def get_tracks(distance, seconds, ease_func):
    tracks = [0]
    offsets = [0]
    for t in np.arange(0.0, seconds, 0.1):
        offset = round(ease_func(t / seconds) * distance)
        tracks.append(offset - offsets[-1])
        offsets.append(offset)
    return offsets, tracks


def get_product_id(href):
    regex_obj = re.match(".*?/(\d+?).html", href)
    assert regex_obj, "匹配商品url失败"
    product_id = regex_obj.group(1)
    return product_id


def execute():
    username = "l241025097"
    password = "cn198641S"
    product_name = "风魔"
    start_time = "2023-02-14 12:00:00"
    url = "https://www.jd.com/"
    options = ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # WebDriver driver = new ChromeDriver(option)
    driver = Chrome(options=options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    driver.get(url)
    driver.find_element(By.CSS_SELECTOR, "li#ttbar-login a.link-login").click()
    driver.find_element(By.CSS_SELECTOR, "div.login-tab-r a").click()

    username_input = driver.find_element(By.ID, "loginname")
    username_input.clear()
    username_input.send_keys(username)

    password_input = driver.find_element(By.ID, "nloginpwd")
    password_input.clear()
    password_input.send_keys(password)

    driver.find_element(By.ID, "loginsubmit").click()
    # while 1:
    #     background_byte = get_src_base64(driver, "div.JDJRV-bigimg img")
    #     target_byte = get_src_base64(driver, "div.JDJRV-smallimg img")
    #     slider_btn = driver.find_element(By.CSS_SELECTOR, "div.JDJRV-slide-btn")
    #     with open(f"x.png", "wb") as fw:
    #         fw.write(background_byte)
    #     slider = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
    #     ret = slider.slide_match(target_byte, background_byte, simple_target=True)
    #     distance = ret["target"][0] - 24
    #     offsets, track_list = get_tracks(distance, 1, ease_out_expo)
    #     ActionChains(driver).click_and_hold(slider_btn).perform()
    #     for x in track_list:
    #         ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    #     ActionChains(driver).pause(0.5).release().perform()
    #     locator = (By.CSS_SELECTOR, "div.JDJRV-slide-err")
    #     try:
    #         WebDriverWait(driver, 1, 0.1).until(ec.visibility_of_any_elements_located(locator), "滑块验证成功")
    #     except Exception as err:
    #         print(err)
    #         break
    #     sleep(1)
    driver.find_element(By.CSS_SELECTOR, "li#ttbar-myjd a").click()
    WebDriverWait(driver, 5, 0.5).until(ec.number_of_windows_to_be(2), "等待新窗口切换失败")
    new_window_name = driver.window_handles[1]
    driver.switch_to_window(new_window_name)
    driver.find_element(By.CSS_SELECTOR, "dt#_MYJD_hd + dd#_MYJD_product a").click()
    sm = SequenceMatcher()
    match_list = []
    for each_div in driver.find_elements(By.CSS_SELECTOR, "div.cont-box"):
        info_a = each_div.find_element(By.CSS_SELECTOR, "div.product-info a")
        result = sm.set_seqs(product_name, info_a.text)
        score = sm.ratio()
        href = each_div.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        product_id = get_product_id(href)
        each_dict = {
            "score": score,
            "id": product_id,
            "name": info_a.text,
            "href": href
        }
        match_list.append(each_dict)
        other_box_a_list = each_div.find_elements(By.CSS_SELECTOR, "div.other-box a")
        if other_box_a_list:
            for each_a in other_box_a_list:
                each_a_img = each_a.find_element(By.TAG_NAME, "img")
                other_product_href = each_a.get_attribute("href")
                other_product_id = get_product_id(other_product_href)
                other_product_name = each_a_img.get_attribute("title")
                result = sm.set_seqs(product_name, other_product_name)
                score = sm.ratio()
                each_dict = {
                    "score": score,
                    "id": other_product_id,
                    "name": other_product_name,
                    "href": other_product_href
                }
                match_list.append(each_dict)
    product_dict = max(match_list, key=lambda x: x["score"])
    print(product_dict)
    stime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    diff_sec = (stime - datetime.now()).total_seconds()
    if diff_sec > 900:
        print("距离抢购时间大于15分钟，程序退出！")
        return
    else:
        if (diff_sec > 120) and (diff_sec <= 900):
            sleep(diff_sec - 120)
        while 1:
            down_time = datetime.now()
            diff_sec = (stime - down_time).total_seconds()
            print(diff_sec)
            if diff_sec > 0.5:
                continue
            open_href = f"window.open(\"{product_dict['href']}\")"
            driver.execute_script(open_href)
            WebDriverWait(driver, 5, 0.5).until(ec.number_of_windows_to_be(3), "等待抢购页面打开失败")
            driver.switch_to_window(driver.window_handles[2])
            locator = (By.ID, "btn-reservation")
            WebDriverWait(driver, 1, 0.1).until(ec.text_to_be_present_in_element(locator, "抢购"), "等待抢购按钮出现失败")
            driver.find_element(*locator).click()
            locator = (By.ID, "GotoShoppingCart")
            WebDriverWait(driver, 1, 0.1).until(ec.presence_of_element_located(locator), "等待去购物车结算按钮出现失败").click()
            locator = (By.CSS_SELECTOR, "a.common-submit-btn")
            WebDriverWait(driver, 1, 0.1).until(ec.presence_of_element_located(locator), "等待结算按钮出现失败").click()
            locator = (By.ID, "order-submit")
            WebDriverWait(driver, 1, 0.1).until(ec.presence_of_element_located(locator), "等待提交订单按钮出现失败").click()
            break
    sleep(3600)
    driver.quit()


if __name__ == "__main__":
    execute()
