import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from inference import OmniInference
import flask
import base64
import tempfile
import traceback
from flask import Flask, Response, stream_with_context
from pseudo_rag.audio_prompt_helper import get_joined_prompt
from datetime import datetime


class OmniChatServer(object):
    def __init__(self, ip='0.0.0.0', port=60808, run_app=True,
                 ckpt_dir='./checkpoint', device='cuda:0') -> None:
        server = Flask(__name__)
        # CORS(server, resources=r"/*")
        # server.config["JSON_AS_ASCII"] = False

        self.client = OmniInference(ckpt_dir, device)
        self.client.warm_up()

        server.route("/chat", methods=["POST"])(self.chat)

        if run_app:
            server.run(host=ip, port=port, threaded=False)
        else:
            self.server = server

    def chat(self) -> Response:

        req_data = flask.request.get_json()
        try:
            data_buf = req_data["audio"].encode("utf-8")
            prompt = req_data["text"]
            data_buf = base64.b64decode(data_buf)
            stream_stride = req_data.get("stream_stride", 4)
            max_tokens = req_data.get("max_tokens", 2048)

            # Create a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./user_query_{timestamp}.wav"

            with open(output_path, "wb") as f:
                f.write(data_buf)
                print(f"file recorded by user: {output_path}")

            # Write data to a temporary file and to the specific location
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(data_buf)
                try:
                    merge=True
                    if merge:
                        joined_prompt = get_joined_prompt(user_query_wav_file=f.name, prompt_text=prompt)
                        audio_generator = self.client.run_AT_batch_stream(joined_prompt, stream_stride, max_tokens)
                    else:
                        audio_generator = self.client.run_AT_batch_stream(f.name, stream_stride, max_tokens)
                except:
                    # Prompt too long
                    print("ERROR: prompt too long")
                return Response(stream_with_context(audio_generator), mimetype="audio/wav")
        except Exception as e:
            print(traceback.format_exc())


# CUDA_VISIBLE_DEVICES=1 gunicorn -w 2 -b 0.0.0.0:60808 'server:create_app()'
def create_app():
    server = OmniChatServer(run_app=False)
    return server.server


def serve(ip='0.0.0.0', port=60808, device='cuda:0'):

    OmniChatServer(ip, port=port,run_app=True, device=device)


if __name__ == "__main__":
    import fire
    fire.Fire(serve)

