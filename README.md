# PlantUML GPT Bot

A Telegram bot to generate PlantUML and svg files from voice instructions.

![Architecture Diagram](./architecture.drawio.svg)

![Sequence Diagram](./seq-diagram.svg)

## Running

Create a bot in Telegram, install *ffmpeg* and/or *aconv* to process the audio files, then install python dependencies:

```sh
pip install -r requirements.txt
```

then, create a .env file with the bot token and OpenAI API key:

```sh
TOKEN="6325628720:AAEnyPZjyjeZ5G4SYAbbIh_FLlkdMuV6YA4"
OPENAI_API_KEY="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"
```

finally run the bot.py file and start a conversation in telegram with the configured bot:

![Telegram bot](./convesation.png)

Send voice messages with instructions about the UML diagram that you want to generate.

# License

This project is licensed under the [AGPL 3.0](https://www.gnu.org/licenses/agpl-3.0.en.html) license.