from openai import OpenAI
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import threading

client = OpenAI()

def Get_Embeddings(embedding_string):
  response = client.embeddings.create(
    input= embedding_string,
    model="text-embedding-ada-002"
  )
  feature_vector = response.data[0].embedding
  return feature_vector

def getAnswer(messages):
  
  response = client.chat.completions.create(
  model="gpt-4o",
  messages=messages
  )
  return response.choices[0].message.content

def googleSearch(searchQuery):
  res = search(searchQuery, num_results=2)
  set1 = set(res)
  print(set1)
  return set1

def gettextfromwebsitethread(url,all_texts):
  try:
    response = requests.get(url)
  except:
    print("something went wrong")
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    all_text = soup.get_text()
    all_texts.append(all_text)
  else:
    print (f"Failed to retrieve the webpage. Status code: {response.status_code}")
  
def gettextfromwebsite(url , all_texts):
  
  thread = threading.Thread(target=gettextfromwebsitethread , args= (url,all_texts))
  thread.daemon = True
  thread.start()
  thread.join(10)

  if thread.is_alive():
        print("Function timed out")