from openai import OpenAI
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import threading
from Levenshtein import distance
from operator import itemgetter
from urllib.parse import urlparse
import re
import os
import base64
from io import BytesIO
import tempfile

def cleandata(text):
  cleaned_text = text.replace('\n', ' ').replace('\xa0', ' ')
  cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
  return cleaned_text

client = OpenAI()

def Get_Embeddings(embedding_string):
  # response = client.embeddings.create(
  #   input= embedding_string,
  #   model="text-embedding-ada-002"
  # )
  # feature_vector = response.data[0].embedding
  # return feature_vector
  api_key = "1e0c591a85d344d0bc5bd7eb809ad685"#os.environ['embedding_key']
  url = "https://ai-api-dev.dentsu.com/openai/deployments/TextEmbeddingAda2/embeddings?api-version=2024-02-01"#os.environ["embedding_url"]
  hdr ={# Request headers
          'x-service-line': 'CXM',
          'x-brand': 'merkle',
          'x-project': 'Intelligent_M',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
          'api-version': 'v8',
          'Ocp-Apim-Subscription-Key': api_key}
  data =  {
      "input": embedding_string,
      "user": "string",
      "input_type": "query"
  }
  response = requests.post(url=url,headers=hdr , json = data)
  return response.json().get('data')[0].get('embedding')

def getAnswer(messages):
  
  # response = client.chat.completions.create(
  # model="gpt-4o",
  # messages=messages
  # )
  # return response.choices[0].message.content
  api_key = "f9b9ff0924a24048a80d82b259c3f647"#os.environ['completions_key']
  url =  "https://ai-api-dev.dentsu.com/openai/deployments/GPT4o128k/chat/completions?api-version=2024-02-01"#os.environ['completions_url']#os.environ['completions_dentsu']
  hdr ={# Request headers
        'x-service-line': 'CXM',
        'x-brand': 'merkle',
        'x-project': 'Intelligent_M',
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'api-version': 'v8',
        'Ocp-Apim-Subscription-Key': api_key}
  data ={
        "model": "GPT4o128k",
        "messages": messages
        }  
  response = requests.post(url=url,headers=hdr , json = data)
  return response.json().get("choices")[0].get("message").get("content")

def webSearch(searchQuery):
  res = search(searchQuery, num_results=15)
  set1 = set(res)
  print(set1)
  return set1

def getUrls(userQuery):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url= f'https://www.google.com/search?q={userQuery}&ie=utf-8&oe=utf-8&num=20'
    html = requests.get(url,headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')
    urldic = []
    urlset = set()
    for link in soup.find_all('a'):
        dataurl = {}
        if(type(link.get('href')) == str and link.get('href').startswith("http")):
            if (link.get('href').find("google") > 1 or link.get('href').find("youtube") > 1):
                pass
            elif not link.get('href') in urlset:
                urlset.add(link.get('href'))
                dataurl = {"url" : link.get('href'), "dist" : distance(link.get('href'), userQuery)}
                urldic.append(dataurl)
    newlist = sorted(urldic, key=itemgetter('dist'))
    return newlist

def gettextfromwebsitethread(url,all_texts):
  parsed_url = urlparse(url)
  headers = {'Host':parsed_url.netloc}
  try:
    response = requests.get(url , headers=headers)
  except:
    print("something went wrong")
  try:
    if response.status_code == 200:
      soup = BeautifulSoup(response.content, 'html.parser')
      all_text = soup.get_text()
      urldatadic = {}
      urldatadic['url'] = url
      if(len(all_text)>30):
        try:
          urldatadic['data'] = cleandata(all_text)
        except:
           urldatadic['data'] = all_text
        all_texts.append(urldatadic)
      else:
        print ("data irrelevant")
    else:
      print (f"Failed to retrieve the webpage. Status code: {response.status_code}")
  except:
    print("something went wrong")
  
def gettextfromwebsite(url , all_texts):
  
  thread = threading.Thread(target=gettextfromwebsitethread , args= (url,all_texts))
  thread.daemon = True
  thread.start()
  thread.join(3)
  if thread.is_alive():
        print("Function timed out")



def speechtotext(audio_file):
  transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
  )
  final_input = transcription.text
  return (final_input)


# def translatetexttoEnglish(sourceText , sourceLang, targetLang):
#   api_key = "0ELDJvqbaDLzAGPIR1Dfv38ehE21HkMjxWkXYWq-Mk1bajlyyxXMyHGpwb3lD2cz"
#   headers = {
#     "Content-Type": "application/json",
#     "Authorization": api_key
#   }
#   payload = {
#     "pipelineTasks": [
#         {
#             "taskType": "translation",
#             "config": {
#                 "language": {
#                     "sourceLanguage": "mr",
#                     "targetLanguage": "en"
#                 },
#                 "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
#             }
#         }
#     ],
#     "inputData": {
#         "input": [
#             {
#                 "source": "नमस्कार माझा"
#             }
#         ]
#     }
#   }
#   response = requests.post("https://dhruva-api.bhashini.gov.in/services/inference/pipeline", headers=headers, json=payload)
#   print(response.json())

def translateAudioToEnglish(base64Audio, sourceLang, targetLang):
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


def Get_Base64(request):  #Returns the base64 of an image from the temp memory file
    return base64.b64encode(BytesIO(request.data.get('audio').read()).getvalue()).decode('utf-8')


def translatetexttonative(text, sourceLang , targetLang):
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




def texttospeech(text , sourceLang):
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
  bytes = base64.b64decode(bs64, validate=True)
  temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
  speech_file_path = temp1.name
  f = open(speech_file_path, 'wb')
  f.write(bytes)
  f.close()
  return speech_file_path


def texttospeechopenai(text):
  temp1 = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
  speech_file_path = temp1.name
  response = client.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=text
    )
  response.stream_to_file(speech_file_path)
  return speech_file_path
