import json
import os
from typing import List
import google.generativeai as genai
from fastapi import HTTPException
from openai import OpenAI, OpenAIError
from api.schemas.schemas import Difficulty, WordInfo


class HangManAI:
    _NUMB_OF_WORDS = 10
    _RETRY_COUNT = 3
    _NUMB_OF_EXTRA_WORDS = 6

    def __init__(self):
        """
            OpenAI available models:
            - gpt-3.5-turbo-1106
            - gpt-4-1106-preview

            Google Gemini available models:
            - gemini-pro
        """
        self.openai_model = 'gpt-3.5-turbo-1106'
        self.openai_gpt4_model = 'gpt-4-1106-preview'
        self.gemini_model = 'gemini-pro'

    def get_games(self, topic: str, difficulty: Difficulty) -> List[WordInfo]:
        client = self._openai_client()

        user_prompt = f'Create a list of {self._NUMB_OF_WORDS} words related to the topic "{topic}" with difficulty level "{difficulty}". Provide a simple definition for each word. Easy: 1-4 letter words, Medium: 4-7 letter words, Hard: 7+ letter words.'

        messages = [
            {'role': 'system', 'content': 'You are a helpful dictionary assistant designed to determine a list of words related to a topic.'},
            {'role': 'system',
                'content': 'The JSON response should be in the following format: {"words" : [{"word": "word", "definition": "definition"}]}'},
            {'role': 'system',
             'content': 'The definition does not include the word itself and should be concise and contain less than 7 words.'},
            {'role': 'user', 'content': user_prompt},
        ]

        completion = client.chat.completions.create(
            messages=messages,
            model=self.openai_gpt4_model,
            response_format={"type": "json_object"},
        )

        self._print_cost(completion)

        json_response = dict(json.loads(completion.choices[0].message.content))

        try:
            words = json_response.get("words")
            results = []
            for word in words:
                word = WordInfo(**word)
                # Validate the definition
                if word.word.lower() in word.definition.lower():
                    word.definition = self._get_word_definition(
                        word=word.word, topic=topic)
                results.append(word)

            return results
        except Exception as e:
            print(e)
            print("Failed to parse json_response to WordInfo.")
            raise HTTPException(
                status_code=500, detail="Error getting word list. Please try again later.")

    def _print_cost(self, completion):
        """
        Prints the total tokens used and the corresponding cost.

        Parameters:
        - completion: The completion object.

        Returns:
        None
        """
        # print the total tokens used
        print(completion.usage.total_tokens)
        total_cost = (completion.usage.total_tokens / 1000) * 0.0010
        print(f"total cost: ${total_cost}")

    def _get_word_definition(self, word: str, topic: str) -> str:
        prompt = f'Provide a simple definition within 7 words for the word "{word}" related to {topic}.'
        client = self._openai_client()

        messages = [
            {'role': 'system', 'content': 'You are a helpful dictionary assistant designed to output a simple definition for a word.'},
            {'role': 'system', 'content': 'The JSON response should be in the following format: {"definition": "result here"}'},
            {'role': 'system', 'content': 'If you are unsure, try to provide the most likely definition based on the word itself.'},
            {'role': 'system', 'content': f'The definition should be concise and contain less than 7 words and should not include the word "{word}" itself.'},
            {'role': 'user', 'content': prompt},
        ]

        try:
            completion = client.chat.completions.create(
                messages=messages,
                model=self.openai_model,
                response_format={"type": "json_object"},
                temperature=0
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500, detail="Error getting word definition. Please try again later.")

        self._print_cost(completion)

        json_response = json.loads(completion.choices[0].message.content)

        return json_response['definition']

    def _openai_client(self) -> OpenAI:
        """
        Returns an instance of the OpenAI client.

        Raises:
            HTTPException: If there is an error configuring the OpenAI API Key.

        Returns:
            OpenAI: An instance of the OpenAI client.
        """
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return client
        except OpenAIError:
            raise HTTPException(
                status_code=500, detail="Error configuring OpenAI API Key")

    def _google_gemini_client(self, model: str = 'gemini-pro') -> genai.GenerativeModel:
        """
        Initializes and configures the Google Gemini client.

        Args:
            model (str): The model to use for the Gemini client. Defaults to 'gemini-pro'.

        Returns:
            genai.GenerativeModel: The configured Gemini client.

        Raises:
            HTTPException: If there is an error configuring the Google Gemini API Key.
        """
        try:
            genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
            gemini = genai.GenerativeModel(model)

            return gemini
        except Exception:
            raise HTTPException(
                status_code=500, detail="Error configuring Google Gemini API Key")
