#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install Flask Flask-CORS google-api-python-client youtube-transcript-api deep-translator requests


# In[2]:


pip install --upgrade streamlit


# In[3]:


pip install --upgrade flask


# In[4]:


pip install flask_sqlalchemy


# In[ ]:


import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
import urllib.parse
import openai
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

YOUTUBE_API_KEY = 'AIzaSyCbNY1pb4V-NVh8XfuzEmcbS268ebGJpPs'
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

genai.configure(api_key='AIzaSyCO5hPwvIcjMEL7x4wYzcO_iEr1U38AZGM')

host = '127.0.0.1'
port = '3306'
username = 'root'
password = ''
database_schema = 'analysis'
mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"

app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(11), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=False)
    transcript = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(50), nullable=True)

with app.app_context():
    db.create_all()

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_video_id_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params.get('v', [None])[0]

def get_playlist_id_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params.get('list', [None])[0]

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return transcript
    except (NoTranscriptFound, TranscriptsDisabled):
        return None
    except Exception as e:
        print(f"Unexpected error while retrieving transcript for video ID {video_id}: {e}")
        return None

def get_transcript_auto(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        for transcript in transcript_list:
            if transcript.language_code != 'en':
                return transcript.fetch()
    except Exception as e:
        print(f"Could not retrieve auto transcript for video ID {video_id}: {e}")
    return None

def translate_transcript(transcript, target_language='en'):
    text = ' '.join([entry['text'] for entry in transcript])
    translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
    return [{'text': translated_text}]

def analyze_sentiment_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze the sentiment as positive, negative, or neutral for the following text: {text}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def analyze_sentiment_with_gemini(text):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "Analyze sentiment",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Please provide me with the text you would like me to analyze for sentiment.",
                ],
            },
        ]
    )

    response = chat_session.send_message(text)
    return response.text

def analyze_sentiment_with_olama(text):
    d3 = {
        "model": "llama3:latest",
        "prompt": f"Analyze the sentiment as positive, negative, or neutral for the following text: {text}",
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post("http://194.238.17.64:11434/api/generate", headers=headers, data=json.dumps(d3))
        response_json = response.json()
        if 'response' in response_json:
            return response_json['response'].strip()
        else:
            print(f"Unexpected response format: {response_json}")
            return "Error: Unexpected response format"
    except Exception as e:
        print(f"Error while calling OLAMA API: {e}")
        return "Error: Unable to analyze sentiment"

def analyze_sentiment(text, model):
    if model == "gpt":
        return analyze_sentiment_with_gpt(text)
    elif model == "gemini":
        return analyze_sentiment_with_gemini(text)
    elif model == "olama":
        return analyze_sentiment_with_olama(text)
    else:
        return "Error: Invalid model specified"

def analyze_transcript(transcript, model):
    text = ' '.join(entry['text'] for entry in transcript)
    sentiment = analyze_sentiment(text, model)
    if "positive" in sentiment.lower():
        return "Positive"
    elif "negative" in sentiment.lower():
        return "Negative"
    else:
        return "Neutral"

@app.route('/')
def index():
    return "Welcome to the YouTube Transcript Sentiment Analysis API"

@app.route('/analyze', methods=['GET'])
def analyze():
    url = request.args.get('url')
    model = request.args.get('model', 'gpt')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    video_id = get_video_id_from_url(url)
    playlist_id = get_playlist_id_from_url(url)
    results = []

    if playlist_id:
        next_page_token = None
        while True:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in playlist_response.get('items', []):
                video_id = item['snippet']['resourceId']['videoId']
                title = item['snippet']['title']
                thumbnail = item['snippet']['thumbnails']['default']['url']
                transcript = get_transcript(video_id)
                if not transcript:
                    transcript = get_transcript_auto(video_id)
                    if transcript:
                        transcript = translate_transcript(transcript)
                if transcript:
                    sentiment = analyze_transcript(transcript, model)
                    video_entry = Video.query.filter_by(video_id=video_id).first()
                    if not video_entry:
                        video_entry = Video(
                            video_id=video_id,
                            title=title,
                            url=f'https://www.youtube.com/watch?v={video_id}',
                            thumbnail=thumbnail,
                            transcript=' '.join([entry['text'] for entry in transcript]),
                            sentiment=sentiment
                        )
                        db.session.add(video_entry)
                        db.session.commit()
                    results.append({
                        'title': title,
                        'thumbnail': thumbnail,
                        'sentiment': sentiment
                    })

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

    elif video_id:
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        if 'items' in video_response and len(video_response['items']) > 0:
            video_info = video_response['items'][0]['snippet']
            title = video_info['title']
            thumbnail = video_info['thumbnails']['default']['url']
            transcript = get_transcript(video_id)
            if not transcript:
                transcript = get_transcript_auto(video_id)
                if transcript:
                    transcript = translate_transcript(transcript)
            if transcript:
                sentiment = analyze_transcript(transcript, model)
                video_entry = Video.query.filter_by(video_id=video_id).first()
                if not video_entry:
                    video_entry = Video(
                        video_id=video_id,
                        title=title,
                        url=f'https://www.youtube.com/watch?v={video_id}',
                        thumbnail=thumbnail,
                        transcript=' '.join([entry['text'] for entry in transcript]),
                        sentiment=sentiment
                    )
                    db.session.add(video_entry)
                    db.session.commit()
                results.append({
                    'title': title,
                    'thumbnail': thumbnail,
                    'sentiment': sentiment
                })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=False, port='5000')


