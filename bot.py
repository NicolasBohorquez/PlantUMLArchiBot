import os
import base64
import openai
import shutil
import string
import telebot
import zipfile
import requests
import tempfile
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()  # take environment variables from .env.

# Telegram bot token
TOKEN = os.getenv('TOKEN')

# OpenAI ChatGPT API endpoint
CHATGPT_API_URL = 'https://api.openai.com/v1/engines/davinci-codex/completions'

# OpenAI model id
CHATGPT_MODEL_ID = 'gpt-3.5-turbo'

# OpenAI Speech to Text API endpoint
SPEECH_TO_TEXT_API_URL = 'https://api.openai.com/v1/audio/transcriptions'

# OpenAI API credentials
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# PlantUML Server URL
PLANTUML_SERVER_URL = 'https://kroki.io/plantuml'

# Initialize the Telegram bot
bot = telebot.TeleBot(TOKEN)

# Set OpenAI API credentials
openai.api_key = OPENAI_API_KEY

# Prefix to set the general conditions
prefix = 'generate plantuml of: '

# Suffix to clean prompt response
suffix = ''' . Use only ascii characters without tildes. 
Use skinparam for handwritten as true explicitly.
Use skinparam for monochrome as true explicitly.
Include a title.
Respond only with the plantuml valid syntax
'''


def generate_diagram(diagram):
    """
    Generate an SVG representation of a diagram using PlantUML Server.

    Args:
        diagram (str): The diagram to be converted to SVG.

    Returns:
        tuple: A tuple containing the original diagram and the SVG content.
    """
    response = requests.post(PLANTUML_SERVER_URL, data=diagram
        ,headers={ 'Content-Type': 'plain/text', 'Accept': 'image/svg+xml' })
    svg_content = response.content
    return diagram, svg_content

def compress_files(plantuml_code, svg_content):
    """
    Compresses the given PlantUML code and SVG content into a zip file.

    Args:
        plantuml_code (str): The PlantUML code to be compressed.
        svg_content (bytes): The SVG content to be compressed.

    Returns:
        str: The path of the compressed zip file.
    """
    temp_dir = tempfile.mkdtemp()

    plantuml_file = os.path.join(temp_dir, 'diagram.puml')
    svg_file = os.path.join(temp_dir, 'diagram.svg')

    with open(plantuml_file, 'w') as f:
        f.write(plantuml_code)

    with open(svg_file, 'wb') as f:
        f.write(svg_content)

    zip_file = os.path.join('.', 'diagram.zip')
    with zipfile.ZipFile(zip_file, 'w') as zipf:
        zipf.write(plantuml_file, 'diagram.puml')
        zipf.write(svg_file, 'diagram.svg')

    shutil.rmtree(temp_dir)

    return zip_file

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am PlanUMLTeleGptBot. Here is how i can help you:
1. Send audio messages with the kind of UML diagram that you want to be drawn, example:
    'sequence diagram on how to take a bus'
your result will be returned as a zip file name diagram.zip
""")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """
    Handles voice messages by downloading the voice file, converting it to text using OpenAI Speech to Text API,
    generating a response using OpenAI ChatGPT API, generating PlantUML and SVG files, compressing the files into a zip,
    and sending the zip file back to the user.

    Args:
        message (obj): The voice message object.

    Returns:
        None
    """
    file_info = bot.get_file(message.voice.file_id)
    file_path = file_info.file_path

    # Download the audio file
    audio_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    audio_file = requests.get(audio_url)

    # Convert audio to text using OpenAI Speech to Text API
    temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav')
    with open(temp_audio_file.name, 'wb') as f:
        f.write(audio_file.content)

    audio = AudioSegment.from_file(temp_audio_file.name)
    audio.export(temp_audio_file.name, format='wav')
    transcription = {"text":"Let's go do some ROCK-conaissance!"}
    plantuml = {"text":'@startuml rectangle uhoh @enduml'}
    try:
        # transcribe the audio into a text message
        transcription = openai.Audio.transcribe("whisper-1", temp_audio_file)
        plantuml = openai.ChatCompletion.create(
            model=CHATGPT_MODEL_ID,
            messages=[
                    {"role": "user", "content": prefix+transcription.text+suffix},
                ]
            )
        plantuml.text = plantuml.choices[0].message.content
        plantuml.text = plantuml.text.replace('\\n', '\n')
        # Reply with the transcription and PlantUML text
        bot.reply_to(message, transcription.text)
        
        # Generate PlantUML and SVG files
        plantuml_code, svg_content = generate_diagram(plantuml.text)
        
        # Compress PlantUML and SVG files into a zip
        zip_file = compress_files(plantuml_code, svg_content)

        # Send the compressed zip file back to the user
        with open(zip_file, 'rb') as f:
            bot.send_document(message.chat.id, f)    
        os.remove(zip_file)
    except Exception as e:
        bot.reply_to(message, e)

# Start the Telegram bot
bot.polling()
