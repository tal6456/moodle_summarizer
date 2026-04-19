import os

import google.generativeai as genai
from openai import OpenAI


def transcribe_audio(file_path):
    client = OpenAI()
    with open(file_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
        )
    return transcript.text


def summarize_transcript(transcript_text):
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        'Summarize the following lecture transcript and extract the content into these sections:\n'
        '1. Executive Summary\n'
        '2. Core Concepts & Intuition\n'
        '3. Practical Examples\n\n'
        f'Transcript:\n{transcript_text}'
    )
    response = model.generate_content(prompt)
    return response.text
