import ssl
import re
import time

import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def close_driver(driver):
    driver.close()
    driver.quit()
    return

def create_driver():
    print("初始化chorme中...")
    desired_capabilities = DesiredCapabilities.CHROME
    print('*****adding argument...1')
    desired_capabilities["pageLoadStrategy"] = "eager"
    print('*****adding argument...2')
    chrome_options = Options()
    print('*****adding argument...3')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--user-data-dir=userdir")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    # chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")


    ssl._create_default_https_context = ssl._create_unverified_context
    print('*****start create !')
    driver = uc.Chrome(use_subprocess=True,executable_path="/usr/local/bin/chromedriver",options=chrome_options, desired_capabilities=desired_capabilities)
    return driver


def JWXTcookie(driver=None, account='', password=''):
    print("获取调用参数:", driver, account, password)
    if driver is None:
        return create_driver()
    try:
        driver.get(
            'http://uaaap-swu-edu-cn-s.sangfor.vpn.swu.edu.cn:8118/cas/login?service=https%3A%2F%2Fspvpn.swu.edu.cn%2Fauth%2Fcas_validate%3Fentry_id%3D1')
        element = WebDriverWait(driver, timeout=10, poll_frequency=0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/a[2]'))
        )
        driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[2]/a[2]').click()
        driver.find_element(by=By.XPATH, value='//*[@id="username"]').send_keys(account)
        driver.find_element(by=By.XPATH, value='//*[@id="password"]').send_keys(password)
        driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div/div/div/div[5]/a[1]').click()
    except:
        close_driver(driver)
        return {
            "state": "系统初始化失败，请通知管理员",
        }
    finally:
        print(driver.get_cookies())
        pass

    try:
        print(driver.current_url)
        msg = re.findall(r'<font.*?id.*?>(.*)<\/font>',driver.page_source)
        if len(msg) > 0:
            close_driver(driver)
            return {
                "state": msg[0],
            }
        else:
            element = WebDriverWait(driver, timeout=10, poll_frequency=0.5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="rsList"]/div[1]/div/ul/li[1]/a/p'))
            )
            driver.find_element(by=By.XPATH, value='//*[@id="rsList"]/div[1]/div/ul/li[1]/a/p').click()
    except TimeoutException:
        close_driver(driver)
        return {
            "state": "办事大厅请求超时，请稍后再试",
        }
    except:
        close_driver(driver)
        return {
            "state": "办事大厅未知错误，请稍后再试",
        }
    finally:
        pass

    try:
        driver.switch_to.window(driver.window_handles[1])
        new_window = 'window.open("{}")'.format(
            'http://jw-swu-edu-cn.sangfor.vpn.swu.edu.cn:8118/sso/zllogin')  # js函数，此方法适用于所有的浏览器
        driver.execute_script(new_window)
    except TimeoutException:
        close_driver(driver)
        return {
            "state": "教务系统繁忙，请稍后再试",
        }
    except:
        close_driver(driver)
        return {
            "state": "教务系统未知错误，请稍后再试",
        }
    finally:
        print(driver.get_cookies())
        pass

    try:
        driver.switch_to.window(driver.window_handles[2])
        element = WebDriverWait(driver, timeout=10, poll_frequency=0.5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="cdNav"]/ul/li[4]/ul/li[4]/a'))
        )
        new_window = 'window.open("{}")'.format('http://jw-swu-edu-cn.sangfor.vpn.swu.edu.cn:8118/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N2151&xnm=2022&xqm=3&kzlx=ck&su=222020321062052&sf_request_type=ajax')  # js函数，此方法适用于所有的浏览器
        driver.execute_script(new_window)
        driver.switch_to.window(driver.window_handles[3])
        print(driver.get_cookies())
    except TimeoutException:
        close_driver(driver)
        return {
            "state": "获取课表功能繁忙，请稍后再试",
        }
    except:
        close_driver(driver)
        return {
            "state": "获取课表未知错误，请稍后再试",
        }
    finally:
        cookiejar = driver.get_cookies()
        # 做完一系列操作后关闭school_handle
        close_driver(driver)
        return {
            "state": "ok",
            "cookie": cookiejar,
        }
