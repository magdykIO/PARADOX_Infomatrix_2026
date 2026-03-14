import json
import google.generativeai as genai

class RPGTaskArchitect:
    def __init__(self, api_key):
        # Initializing Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

    def generate_rpg_plan(self, user_dream):
        """
        Generates a 3-task RPG quest line with strict progression,
        contextual deadlines, and specific betting multipliers.
        """
        
        prompt = f"""
        ACT AS: A Logical RPG Game Master, Productivity Expert, and Mathematical Odds Maker.
        GOAL: Transform the real-world objective "{user_dream}" into a 3-task progressive quest line.

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
          "quest_line": "{user_dream}",
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
        try:
            response = self.model.generate_content(prompt)
            # Извлекаем и парсим JSON
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"AI Logic engine failure: {str(e)}"}
    

    def generate_comment(self, success: bool):
        """Generates a very short RPG-style comment (1-3 words)."""
        status = "victory" if success else "defeat"
        prompt = f"Write a {status} message for an RPG player. Length: 1-3 words. Language: English."
        
        try:
            # Здесь используем обычную модель (не JSON), так как нам нужна просто строка
            response = self.model.generate_content(prompt)
            return response.text.strip().replace('"', '')
        except:
            return "Victory!" if success else "Task failed."