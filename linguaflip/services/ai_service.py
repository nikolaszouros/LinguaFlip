import os
import json
from google import genai
from db.database import get_db
from languages import LANGUAGES


def _lang_name(code):
    """Return the full language name for a code, falling back to the code itself."""
    return LANGUAGES.get(code, code)


class AIService:
    def __init__(self, api_key):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_suggestions(self, deck):
        """
        Ask Gemini to generate 5-10 vocabulary words for the deck's language pair.
        Returns a list of {front, back} dicts, or [] on error.
        """
        if self.client is None:
            return []
        source = _lang_name(deck.source_lang)
        target = _lang_name(deck.target_lang)
        try:
            prompt = (
                f'Generate 5-10 common vocabulary words or short phrases for someone learning '
                f'{target} whose native language is {source}. '
                f'Return ONLY a raw JSON array of objects with exactly two keys: '
                f'"front" (the word in {source}) and "back" (the translation in {target}). '
                f'No markdown, no code fences, no explanation — just the JSON array.'
            )
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            content = response.text.strip()
            if content.startswith('```'):
                lines = content.splitlines()
                content = '\n'.join(lines[1:-1]).strip()
            suggestions = json.loads(content)
            return suggestions if isinstance(suggestions, list) else []
        except Exception as e:
            print(f'[AIService.generate_suggestions] error: {e}')
            return []

    def translate(self, word, source_lang, target_lang):
        """
        Translate a single word/phrase from source_lang to target_lang.
        Returns the translated string, or None on failure.
        """
        if self.client is None:
            print('[AIService.translate] No API client — GEMINI_API_KEY not set.')
            return None
        source = _lang_name(source_lang)
        target = _lang_name(target_lang)
        try:
            prompt = (
                f'Translate the following word or phrase from {source} to {target}. '
                f'Return ONLY the translation, nothing else — no explanation, '
                f'no extra punctuation, no quotes.\n\n{word}'
            )
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f'[AIService.translate] error: {e}')
            return None

    def log_usage(self, user_id):
        db = get_db()
        db.execute('INSERT INTO ai_usage_log (user_id) VALUES (%s)', (user_id,))
        db.commit()

    def check_rate_limit(self, user):
        return user.get_ai_usage_today() < 10
