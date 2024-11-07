import os
import wave
from pydub import AudioSegment

def resample_wav(file_path: str, target_sample_rate: int = 16000) -> str:
    """
    Resamples a WAV file to the target sample rate if needed.
    
    Args:
        file_path (str): The file path of the WAV file.
        target_sample_rate (int): The desired sample rate (default: 16000).
        
    Returns:
        str: The file path of the resampled WAV file.
    """
    # Load the audio file
    audio = AudioSegment.from_wav(file_path)
    
    # Check the sample rate and resample if needed
    if audio.frame_rate != target_sample_rate:
        audio = audio.set_frame_rate(target_sample_rate)
        resampled_file_path = file_path.replace(".wav", "_resampled.wav")
        audio.export(resampled_file_path, format="wav")
        return resampled_file_path
    
    return file_path

def merge_wav_files(wav_files: list) -> str:
    """
    Merges multiple WAV files into one WAV file and saves it to a './tmp' directory.
    
    Args:
        wav_files (list): List of file paths to the WAV files to be merged.
    
    Returns:
        str: The absolute file path of the merged WAV file saved in the './tmp' directory.
    """
    # Create the './tmp' directory if it doesn't exist
    temp_dir = './tmp'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Define the path for the merged file
    merged_file_path = os.path.join(temp_dir, 'merged.wav')
    
    # Open the first WAV file to get parameters
    with wave.open(wav_files[0], 'rb') as first_file:
        params = first_file.getparams()
        
        # Open the merged WAV file for writing
        with wave.open(merged_file_path, 'wb') as merged_file:
            merged_file.setparams(params)
            
            # Process each WAV file
            for wav_file in wav_files:
                # Resample if necessary
                processed_file = resample_wav(wav_file)
                
                # Write data from each processed (or original) WAV file
                with wave.open(processed_file, 'rb') as file:
                    merged_file.writeframes(file.readframes(file.getnframes()))
                
                # Remove resampled file if created
                if processed_file != wav_file:
                    os.remove(processed_file)
    
    # Return the absolute path of the merged WAV file
    return os.path.abspath(merged_file_path)

# Example usage
if __name__ == "__main__":
    wav_files = [
        "speech_cache/fd19b56a169332c390db8ba56ba15ad40173f8522f8c29f75974e0b56d67bc1f.wav", 
        "speech_cache/822501cb02685996774f2a184f3054e4251c9bd0751f612c54e3790ee586edc2.wav"
    ]
    merged_file = merge_wav_files(wav_files)
    print(f"Merged WAV file saved at: {merged_file}")
