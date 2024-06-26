from openai import OpenAI
from googlesearch import search
import requests
from bs4 import BeautifulSoup


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
  res = search(searchQuery, num_results=5)
  set1 = set(res)
  return set1


def gettextfromwebsite(url):
  response = requests.get(url)
  if response.status_code == 200:
      soup = BeautifulSoup(response.content, 'html.parser')
      all_text = soup.get_text()
      return all_text
  else:
      return (f"Failed to retrieve the webpage. Status code: {response.status_code}")