# import os
# import json
# import requests
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from googleapiclient.discovery import build
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# from deep_translator import GoogleTranslator
# import urllib.parse

# app = Flask(_name_)
# CORS(app)

# # You can directly assign the API key here
# YOUTUBE_API_KEY = 'AIzaSyCbNY1pb4V-NVh8XfuzEmcbS268ebGJpPs'
# # Alternatively, ensure the environment variable is set
# # YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# # MySQL connection details
# host = '127.0.0.1'
# port = '3306'
# username = 'root'
# password = ''
# database_schema = 'analysis'
# mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"

# app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# class Video(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     video_id = db.Column(db.String(11), unique=True, nullable=False)
#     title = db.Column(db.String(255), nullable=False)
#     url = db.Column(db.String(255), nullable=False)
#     thumbnail = db.Column(db.String(255), nullable=False)
#     transcript = db.Column(db.Text, nullable=True)
#     sentiment = db.Column(db.String(50), nullable=True)

# # Ensure database is created
# with app.app_context():
#     db.create_all()

# youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# def get_video_id_from_url(url):
#     parsed_url = urllib.parse.urlparse(url)
#     query_params = urllib.parse.parse_qs(parsed_url.query)
#     return query_params.get('v', [None])[0]

# def get_playlist_id_from_url(url):
#     parsed_url = urllib.parse.urlparse(url)
#     query_params = urllib.parse.parse_qs(parsed_url.query)
#     return query_params.get('list', [None])[0]

# def get_transcript(video_id):
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#         return transcript
#     except (NoTranscriptFound, TranscriptsDisabled):
#         return None
#     except Exception as e:
#         print(f"Unexpected error while retrieving transcript for video ID {video_id}: {e}")
#         return None

# def get_transcript_auto(video_id):
#     try:
#         transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
#         for transcript in transcript_list:
#             if transcript.language_code != 'en':
#                 return transcript.fetch()
#     except Exception as e:
#         print(f"Could not retrieve auto transcript for video ID {video_id}: {e}")
#     return None

# def translate_transcript(transcript, target_language='en'):
#     text = ' '.join([entry['text'] for entry in transcript])
#     translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
#     return [{'text': translated_text}]

# def analyze_sentiment(text):
#     d3 = {
#         "model": "llama3:latest",
#         "prompt": f"Analyze the sentiment as positive, negative, or neutral for the following text: {text}",
#         "stream": False
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     try:
#         response = requests.post("http://194.238.17.64:11434/api/generate", headers=headers, data=json.dumps(d3))
#         response_json = response.json()
#         if 'response' in response_json:
#             return response_json['response'].strip()
#         else:
#             print(f"Unexpected response format: {response_json}")
#             return "Error: Unexpected response format"
#     except Exception as e:
#         print(f"Error while calling OLAMA API: {e}")
#         return "Error: Unable to analyze sentiment"

