import os

import google.generativeai as genai
from openai import OpenAI

_OPENAI_CLIENT = None
_GENAI_MODEL = None


def _get_openai_client():
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OPENAI_API_KEY environment variable is not set.')
        _OPENAI_CLIENT = OpenAI(api_key=api_key)
    return _OPENAI_CLIENT


def _get_genai_model():
    global _GENAI_MODEL
    if _GENAI_MODEL is None:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('GOOGLE_API_KEY environment variable is not set.')
        genai.configure(api_key=api_key)
        _GENAI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
    return _GENAI_MODEL


def transcribe_audio(file_path):
    """Transcribe an audio file to text using OpenAI Whisper."""
    try:
        with open(file_path, 'rb') as audio_file:
            transcript = _get_openai_client().audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
            )
        return transcript.text
    except OSError as exc:
        raise ValueError(f'Failed to read audio file: {file_path}') from exc
    except Exception as exc:
        raise RuntimeError('Failed to transcribe audio with OpenAI Whisper.') from exc


def summarize_transcript(transcript_text):
    """Generate a structured summary from transcript text using Gemini."""
    prompt = (
        'Summarize the following lecture transcript and extract the content into these sections:\n'
        '1. Executive Summary\n'
        '2. Core Concepts & Intuition\n'
        '3. Practical Examples\n\n'
        f'Transcript:\n{transcript_text}'
    )
    try:
        response = _get_genai_model().generate_content(prompt)
        return response.text
    except Exception as exc:
        raise RuntimeError('Failed to summarize transcript with Google Generative AI.') from exc
