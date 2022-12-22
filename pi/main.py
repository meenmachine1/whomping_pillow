#!/usr/bin/env python3

import argparse
import random
import time

# Local Imports
from flexcomm import FlexComm
from phrases import Phrases
from polly import Polly
from log import *

def main(args):
    logger = get_logger()

    print("-"*40)
    print("--- Operation Take Back Bean Bag Chair ---")
    print("-"*40, end="\n\n")

    print("Initializing polly api")
    polly = Polly("johnameen")

    phrases = Phrases()

    print("Initializing sensor")
    flexcomm = FlexComm(cal_mult=4, port=args.uart)

    if args.vulgar:
        phrase_key = "vulgar"
    else:
        phrase_key = "tame"

    if phrase_key not in phrases.phrases:
        print("Error: could not find phrase_key in phrases provided.")

    phrases_to_say = phrases.phrases[phrase_key]

    print("##Starting main loop##")
    someone_sitting = False
    while True:
        if flexcomm.someone_sitting(10):
            # Only play audio after someone sits down. Not constantly during
            if someone_sitting:
                continue
            print("Caught someone sitting in chair")
            someone_sitting = True

            phrase = random.choice(phrases_to_say)
            polly.get_and_play_speech(phrase)
            print(f"Told them: {phrase}")
        else:
            someone_sitting = False
        
        time.sleep(0.01)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sexually harass people on my bean bag chair")

    parser.add_argument("--vulgar",
                      action="store_true",
                      default=False,
                      help="The beanbag will be vulgar")
    parser.add_argument("--uart",
                        help="Path to uart device",
                        metavar="/dev/ttyAMA1",
                        default="/dev/ttyAMA1")

    args = parser.parse_args()

    setUpLogging(log_level=logging.WARNING)
    main(args)