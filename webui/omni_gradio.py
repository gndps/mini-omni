"""A simple web interactive chat demo based on gradio."""

import os
import time
import gradio as gr
import base64
import numpy as np
import requests


API_URL = os.getenv("API_URL", None)
client = None

if API_URL is None:
    from inference import OmniInference
    omni_client = OmniInference('./checkpoint', 'cuda:0')
    omni_client.warm_up()


OUT_CHUNK = 4096
OUT_RATE = 24000
OUT_CHANNELS = 1


def process_audio(audio, text):
    filepath = audio
    print(f"filepath: {filepath}")
    print(f"text: {text}")
    if filepath is None:
        return

    cnt = 0
    if API_URL is not None:
        with open(filepath, "rb") as f:
            data = f.read()
            base64_encoded = str(base64.b64encode(data), encoding="utf-8")
            files = {"audio": base64_encoded,
                    "text": text}
            tik = time.time()
            with requests.post(API_URL, json=files, stream=True) as response:
                try:
                    for chunk in response.iter_content(chunk_size=OUT_CHUNK):
                        if chunk:
                            # Convert chunk to numpy array
                            if cnt == 0:
                                print(f"first chunk time cost: {time.time() - tik:.3f}")
                            cnt += 1
                            audio_data = np.frombuffer(chunk, dtype=np.int16)
                            audio_data = audio_data.reshape(-1, OUT_CHANNELS)
                            yield OUT_RATE, audio_data.astype(np.int16)

                except Exception as e:
                    print(f"error: {e}")
    else:
        tik = time.time()
        for chunk in omni_client.run_AT_batch_stream(filepath):
            # Convert chunk to numpy array
            if cnt == 0:
                print(f"first chunk time cost: {time.time() - tik:.3f}")
            cnt += 1
            audio_data = np.frombuffer(chunk, dtype=np.int16)
            audio_data = audio_data.reshape(-1, OUT_CHANNELS)
            yield OUT_RATE, audio_data.astype(np.int16)


def main(port=None):

    demo = gr.Interface(
        process_audio,
        inputs=[
            gr.Audio(type="filepath", label="Microphone"),
            gr.Textbox("""You should act as DP's virtual assistant, which is a company specializing in artificial intelligence powered Customer Communications Platform.
Here is a list of their products:
1. AI Agent Assist - Faster answers, self-service, consistent info.
2. AI Contact Center - Real-time suggestions, improved service, live/post-call.
3. AI Playbooks - Real-time sales guidance, team alignment, consistent experience.
4. AI Sales - Transcriptions, coaching, smart responses, performance analytics.
Please answer customer's following query""", label="Text Input")
        ],
        outputs=[gr.Audio(label="Response", streaming=True, autoplay=True)],
        title="Chat Mini-Omni Demo",
        live=True,
    )
    if port is not None:
        demo.queue().launch(share=False, server_name="0.0.0.0", server_port=port)
    else:
        demo.queue().launch()


if __name__ == "__main__":
    import fire

    fire.Fire(main)
