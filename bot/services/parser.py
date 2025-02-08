# парсинг данных о всех животных с официального сайта  и передача в базу данных
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bot.utils.config import config


# Функция для получения страницы с классификацией животного и URL изображения
def get_animal_page(animal_name, driver):
    search_url = f"https://moscowzoo.ru/animals/kinds/{animal_name}/"
    driver.get(search_url)

    # Явное ожидание, что блок с классификацией появится на странице
    try:
        # Ожидаем появления блока с классификацией
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".systematics__block.description")
            )
        )

        classification_ = {}

        # Извлекаем данные из блока с классификацией
        systematics_block = driver.find_element(
            By.CSS_SELECTOR, ".systematics__block.description"
        )

        # Обрабатываем каждый элемент с использованием XPath
        elements = systematics_block.find_elements(By.XPATH, ".//span")
        for element in elements:
            text = element.text
            if "Класс" in text:
                classification_["Класс"] = text.split("—")[1].strip()
            elif "Отряд" in text:
                classification_["Отряд"] = text.split("—")[1].strip()
            elif "Семейство" in text:
                classification_["Семейство"] = text.split("—")[1].strip()
            elif "Род" in text:
                classification_["Род"] = text.split("—")[1].strip()

        # Получение URL изображения
        try:
            image_element = driver.find_element(
                By.CSS_SELECTOR, ".systematics__right-image"
            )
            classification_["URL изображения"] = image_element.get_attribute("src")
        except Exception as e:
            classification_["URL изображения"] = None
            print(f"Не удалось получить URL изображения: {e}")

        return classification_
    except Exception as e:
        print(f"Ошибка при извлечении классификации: {e}")
        return None


def capitalize_first_word(text):
    return text.lower().capitalize()


def parse_and_collect_data():
    # Настройки Selenium для работы с Chrome
    options = Options()
    options.add_argument("--headless")  # Запускать без отображения интерфейса
    options.add_argument("--disable-gpu")  # Отключить GPU для ускорения работы
    options.add_argument("--no-sandbox")
    # Устанавливаем WebDriver для Chrome
    with webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    ) as driver:
        # Загрузка переменных из .env файла
        try:
            load_dotenv()
            url = config.api_url

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ru-RU,ru;q=0.6",
                "Origin": "https://moscowzoo.ru",
                "Referer": "https://moscowzoo.ru/",
                "User-Agent": "Python/Requests",
            }

            resp = requests.get(url, headers=headers)

            if resp.status_code == 200:
                data = resp.json()

                # Получение данных
                animals_list = data["data"]["content"].get("animalsList", [])

                # Список для хранения данных животных
                results = []

                # Списки для хранения названий и кодов животных
                animal_codes = [animal["code"] for animal in animals_list]
                animal_names = [animal["title"] for animal in animals_list]

                for animal_code, animal_name in zip(animal_codes, animal_names):
                    classification = get_animal_page(animal_code, driver=driver)
                    # Выводим классификацию
                    if classification:
                        classification["Название животного"] = capitalize_first_word(
                            animal_name
                        )
                        results.append(classification)
                    else:
                        print(
                            f"Не удалось получить классификацию для {animal_name} (код: {animal_code})"
                        )
            else:
                print(f"Ошибка запроса: {resp.status_code}")
        except Exception as e:
            print(f"Ошибка во время выполнения программы: {e}")
    return results
