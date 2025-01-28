# парсинг данных о всех животных с официального сайта
import json
from dotenv import load_dotenv
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Настройки для работы с Chrome
options = Options()
options.add_argument('--headless')  # Запускать без отображения интерфейса
options.add_argument('--disable-gpu')  # Отключить GPU для ускорения работы
options.add_argument('--no-sandbox')

# Устанавливаем WebDriver для Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# Функция для получения страницы с классификацией животного и URL изображения
def get_animal_page(animal_name):
    search_url = f"https://moscowzoo.ru/animals/kinds/{animal_name}/"
    driver.get(search_url)

    # Явное ожидание, что блок с классификацией появится на странице
    try:
        # Ожидаем появления блока с классификацией
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.systematics__block.description'))
        )

        classification = {}

        # Извлекаем данные из блока с классификацией
        systematics_block = driver.find_element(By.CSS_SELECTOR, '.systematics__block.description')

        # Обрабатываем каждый элемент с использованием XPath
        elements = systematics_block.find_elements(By.XPATH, './/span')
        for element in elements:
            text = element.text
            if 'Класс' in text:
                classification['Класс'] = text.split('—')[1].strip()
            elif 'Отряд' in text:
                classification['Отряд'] = text.split('—')[1].strip()
            elif 'Семейство' in text:
                classification['Семейство'] = text.split('—')[1].strip()
            elif 'Род' in text:
                classification['Род'] = text.split('—')[1].strip()

        # Получение URL изображения
        try:
            image_element = driver.find_element(By.CSS_SELECTOR, '.systematics__right-image')
            classification['URL изображения'] = image_element.get_attribute('src')
        except Exception as e:
            classification['URL изображения'] = None
            print(f"Не удалось получить URL изображения: {e}")

        return classification
    except Exception as e:
        print(f"Ошибка при извлечении классификации: {e}")
        return None


def capitalize_first_two_words(text):
    return text.lower().capitalize()


# Загрузка переменных из .env файла
load_dotenv()
url = os.getenv("API_URL")

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.6',
    'Origin': 'https://moscowzoo.ru',
    'Referer': 'https://moscowzoo.ru/',
    'User-Agent': 'Python/Requests'
}
resp = requests.get(url, headers=headers)

if resp.status_code == 200:
    data = resp.json()

    # Получение данных
    animals_list = data['data']['content'].get('animalsList', [])

    # Список для хранения данных животных
    results = []

    # Списки для хранения названий и кодов животных
    animal_codes = [animal['code'] for animal in animals_list]
    animal_names = [animal['title'] for animal in animals_list]

    for animal_code, animal_name in zip(animal_codes, animal_names):
        classification = get_animal_page(animal_code)
        # Выводим классификацию
        if classification:
            classification["Название животного"] = capitalize_first_two_words(animal_name)
            results.append(classification)
        else:
            print(f"Не удалось получить классификацию для {animal_name} (код: {animal_code})")

    # Сохраняем результаты в файл JSON (пока костыль, в дальнейшем здесь будет база данных)
    with open('animals_classification.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("Данные успешно сохранены в файл animals_classification.json")
else:
    print(f"Ошибка запроса: {resp.status_code}")

# Закрываем браузер
driver.quit()

