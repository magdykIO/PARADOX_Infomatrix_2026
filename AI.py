import os
from dotenv import load_dotenv
import warnings
import google.generativeai as gemini


warnings.filterwarnings("ignore")  # Ignoring googl's warrnings about newer versions
load_dotenv()  # Finding key

env_path = load_dotenv()
print(f"DEBUG: Шлях до файлу .env -> '{env_path}'")

# 2. Примусово завантажуємо його
load_dotenv(env_path)

# 3. Витягуємо ключ
api_key = os.getenv("GEMINI_API_KEY")

# 4. Жорстка перевірка
if not api_key:
    print("❌ КРИТИЧНА ПОМИЛКА: Python не бачить змінну GEMINI_API_KEY.")
    print("Перевір, чи файл точно називається '.env', а не '.env.txt' чи щось подібне!")
    exit()  # Зупиняємо програму, щоб не було довгих червоних помилок
else:
    print(f"✅ УСПІХ: Ключ знайдено! (починається на {api_key[:10]}...)")

# Налаштовуємо модель
gemini.configure(api_key=api_key)  # Setting up the key


class TODO:

    # Initialise model
    def __init__(self):
        self.model = gemini.GenerativeModel("gemini-1.5-flash")

    # model will split task in small tasks
    def generate_quest(self, task_name):
        prompt = f"Перетвори завдання '{task_name}' на епічний квест у стилі RPG. Дай назву монстру та короткий опис битви."
        response = self.model.generate_content(prompt)
        return response.text

    def decompose_task(self, big_task):
        prompt = f"""
        Користувач хоче виконати завдання: '{big_task}'.
        Розбий це велике завдання на 3-5 маленьких, конкретних підзавдань (квестів).
        Кожне підзавдання має бути сформульоване як ігрова дія.
        Поверни результат ТІЛЬКИ у вигляді списку через дефіс, без вступу.
        Наприклад:
        - Зібрати магічні сувої (папери) зі столу
        - Очистити арену від пилу
        """
        response = self.model.generate_content(prompt)
        return response.text
