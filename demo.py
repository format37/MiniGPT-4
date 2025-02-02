import argparse
import os
import random

import numpy as np
import torch
import torch.backends.cudnn as cudnn
import gradio as gr

from minigpt4.common.config import Config
from minigpt4.common.dist_utils import get_rank
from minigpt4.common.registry import registry
from minigpt4.conversation.conversation import Chat, CONV_VISION

# imports modules for registration
from minigpt4.datasets.builders import *
from minigpt4.models import *
from minigpt4.processors import *
from minigpt4.runners import *
from minigpt4.tasks import *

from PIL import Image
from io import BytesIO
import base64

import re


def parse_args():
    parser = argparse.ArgumentParser(description="Demo")
    parser.add_argument("--cfg-path", required=True, help="path to configuration file.")
    parser.add_argument(
        "--options",
        nargs="+",
        help="override some settings in the used config, the key-value pair "
        "in xxx=yyy format will be merged into config file (deprecate), "
        "change to --cfg-options instead.",
    )
    args = parser.parse_args()
    return args


def setup_seeds(config):
    seed = config.run_cfg.seed + get_rank()

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    cudnn.benchmark = False
    cudnn.deterministic = True


def remove_special_chars_and_tags(text):
    # Remove HTML-like tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove escaped characters
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')

    return text


# ========================================
#             Model Initialization
# ========================================

print('Initializing Chat')
cfg = Config(parse_args())

model_config = cfg.model_cfg
model_cls = registry.get_model_class(model_config.arch)
model = model_cls.from_config(model_config).to('cuda:0')

vis_processor_cfg = cfg.datasets_cfg.cc_sbu_align.vis_processor.train
vis_processor = registry.get_processor_class(vis_processor_cfg.name).from_config(vis_processor_cfg)
chat = Chat(model, vis_processor)
print('Initialization Finished')

# ========================================
#             Gradio Setting
# ========================================

def gradio_reset(chat_state, img_list):
    if chat_state is not None:
        chat_state.messages = []
    if img_list is not None:
        img_list = []
    return None, gr.update(value=None, interactive=True), gr.update(placeholder='Please upload your image first', interactive=False),gr.update(value="Upload & Start Chat", interactive=True), chat_state, img_list


def upload_img(gr_img, text_input, chat_state):
    if gr_img is None:
        return None, None, gr.update(interactive=True), chat_state, None
    chat_state = CONV_VISION.copy()
    img_list = []
    llm_message = chat.upload_img(gr_img, chat_state, img_list)
    return gr.update(interactive=False), gr.update(interactive=True, placeholder='Type and press Enter'), gr.update(value="Start Chatting", interactive=False), chat_state, img_list


def gradio_ask(user_message, chatbot, chat_state):
    if len(user_message) == 0:
        return gr.update(interactive=True, placeholder='Input should not be empty!'), chatbot, chat_state
    print('user_message:', user_message)
    chat.ask(user_message, chat_state)
    chatbot = chatbot + [[user_message, None]]
    return '', chatbot, chat_state


def gradio_answer(chatbot, chat_state, img_list, num_beams, temperature, max_new_tokens=1000):
    llm_message = chat.answer(conv=chat_state, img_list=img_list, max_new_tokens=max_new_tokens, num_beams=num_beams, temperature=temperature)[0]
    # llm_message = llm_message.replace('<s>', '')
    llm_message = remove_special_chars_and_tags(llm_message)
    print('llm_message:', llm_message)
    chatbot[-1][1] = llm_message
    return chatbot, chat_state, img_list


def process_image_and_text(chat, data, text_input):
    gr_img = Image.open(BytesIO(base64.b64decode(data.split(',')[1])))
    chat_state = CONV_VISION.copy()
    img_list = []
    llm_message = chat.upload_img(gr_img, chat_state, img_list)
    chat.ask(text_input, chat_state)
    return chat_state, img_list


def main():

    title = """<h1 align="center">Demo of MiniGPT-4</h1>"""
    description = """<h3>This is the demo of MiniGPT-4. Upload your images and start chatting!</h3>"""
    article = """<p><a href='https://minigpt-4.github.io'><img src='https://img.shields.io/badge/Project-Page-Green'></a></p><p><a href='https://github.com/Vision-CAIR/MiniGPT-4'><img src='https://img.shields.io/badge/Github-Code-blue'></a></p><p><a href='https://github.com/TsuTikgiau/blip2-llm/blob/release_prepare/MiniGPT_4.pdf'><img src='https://img.shields.io/badge/Paper-PDF-red'></a></p>"""

    with gr.Blocks() as demo:
        gr.Markdown(title)
        gr.Markdown(description)
        gr.Markdown(article)

        with gr.Row():
            with gr.Column(scale=0.5):
                image = gr.Image(type="pil")
                upload_button = gr.Button(value="Upload & Start Chat", interactive=True, variant="primary")
                clear = gr.Button("Restart")
                
                num_beams = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=1,
                    step=1,
                    interactive=True,
                    label="beam search numbers)",
                )
                
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    interactive=True,
                    label="Temperature",
                )

                max_new_tokens = gr.Slider(
                    minimum=10,
                    maximum=8000,
                    value=1000,
                    step=10,
                    interactive=True,
                    label="Max New Tokens",
                )

            with gr.Column():
                chat_state = gr.State()
                img_list = gr.State()
                chatbot = gr.Chatbot(label='MiniGPT-4')
                text_input = gr.Textbox(label='User', placeholder='Please upload your image first', interactive=False)
        
        upload_button.click(upload_img, [image, text_input, chat_state], [image, text_input, upload_button, chat_state, img_list], api_name="upload_image")
        
        text_input.submit(gradio_ask, [text_input, chatbot, chat_state], [text_input, chatbot, chat_state], api_name="ask_question").then(
            gradio_answer, [chatbot, chat_state, img_list, num_beams, temperature, max_new_tokens], [chatbot, chat_state, img_list], api_name="get_answer"
        )
        clear.click(gradio_reset, [chat_state, img_list], [chatbot, image, text_input, upload_button, chat_state, img_list], queue=False)

    demo.launch(share=True, enable_queue=True)



if __name__ == "__main__":
    main()
