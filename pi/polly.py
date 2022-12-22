#!/usr/bin/env python3

'''
TODO: 
 - Add logging library instead of just prints
'''

from hashlib import sha256
import json
import os
import time
import typing
import vlc

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from pathlib import Path
from tempfile import NamedTemporaryFile

'''
Calls the Polly API for generation of text-to-speech when necessary.
Will used cached text if that audio file exists
'''
class Polly():
    def __init__(self, profile_name, audio_save_dir="audio", region_name="us-east-1", voice="Matthew", output_format="mp3"):
        self.session = Session(profile_name=profile_name)
        self.audio_save_dir = Path(audio_save_dir)

        self.client = self.session.client("polly", region_name)
        self.audio_save_dir.mkdir(parents=True, exist_ok=True)

        self.audio_save_dir = self.audio_save_dir.as_posix()

        ids_path = f"{self.audio_save_dir}/ids.json"
        if os.path.exists(ids_path) and not os.path.isdir(ids_path):
            with open(ids_path, "r") as ids_file:
                try:
                    self.ids = json.load(ids_file)
                except json.JSONDecodeError as e:
                    print(f"Could not load ids file at {ids_path}. Got: {e}")
                    print("Will overwrite as program runs.")                    
        else:
            self.ids = {}
            with open(ids_path, "w") as ids_file:
                json.dump(self.ids, ids_file)
            
        self.ids_path = ids_path

        self.output_format = output_format
        self.voice = voice

    def update_id(self, text_id):
        if text_id in self.ids:
            print(f"Warning: {text_id} already exists in IDs lookup. Updating index.")
        
        # Yes this makes no sense but it's because the lookup naming scheme will be updated in the future
        self.ids[text_id] = f"{text_id}.mp3"

        with NamedTemporaryFile(mode="w", prefix=self.ids[text_id], delete=False) as ids_file:
            try:
                json.dump(self.ids, ids_file)
            except json.JSONDecodeError as e:
                print(f"Could not dump ids to temporary file: {ids_file.name}. Got error: {e}")

            # ? Need EXDEV try catch? Not that serious.
            os.rename(ids_file.name, self.ids_path)

    def get_speech(self, text: typing.Union[bytes, str]):
        text = text.lower()
        text, text_enc = (text, text.encode()) if isinstance(text, str) else (text.decode(), text)

        text_id = sha256(text_enc).hexdigest()

        audio = None
        audio_path = f"{self.audio_save_dir}/{text_id}.mp3"
        if text_id in self.ids:
            audio_potential_path = f"{self.audio_save_dir}/{self.ids[text_id]}"

            if os.path.exists(audio_potential_path) and not os.path.isdir(audio_potential_path):
                audio_path = audio_potential_path
                with open(audio_path, "rb") as audio_file:
                    audio = audio_file.read()

        if audio: return (audio, audio_path)
        
        try:
            response = self.client.synthesize_speech(Text=text, OutputFormat=self.output_format, VoiceId=self.voice)
        except (BotoCoreError, ClientError) as e:
            print(f"Unable to get speech from api. Got: {e}")
            return (None, None)
        
        # Access the audio stream from the response
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                audio = stream.read()
            
            with open(audio_path, "wb") as audio_file:                
                audio_file.write(audio)
        else:
            print("No audio in response.")
            return (None, None)

        self.update_id(text_id)

        return (audio, audio_path)

    def get_and_play_speech(self, text):
        audio, audio_path = self.get_speech(text)

        if None in (audio, audio_path):
            print("Unable to get speech so unable to play.")
        else:
            Polly.play_audio(audio_path)

        return audio, audio_path

    def play_audio(audio_path):
        # Note: VLC API doesn't obviously say how to play media with a data object that
        # already exists. Only obvious method is through overwriting media callbacks.
        # Slower to pass the path, but I'm lazy and speed isn't really necessary.
        mp = vlc.MediaPlayer(audio_path)

        mp.play()

        # Hacky solution for a hacky api. The play method starts a seperate thread but doesn't
        # doesn't use the underlying object to set a flag that something is playing immediately. Instead the
        # is_playing method calls the underlying c function (libvlc_media_player_is_playing) to check if 
        # the mediaplayer is playing. Since there is technically a delay as the other thread spins up 
        # and starts the player, it will return False for the first ~0.1 seconds. Instead of putting a sleep 
        # for that approximate time (which could change depending on file size), this should be a tad bit safer.
        cur_time = time.time()
        while not mp.is_playing() and (time.time() - cur_time) < 1:
            time.sleep(0.01)
            continue

        while mp.is_playing():
            time.sleep(0.1)

def test():
    p = Polly("johnameen")
    p.get_and_play_speech(b"Hello world!")

if __name__ == "__main__":
    test()