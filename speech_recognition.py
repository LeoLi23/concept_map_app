import os
import azure.cognitiveservices.speech as speechsdk

print(speechsdk.__version__)
is_recognizing = True


def parseConfig():
    with open('.env') as f:
        env_lines = f.read().splitlines()
    d = {}
    for line in env_lines:
        if not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            d[key] = value.strip()
    return d


# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
env_dict = parseConfig()
print(env_dict)
speech_config = speechsdk.SpeechConfig(subscription=env_dict['SPEECH_KEY'],
                                       region=env_dict['SPEECH_REGION'])
speech_config.speech_recognition_language = "en-US"

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

print("Speak into your microphone.")


# Create an event handler to handle recognized speech
def speech_recognized(evt):
    global is_recognizing
    result = evt.result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        curr_text = result.text
        curr_text = curr_text.replace('.', "")
        if curr_text.lower() == "stop":
            is_recognizing = False
            speech_recognizer.stop_continuous_recognition()
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        print("Speech recognition canceled: {}".format(result.cancellation_details.reason))


# Connect the event handler to the recognized event
speech_recognizer.recognized.connect(speech_recognized)

# Start continuous recognition
speech_recognizer.start_continuous_recognition()

# Wait for speech recognition to stop (e.g. when the user says "stop")
while is_recognizing:
    pass
