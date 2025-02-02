# Телеграм-бот для Московского зоопарка

Проект представляет собой Телеграм-бота для Московского зоопарка, который помогает пользователям пройти викторину, выбрать животное, узнать о программе опеки и поделиться результатами в социальных сетях. Бот извлекает данные о животных с официального сайта Московского зоопарка с помощью API и библиотеки Selenium и сохраняет их в базе данных PostgreSQL.

---

## Требования
- Python 3.x
- Telegram бот — необходимо получить токен через BotFather в Telegram для аутентификации бота.
- PostgreSQL — база данных для хранения информации о животных и ответах пользователей.
- Selenium и API — для парсинга данных с официального сайта Московского зоопарка.
  
## Основные функции
### 1. **Взаимодействие с пользователем**:
- Приветствие и поддержка дружественного общения в процессе викторины.
- Поддержка перезапуска викторины с кнопки "Попробовать ещё раз".
### 2. **Модуль викторины**:
- Бот проводит викторину с несколькими вопросами, которые можно настроить.
- Вопросы и ответы могут быть обновлены в любой момент.
### 3. **Алгоритм обработки ответов**:
- Алгоритм, который анализирует ответы пользователя и определяет, какое животное ему подходит.
- Вопросы строятся по принципу «выбора класса животного», после чего отбираются соответствующие отряды и так далее.
### 4. **Подведение результатов**:
- Бот генерирует персонализированное сообщение с названием животного, его фотографией и информацией о программе опеки.
### 5. **Поддержка изображений**:
- Бот может отправлять фото или стикеры с изображением подходящего животного.
### 6. **Обратная связь и контакт с зоопарком**:
- Возможность связаться с сотрудниками зоопарка для получения дополнительной информации и оформления опеки.
- Бот может отправлять результаты викторины сотруднику зоопарка.
### 7. **Поддержка социальных сетей**:
- Пользователи могут легко поделиться результатами викторины в социальных сетях, включая ссылку на бота.
### 8. **Конфиденциальность данных**:
- Бот соблюдает правила конфиденциальности и собирает только необходимые данные.
### 9. **Масштабируемость и мониторинг**:
- Спроектирован с учетом возможного роста количества пользователей и мониторинга производительности.
### 10. **Локализация и сопровождение**:
- Удобные инструкции и справочные сообщения для пользователей.


## Установка

### **1. Клонирование репозитория**
```
git clone https://github.com/rebondareva/MoscowZooBot.git
cd MoscowZooBot
```
### **2. Установка зависимостей**
Убедитесь, что у вас установлен Python и pip, затем выполните:
```
pip install -r requirements.txt
```
### **3. Настройка окружения**
Создайте файл .env в корневой директории проекта с следующим содержимым:
```
# Основные настройки
BOT_TOKEN=<ваш_бот_токен_от_BotFather>

# Настройки базы данных PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/zoopark_bot

# Настройки для парсера
ZOOPARK_API_URL=<url_api_Московского_зоопарка>

# Настройки почты (для отправки сообщений сотрудникам зоопарка)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_HOST_USER=<ваш_email>
EMAIL_HOST_PASSWORD=<ваш_пароль_от_email>
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=<ваш_email>
SERVER_EMAIL=<ваш_email>

# Настройки для Selenium
SELENIUM_DRIVER_PATH=<путь_к_драйверу_браузера>
```
### **4. Применение миграций для базы данных**
Для работы с базой данных используйте миграции PostgreSQL:
```
python manage.py migrate
```
### **5. Запуск бота**
Запустите бота, выполнив:
```
python bot.py
```
## Структура проекта
- bot.py: Основной файл с логикой бота.
- quiz.py: Модуль викторины и обработки ответов.
- parsing.py: Парсер данных с сайта Московского зоопарка (с использованием API и Selenium).
- models.py: Модели базы данных для хранения информации о животных.
- config.py: Файл конфигурации, включая настройки для почты и базы данных.
  
## Важные зависимости в requirements.txt
- aiogram: Основная библиотека для создания Телеграм-ботов.
- selenium: Для парсинга данных с сайта.
- psycopg2: Для работы с PostgreSQL.
- SQLAlchemy: ORM для работы с базой данных.
- python-dotenv: Для работы с конфигурационными файлами .env.
- pillow: Для работы с изображениями.

## Примечания

Проект еще не полностью реализован, но уже содержит основные функциональные элементы, такие как парсер данных с сайта в базу данных. В будущем планируется добавление дополнительных функций, улучшение алгоритмов подбора животных и улучшение масштабируемости бота.

