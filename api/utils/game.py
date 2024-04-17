from typing import List
from api.models.models import Word


class Game:
    def __init__(self, words: List[Word]):
        self.words_bank: List[Word] = words

    def generate_hangman_games(self, route: int):
        hangman_bank = {}
        level = 0
        for word_obj in self.words_bank:
            level += 1
            hangman_bank[f"level{level}"] = []
            word_to_hide = word_obj.word.lower()
            definition = word_obj.definition.replace(
                word_to_hide, len(word_obj.word) * '_').capitalize()
            difficulty = "Easy"
            if route == 3 or route == 4:
                difficulty = "Medium"
            if route == 5:
                difficulty = "Hard"

            hangman_bank[f"level{level}"].append({
                "gameTitle": "Hangman Game",
                "defaultAttempts": 6,
                "difficulty": difficulty,
                "hint": definition,
                "correctAnswer": word_obj.word,
            })

        return hangman_bank
