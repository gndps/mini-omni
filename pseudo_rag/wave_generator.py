import os
import hashlib
import json
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import argparse

# Ensure the speech_cache directory exists
os.makedirs("speech_cache", exist_ok=True)

# Load the SpeechT5Processor, model, and vocoder
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# Load speaker embeddings (this example uses a female voice from CMU Arctic)
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

# Cache file to store the generated speech file paths
cache_file = "cache.json"

def load_cache():
    """Load the existing cache from the cache.json file."""
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save the cache to the cache.json file."""
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=4)

def generate_speech(input_text_or_file):
    # Read text from a file if a filename is passed, otherwise use the provided text
    if os.path.isfile(input_text_or_file):
        with open(input_text_or_file, "r") as file:
            text = file.read()
    else:
        print(os.listdir())
        text = input_text_or_file

    # Generate a unique hash based on the input text to use as the filename
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    wav_filename = f"speech_cache/{text_hash}.wav"
    
    # Check if the text has been synthesized before
    cache = load_cache()
    if text_hash in cache:
        print(f"Using cached speech for the text.")
        return wav_filename  # Return cached .wav file path

    # Tokenize the input text
    inputs = processor(text=text, return_tensors="pt")

    # Generate the spectrogram from the input text using the model
    try:
        spectrogram = model.generate_speech(inputs["input_ids"], speaker_embeddings)
    except:
        ValueError("Prompt too long")

    # Convert the spectrogram to speech using the vocoder
    with torch.no_grad():
        speech = vocoder(spectrogram)

    # Save the audio to a .wav file
    sf.write(wav_filename, speech.numpy(), samplerate=16000)

    # Update the cache with the new file path
    cache[text_hash] = wav_filename
    save_cache(cache)
    
    return wav_filename

def main():
    wav_file_from_file = generate_speech("q1.txt")
    print(f"Speech saved to: {wav_file_from_file}")

if __name__ == "__main__":
    main()
