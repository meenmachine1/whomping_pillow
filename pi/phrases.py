#!/usr/bin/env python3

import json
import os

from pathlib import Path

class Phrases:
    def __init__(self, phrases={}, phrases_path="phrases.json"):
        if phrases and isinstance(phrases, dict):
            self.phrases = phrases
        else:
            self.phrases = self.load_phrases_json(phrases_path)

        if not self.phrases:
            print("No phrases loaded. Bailing out...")
            exit(-1)

    def load_phrases_json(self, phrases_path):
        phrases = {}
        if os.path.exists(phrases_path) and not os.path.isdir(phrases_path):
            with open(phrases_path, "r") as ids_file:
                try:
                    phrases = json.load(ids_file)
                except json.JSONDecodeError as e:
                    print(f"Could not load phrases file at {phrases_path}. Got: {e}")
        else:
            print(f"Could not find phrases json: {phrases_path}")

        return phrases