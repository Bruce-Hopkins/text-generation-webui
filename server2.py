import asyncio
import websockets

import gc
import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

import gradio as gr
import torch

import modules.chat as chat
import modules.extensions as extensions_module
import modules.shared as shared
import modules.ui as ui
from modules.html_generator import generate_chat_html
from modules.LoRA import add_lora_to_model
from modules.models import load_model, load_soft_prompt
from modules.text_generation import generate_reply

# text = """
# Joe: I hate you Steve.
# Steve: But I have done nothing wrong to you.
# Joe: I DON'T CARE! I hate you.
# You can only select one emotion, happy, sad, or angry. In one word, how does Steve feel?
# Answer:"""

text = """
Joe: Hey Steve, how's it going?
Steve: I'm well, how about you?
Joe: I'm fine. *Spills water on Steve's new shirt*.

Between happy, angry, and sad,how do you think Steve feels? Answer in one word.
Answer:"""

# Loading custom settings
settings_file = None
if shared.args.settings is not None and Path(shared.args.settings).exists():
    settings_file = Path(shared.args.settings)
elif Path('settings.json').exists():
    settings_file = Path('settings.json')
if settings_file is not None:
    print(f"Loading settings from {settings_file}...")
    new_settings = json.loads(open(settings_file, 'r').read())
    for item in new_settings:
        shared.settings[item] = new_settings[item]

# Start up the Language model
shared.model_name = shared.args.model
shared.model, shared.tokenizer = load_model(shared.model_name)

def get_reply(text):
    generator = generate_reply(
        question = text, 
        max_new_tokens = 200, 
        do_sample=True, 
        temperature=1.99, 
        top_p=0.18, 
        typical_p=1, 
        repetition_penalty=1.15, 
        encoder_repetition_penalty=1, 
        top_k=89, 
        min_length=0, 
        no_repeat_ngram_size=0, 
        num_beams=1, 
        penalty_alpha=0, 
        length_penalty=1.4,
        eos_token='\n',
        early_stopping=False
    )
    return generator

# for reply in get_reply(text=text):
#     print(reply)


# Define the WebSocket handler
async def handle_text(websocket, path):
    async for message in websocket:
        response = message
        json_data = json.loads(response)
        dictionary_data = dict(json_data)

        for reply in get_reply(dictionary_data["text"]):
            print(reply)
            await websocket.send(reply)

# Add this code to the end of your existing code
start_server = websockets.serve(handle_text, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

 

