from pydub import AudioSegment
from pydub.silence import split_on_silence
from pseudo_rag.wave_generator import generate_speech
from pseudo_rag.wave_merger import merge_wav_files

import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

def remove_silence_and_speed_up(input_path, speedup_factor=1, silence_thresh=-50, min_silence_len=2000, cache_dir="speech_cache"):
    # Generate a cache key based on the input file name
    input_file_name = os.path.basename(input_path)
    cache_file = os.path.join(cache_dir, f"{input_file_name}_processed.wav")
    
    # Check if the processed file exists in the cache
    if os.path.exists(cache_file):
        return cache_file
    
    # Load the audio file
    audio = AudioSegment.from_wav(input_path)
    
    # Split the audio into non-silent parts
    non_silent_audio = split_on_silence(audio, 
                                         min_silence_len=min_silence_len, 
                                         silence_thresh=silence_thresh)
    
    # Combine the non-silent parts back into one audio
    trimmed_audio = AudioSegment.empty()
    for segment in non_silent_audio:
        trimmed_audio += segment
    
    # Speed up the audio
    sped_up_audio = trimmed_audio.speedup(playback_speed=speedup_factor)
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Export the sped-up audio to the output path
    sped_up_audio.export(cache_file, format="wav")
    
    # Save the processed audio to cache
    sped_up_audio.export(cache_file, format="wav")
    print(f"Processed audio saved to cache: {cache_file}")
    return cache_file


import time

def get_joined_prompt(user_query_wav_file, prompt_text):
    start_time = time.time()
    prompt_file = generate_speech(prompt_text)
    prompt_file_optimized = remove_silence_and_speed_up(prompt_file)
    joined_prompt_filepath = merge_wav_files([prompt_file_optimized, user_query_wav_file])
    print('joined_prompt_filepath')
    print(joined_prompt_filepath)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken by get_joined_prompt function: {elapsed_time:.2f} seconds")
    return joined_prompt_filepath


# # Usage example
# input_path = "speech_cache/fd19b56a169332c390db8ba56ba15ad40173f8522f8c29f75974e0b56d67bc1f.wav"
# output_path = "speech_cache/output_speedup_no_silence.wav"
# remove_silence_and_speed_up(input_path, output_path, speedup_factor=1.5)
