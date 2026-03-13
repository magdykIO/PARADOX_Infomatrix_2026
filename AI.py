import os
from dotenv import load_dotenv
import warnings
import google.generativeai as gemini


warnings.filterwarnings("ignore")  # Ignoring googl's warrnings about newer versions
load_dotenv()  # Finding key

env_path = load_dotenv()
print(f"DEBUG: Шлях до файлу .env -> '{env_path}'")

load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY") # Getting API

if not api_key:
    print("❌ КРИТИЧНА ПОМИЛКА: Python не бачить змінну GEMINI_API_KEY.")
    print("Перевір, чи файл точно називається '.env', а не '.env.txt' чи щось подібне!")
    exit() 
else:
    print(f"✅ УСПІХ: Ключ знайдено! (починається на {api_key[:10]}...)")

gemini.configure(api_key=api_key)  # Setting up the key


class TODO:

    # Initialise model
    def __init__(self):
        self.model = gemini.GenerativeModel("gemini-1.5-flash")

    # Model will split task in small tasks
    def decompose_task(self, big_task):
        prompt = f"""
        ACT AS: A Logical RPG Game Master, Productivity Expert, and Mathematical Odds Maker.
        GOAL: Transform the real-world objective "{big_task}" into a 3-task progressive quest line.

        STRICT LOGIC RULES:
        1. PROGRESSION: Create exactly 3 tasks. Task-1 is the start; Task-3 is the epic conclusion.
        2. COMPLEXITY SCALING (1 to 3): 
           - Task 1: Complexity 1 (Novice).
           - Task 2: Complexity 2 (Expert).
           - Task 3: Complexity 3 (Legendary).
        3. FIXED REWARD SYSTEM: 'base_reward' is strictly tied to complexity:
           - Complexity 1: 100 nuts
           - Complexity 2: 250 nuts
           - Complexity 3: 600 nuts
        4. CONTEXTUAL DEADLINES & MULTIPLIERS:
           - Analyze the goal's nature (Intellectual, Physical, or Creative). 
           - Assign 3 options: 'easy', 'medium', 'hard' with realistic timeframes.
           - MULTIPLIERS calculation (Risk-based decimals as requested):
             * EASY: Low risk. Range: 0.05 - 0.1
             * MEDIUM: Fair challenge. Range: 0.1 - 0.2
             * HARD: Extreme pressure. Range: 0.2 - 0.5
        5. STYLE: 
           - 'title': Epic RPG name.
           - 'description': Lore-based flavor text + a CLEAR "REQUIRED ACTION" section in English.
           - 'attribute': Strength, Agility, Intellect, or Willpower.

        OUTPUT JSON STRUCTURE:
        {{
          "quest_line": "{big_task}",
          "tasks": [
            {{
              "task_id": "task-1",
              "title": "string",
              "description": "Flavor text. REQUIRED ACTION: clear instructions.",
              "attribute": "string",
              "complexity": int,
              "base_reward": int,
              "deadlines_config": {{
                "easy": "string",
                "medium": "string",
                "hard": "string"
              }},
              "multipliers_config": {{
                "easy": float,
                "medium": float,
                "hard": float
              }}
            }}
          ]
        }}
        """
        response = self.model.generate_content(prompt)
        return response.text
