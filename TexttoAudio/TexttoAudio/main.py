import requests
import json
from pydub import AudioSegment
from io import BytesIO
from threading import Thread
import os
from concurrent.futures import Future
import base64

# Environment variables
LOVA_DELFY_KEY = os.getenv("LOVA_DELFY_KEY")
ALLOWED_LOCAL = []
SPEAKER_LIST_INFO =[]

def get_speaker_list():
    SPEAKER_URL = "https://api.genny.lovo.ai/api/v1/speakers?sort=displayName%3A1"
    headers = {
        "accept": "application/json",
        "X-API-KEY": LOVA_DELFY_KEY
    }
    response = requests.get(SPEAKER_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()["data"]
        speakers = []
        for i in data:
            if i['speakerStyles'][0]['deprecated']:
                continue
            speaker = {
                'id': i['id'],
                'displayName': i['displayName'],
                'locale': i['locale'],
                'gender': i['gender']
            }
            speakers.append(speaker)
            ALLOWED_LOCAL.append(i['locale'])
        return json.dumps({"success": True, "text": speakers})
    else:
        return json.dumps({"success": False, "text": f"Speakers list not downloaded. Error code:- {response.status_code}. Make sure not to use this Library till this issue is fixed"})

result = json.loads(get_speaker_list())

if result["success"]:
    SPEAKER_LIST_INFO = result["text"]
else:
    print(result)

def main(conversation, speaker_data):
    print("Main function is running")
    return check_data(conversation, speaker_data)

def check_data(conversation, speaker_data):
    print("Checking data format")
    try:
        if isinstance(speaker_data, str):
            speaker_data = json.loads(speaker_data)
    except Exception as e:
        return json.dumps({"success": False, "text": f"Error occured at converting speaker_data:- {e}"})

    try:
        if isinstance(conversation, str):
            conversation = json.loads(conversation)
    except Exception as e:
        return json.dumps({"success": False, "text": f"Error occured at converting speaker_data:- {e}"})

    try:
        name_to_speaker_id = {}
        for speaker_name, speaker_info in speaker_data.items():
            desired_gender = speaker_info.get("gender")
            desired_locale = speaker_info.get("accent")
            if desired_gender not in ("male", "female") or desired_locale not in ALLOWED_LOCAL:
                return json.dumps({"success": False, "text": "Invalid gender or locale"})
            matching_speakers = [item["id"] for item in SPEAKER_LIST_INFO if item["gender"] == desired_gender and item["locale"] == desired_locale]
            name_to_speaker_id[speaker_name] = matching_speakers[0] if matching_speakers else None
        for message in conversation:
            if message.get('name') not in name_to_speaker_id or not message.get('text').strip():
                return json.dumps({"success": False, "text": "Invalid conversation structure"})
    except Exception as e:
        return json.dumps({"success": False, "text": f"Error occured while processing:- {e}"})

    future = Future()
    thread = Thread(target=_get_audio_thread, args=(conversation, name_to_speaker_id, future))
    thread.start()

    try:
        audio_result = future.result()
        return audio_result
    except Exception as e:
        return json.dumps({"success": False, "text": f"Error occured at get_audio:- {e}"})
    

def _get_audio_thread(conversation, name_to_speaker_id, future):
    try:
        result = get_audio(conversation, name_to_speaker_id)
        future.set_result(result)
    except Exception as e:
        future.set_exception(e)

def get_audio(conversation, name_to_speaker_id):
    print(conversation)
    print(name_to_speaker_id)
    print("Text is processing to audio")
    url = "https://api.genny.lovo.ai/api/v1/tts/sync"
    conversation_audio = AudioSegment.empty()
    current_speaker_id = None

    for message in conversation:
        print("conversation starting")
        if "text" in message:
            text = message["text"]
            name = message["name"]
            speaker_id = name_to_speaker_id.get(name, None)
            payload = {
                "speed": 1,
                "text": text,
                "speaker": speaker_id
            }
            print(LOVA_DELFY_KEY)
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "X-API-KEY": LOVA_DELFY_KEY
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                data = response.json()["data"][0]
                audio_url = data["urls"][0]
                audio_response = requests.get(audio_url, stream=True)
                if audio_response.status_code == 200:
                    audio_data = BytesIO(audio_response.content)
                    audio_segment = AudioSegment.from_file(audio_data)
                    conversation_audio += audio_segment
                    current_speaker_id = speaker_id
                else:
                    print(f"Audio fetch error: {audio_response.status_code}")
                    return json.dumps({"success": False, "text": f"Audio fetch error: {audio_response.status_code}"})
            else:
                print(f"LOVA API error: {response.status_code}")
                return json.dumps({"success": False, "text": f"LOVA API error: {response.status_code}"})
        else:
            print("Missing text in conversation")
            return json.dumps({"success": False, "text": "Missing text in conversation"})
    # output_filename = "conversation_audio.wav"
    # conversation_audio.export(output_filename, format="wav")
    # return json.dumps({"success": True, "text": "File is saved at conversation_audio.wav"})
    print("Text processed")
    buffer = BytesIO()
    conversation_audio.export(buffer, format="wav")
    audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return json.dumps({"success": True, "text": audio_base64})


if __name__ == "__main__":
    # Define the conversation as a list of text messages with names
    conversation = [
        {
          "name" : "Dave",
          "text" : "Hello, Mets fans! Welcome to your five-minute update on all things New York Mets and Major League Baseball. Let's dive right in!"
        },
        {
          "name" : "Vanessa",
          "text" : "First up, some big news from the Mets camp. Billy Eppler, the Mets' general manager, has stepped down amid an MLB investigation into potential misuse of the injured list. The investigation is still ongoing, but Eppler has decided to step aside to avoid being a distraction to the club. We'll keep you posted as this story develops."
        }
    ]

    # Define the speaker data as a dictionary
    speaker_data = {
        "Vanessa": {"gender": "female", "accent": "en-US"},
        "Dave": {"gender": "male", "accent": "en-US"}
    }
    result = main(conversation, speaker_data)
    print(result)




