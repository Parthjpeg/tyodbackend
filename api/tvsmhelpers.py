import requests
from openai import OpenAI
import base64
from io import BytesIO
import tempfile

client = OpenAI()

def translatetext(text, sourceLang , targetLang):
  api_key = "0ELDJvqbaDLzAGPIR1Dfv38ehE21HkMjxWkXYWq-Mk1bajlyyxXMyHGpwb3lD2cz"
  headers = {
    "Content-Type": "application/json",
    "Authorization": api_key
  }
  payload = {
    "pipelineTasks": [
        {
            "taskType": "translation",
            "config": {
                "language": {
                    "sourceLanguage": sourceLang,
                    "targetLanguage": targetLang
                },
                "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
            }
        }
    ],
    "inputData": {
        "input": [
            {
                "source": text
            }
        ]
    }
  }
  response = requests.post("https://dhruva-api.bhashini.gov.in/services/inference/pipeline", headers=headers, json=payload)
  return response.json().get("pipelineResponse")[0].get("output")[0].get("target")



def naturallm(messages):
  response = client.chat.completions.create(
  model="gpt-4o",
  messages=messages
  )
  return response.choices[0].message.content


def Get_Base64_tvsm(file):  #Returns the base64 of an image from the temp memory file
    return base64.b64encode(BytesIO(file.read()).getvalue()).decode('utf-8')



def speechtotexttvsm(audio_file):
  transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
  )
  final_input = transcription.text
  return (final_input)

def texttospeechtvsm(text):
  temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
  speech_file_path = temp1.name
  response = client.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=text
    )
  response.stream_to_file(speech_file_path)
  return speech_file_path



def translateAudioToEnglishTvsm(base64Audio, sourceLang, targetLang):
  api_key = "0ELDJvqbaDLzAGPIR1Dfv38ehE21HkMjxWkXYWq-Mk1bajlyyxXMyHGpwb3lD2cz"
  headers = {
    "Content-Type": "application/json",
    "Authorization": api_key
  }
  dataAsr = {
    "bn":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
    "en":"ai4bharat/whisper-medium-en--gpu--t4",
    "gu":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
    "hi":"ai4bharat/conformer-hi-gpu--t4",
    "kn":"ai4bharat/conformer-multilingual-dravidian-gpu--t4",
    "ml":"ai4bharat/conformer-multilingual-dravidian-gpu--t4",
    "mr":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
    "or":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
    "pa":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
    "sa":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4",
    "ta":"ai4bharat/conformer-multilingual-dravidian-gpu--t4",
    "te":"ai4bharat/conformer-multilingual-dravidian-gpu--t4",
    "ur":"ai4bharat/conformer-multilingual-indo_aryan-gpu--t4"
  }

  payload = {
    "pipelineTasks": [
        {
            "taskType": "asr",
            "config": {
                "language": {
                    "sourceLanguage": sourceLang
                },
                "serviceId": dataAsr[sourceLang]
            }
        },
        {
            "taskType": "translation",
            "config": {
                "language": {
                    "sourceLanguage": sourceLang,
                    "targetLanguage": targetLang
                },
                "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
            }
        }
    ],
    "inputData": 
    {
        "audio": 
        [
            {
                "audioContent": base64Audio
            }
        ]
    }
  }
  response = requests.post("https://dhruva-api.bhashini.gov.in/services/inference/pipeline", headers=headers, json=payload)
  transresp = response.json().get("pipelineResponse")[1].get("output")[0].get("target")
  return transresp



def texttospeechtvsm(text , sourceLang):
  api_key = "0ELDJvqbaDLzAGPIR1Dfv38ehE21HkMjxWkXYWq-Mk1bajlyyxXMyHGpwb3lD2cz"
  headers = {
    "Content-Type": "application/json",
    "Authorization": api_key
  }
  dataTTS = {
    "en":"ai4bharat/indic-tts-coqui-misc-gpu--t4",
    "as":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
    "brx":"ai4bharat/indic-tts-coqui-misc-gpu--t4",
    "gu":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
    "hi":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
    "kn":"ai4bharat/indic-tts-coqui-dravidian-gpu--t4",
    "ml":"ai4bharat/indic-tts-coqui-dravidian-gpu--t4",
    "mni":"ai4bharat/indic-tts-coqui-misc-gpu--t4",
    "mr":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
    "or":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
    "pa":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
    "ta":"ai4bharat/indic-tts-coqui-dravidian-gpu--t4",
    "te":"ai4bharat/indic-tts-coqui-dravidian-gpu--t4",
    "bn":"ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"
  }

  payload = {
    "pipelineTasks": [
        {
            "taskType": "tts",
            "config": {
                "language": {
                    "sourceLanguage": sourceLang
                },
                "serviceId": dataTTS[sourceLang] ,
                "gender": "female"
            }
        }
    ],
    "inputData": {
        "input": [
            {
                "source": text
            }
        ]
    }
  }

  response = requests.post("https://dhruva-api.bhashini.gov.in/services/inference/pipeline", headers=headers, json=payload)
  bs64 = response.json().get("pipelineResponse")[0].get("audio")[0].get("audioContent")
  return bs64