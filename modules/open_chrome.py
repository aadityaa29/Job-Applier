from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path

if stealth_mode:
    import undetected_chromedriver as uc
else:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from selenium.common.exceptions import SessionNotCreatedException


def createChromeSession(isRetry: bool = False):

    make_directories([
        file_name,
        failed_file_name,
        logs_folder_path + "/screenshots",
        default_resume_path,
        generated_resume_path + "/temp"
    ])

    options = uc.ChromeOptions() if stealth_mode else Options()

    # Stability options
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")

    if run_in_background:
        options.add_argument("--headless")

    if disable_extensions:
        options.add_argument("--disable-extensions")

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!")

    profile_dir = find_default_profile_directory()

    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved!")

    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")

    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")

    driver = None

    if stealth_mode:
        print_lg("Downloading Chrome Driver...")
        driver = uc.Chrome(options=options, version_main=146)

    else:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()

    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    return options, driver, actions, wait


try:
    options, driver, actions, wait = None, None, None, None
    options, driver, actions, wait = createChromeSession()

except SessionNotCreatedException as e:
    critical_error_log("Failed to create Chrome Session, retrying with guest profile", e)
    options, driver, actions, wait = createChromeSession(True)

except Exception as e:

    msg = (
        "Chrome failed to start.\n\n"
        "Try updating Chrome or set safe_mode = True in config.py\n\n"
    )

    print_lg(msg)
    critical_error_log("In Opening Chrome", e)

    from pyautogui import alert
    alert(msg, "Error in opening chrome")

    try:
        if driver:
            driver.quit()
    except:
        pass