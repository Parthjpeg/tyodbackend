from openai import OpenAI
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import threading
import enchant
from operator import itemgetter
from urllib.parse import urlparse
import re


def cleandata(text):
  cleaned_text = text.replace('\n', ' ').replace('\xa0', ' ')
  cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
  return cleaned_text


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
                dataurl = {"url" : link.get('href'), "dist" : enchant.utils.levenshtein(link.get('href'), userQuery)}
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
  thread.join(10)

  if thread.is_alive():
        print("Function timed out")