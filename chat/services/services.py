import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.5-flash:generateContent"
)

REQUEST_TIMEOUT = 30


def get_gemini_response(prompt: str) -> str:
    """
    Sends the user's prompt to Gemini API
    and returns the AI-generated response.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logger.error("GEMINI_API_KEY not found.")
        return "Server configuration error."

    headers = {
        "x-goog-api-key": api_key
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url=GEMINI_API_URL,
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        response_data = response.json()

        ai_response = (
            response_data["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
        )

        return ai_response

    except requests.exceptions.ConnectionError:
        logger.exception("Unable to connect to Gemini API.")
        return "Unable to connect to AI service."

    except requests.exceptions.Timeout:
        logger.exception("Gemini API request timed out.")
        return "The request timed out. Please try again."

    except requests.exceptions.HTTPError:
        logger.exception("Gemini API returned an HTTP error.")
        return "AI service returned an error."

    except (KeyError, IndexError):
        logger.exception("Unexpected Gemini API response.")
        return "Invalid response received from AI service."

    except Exception:
        logger.exception("Unexpected error while calling Gemini API.")
        return "Something went wrong."