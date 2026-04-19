import os

import google.generativeai as genai
from openai import OpenAI

_OPENAI_CLIENT = OpenAI()


def transcribe_audio(file_path):
    try:
        with open(file_path, 'rb') as audio_file:
            transcript = _OPENAI_CLIENT.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
            )
        return transcript.text
    except OSError as exc:
        raise ValueError(f'Failed to read audio file: {file_path}') from exc
    except Exception as exc:
        raise RuntimeError('Failed to transcribe audio with OpenAI Whisper.') from exc


def summarize_transcript(transcript_text):
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError('GOOGLE_API_KEY environment variable is not set.')

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        'Summarize the following lecture transcript and extract the content into these sections:\n'
        '1. Executive Summary\n'
        '2. Core Concepts & Intuition\n'
        '3. Practical Examples\n\n'
        f'Transcript:\n{transcript_text}'
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        raise RuntimeError('Failed to summarize transcript with Google Generative AI.') from exc