# def analyze_transcript(transcript):
#     text = ' '.join(entry['text'] for entry in transcript)
#     sentiment = analyze_sentiment(text)
#     if "positive" in sentiment.lower():
#         return "Positive"
#     elif "negative" in sentiment.lower():
#         return "Negative"
#     else:
#         return "Neutral"

# @app.route('/')
# def index():
#     return "Welcome to the YouTube Transcript Sentiment Analysis API"

# @app.route('/analyze', methods=['GET'])
# def analyze():
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'error': 'URL is required'}), 400

#     video_id = get_video_id_from_url(url)
#     playlist_id = get_playlist_id_from_url(url)
#     results = []

#     if playlist_id:
#         next_page_token = None
#         while True:
#             playlist_response = youtube.playlistItems().list(
#                 part='snippet',
#                 playlistId=playlist_id,
#                 maxResults=50,
#                 pageToken=next_page_token
#             ).execute()

#             for item in playlist_response.get('items', []):
#                 video_id = item['snippet']['resourceId']['videoId']
#                 title = item['snippet']['title']
#                 thumbnail = item['snippet']['thumbnails']['default']['url']
#                 transcript = get_transcript(video_id)
#                 if not transcript:
#                     transcript = get_transcript_auto(video_id)
#                     if transcript:
#                         transcript = translate_transcript(transcript)
#                 if transcript:
#                     sentiment = analyze_transcript(transcript)
#                     video_entry = Video.query.filter_by(video_id=video_id).first()
#                     if not video_entry:
#                         video_entry = Video(
#                             video_id=video_id,
#                             title=title,
#                             url=f'https://www.youtube.com/watch?v={video_id}',
#                             thumbnail=thumbnail,
#                             transcript=' '.join([entry['text'] for entry in transcript]),
#                             sentiment=sentiment
#                         )
#                         db.session.add(video_entry)
#                         db.session.commit()
#                     results.append({
#                         'title': title,
#                         'thumbnail': thumbnail,
#                         'sentiment': sentiment
#                     })

#             next_page_token = playlist_response.get('nextPageToken')
#             if not next_page_token:
#                 break
#     elif video_id:
#         video_response = youtube.videos().list(
#             part='snippet',
#             id=video_id
#         ).execute()

#         if video_response['items']:
#             video_details = video_response['items'][0]['snippet']
#             title = video_details['title']
#             thumbnail = video_details['thumbnails']['default']['url']
#             transcript = get_transcript(video_id)
#             if not transcript:
#                 transcript = get_transcript_auto(video_id)
#                 if transcript:
#                     transcript = translate_transcript(transcript)
#             if transcript:
#                 sentiment = analyze_transcript(transcript)
#                 video_entry = Video.query.filter_by(video_id=video_id).first()
#                 if not video_entry:
#                     video_entry = Video(
#                         video_id=video_id,
#                         title=title,
#                         url=f'https://www.youtube.com/watch?v={video_id}',
#                         thumbnail=thumbnail,
#                         transcript=' '.join([entry['text'] for entry in transcript]),
#                         sentiment=sentiment
#                     )
#                     db.session.add(video_entry)
#                     db.session.commit()
#                 results.append({
#                     'title': title,
#                     'thumbnail': thumbnail,
#                     'sentiment': sentiment
#                 })
#         else:
#             return jsonify({'error': 'Video not found'}), 404
#     else:
#         return jsonify({'error': 'Invalid URL'}), 400

#     return jsonify(results)


# if _name_ == '_main_':
#     app.run(debug=False,host = '192.168.1.2', port='7076')






















# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from googleapiclient.discovery import build
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# from deep_translator import GoogleTranslator
# import openai
# import urllib.parse

# app = Flask(_name_)
# CORS(app)

# YOUTUBE_API_KEY = 'AIzaSyCbNY1pb4V-NVh8XfuzEmcbS268ebGJpPs'
# OPENAI_API_KEY = 'sk-proj-5BaJxroeVZF0WgTiIA2IT3BlbkFJbLG9nIMa5JCUlJGguakh'

# youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# def get_video_id_from_url(url):
#     parsed_url = urllib.parse.urlparse(url)
#     query_params = urllib.parse.parse_qs(parsed_url.query)
#     return query_params.get('v')[0] if 'v' in query_params else None

# def get_playlist_id_from_url(url):
#     parsed_url = urllib.parse.urlparse(url)
#     query_params = urllib.parse.parse_qs(parsed_url.query)
#     return query_params.get('list')[0] if 'list' in query_params else None

# def get_transcript(video_id):
#     try:
#         return YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#     except (NoTranscriptFound, TranscriptsDisabled):
#         return None

# def get_transcript_auto(video_id):
#     try:
#         transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
#         for transcript in transcript_list:
#             if transcript.language_code != 'en':
#                 return transcript.fetch()
#     except Exception as e:
#         print(f"Could not retrieve transcript for video ID {video_id}: {e}")
#     return None

# def translate_transcript(transcript, target_language='en'):
#     text = ' '.join([entry['text'] for entry in transcript])
#     return [{'text': GoogleTranslator(source='auto', target=target_language).translate(text)}]

# def analyze_sentiment(text):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": f"Analyze the sentiment as positive, negative, or neutral for the following text: {text}"}
#         ]
#     )
#     return response.choices[0].message['content'].strip()

# def analyze_transcript(transcript):
#     text = ' '.join(entry['text'] for entry in transcript)
#     sentiment = analyze_sentiment(text)
#     if "positive" in sentiment.lower():
#         return "Positive"
#     elif "negative" in sentiment.lower():
#         return "Negative"
#     else:
#         return "Neutral"

# @app.route('/')
# def index():
#     return "Welcome to the YouTube Transcript Sentiment Analysis API" 


            

# @app.route('/.p589`1234567nalyze', methods=['GET'])
# def analyze():
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'error': 'URL is required'}), 400

#     video_id = get_video_id_from_url(url)
#     playlist_id = get_playlist_id_from_url(url)
#     results = []

#     if playlist_id:
#         next_page_token = None
#         while True:
#             playlist_response = youtube.playlistItems().list(
#                 part='snippet',
#                 playlistId=playlist_id,
#                 maxResults=50, 
#                 pageToken=next_page_token
#             ).execute()

#             for item in playlist_response.get('items', []):
#                 video_id = item['snippet']['resourceId']['videoId']
#                 title = item['snippet']['title']
#                 thumbnail = item['snippet']['thumbnails']['default']['url']
#                 transcript = get_transcript(video_id)
#                 if not transcript:
#                     transcript = get_transcript_auto(video_id)
#                     if transcript:
#                         transcript = translate_transcript(transcript)
#                 if transcript:
#                     sentiment = analyze_transcript(transcript)
#                     results.append({
#                         'title': title,
#                         'thumbnail': thumbnail,
#                         'sentiment': sentiment,
#                         'video_id': video_id
#                     })

#             next_page_token = playlist_response.get('nextPageToken')
#             if not next_page_token:
#                 break
#     elif video_id:
#         video_response = youtube.videos().list(
#             part='snippet',
#             id=video_id
#         ).execute()

#         if video_response['items']:
#             video_details = video_response['items'][0]['snippet']
#             title = video_details['title']
#             thumbnail = video_details['thumbnails']['default']['url']
#             transcript = get_transcript(video_id)
#             if not transcript:
#                 transcript = get_transcript_auto(video_id)
#                 if transcript:
#                     transcript = translate_transcript(transcript)
#             if transcript:
#                 sentiment = analyze_transcript(transcript)
#                 results.append({
#                     'title': title,
#                     'thumbnail': thumbnail,
#                     'sentiment': sentiment,
#                     'video_id': video_id
#                 })
#         else:
#             return jsonify({'error': 'Video not found'}), 404
#     else:
#         return jsonify({'error': 'Invalid URL'}), 400

#     return jsonify(results)
# if _name_ == '_main_':
#     app.run(debug=False, port=5000)


# In[ ]:




