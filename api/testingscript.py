from googlesearch import search
import requests
from bs4 import BeautifulSoup
import threading


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
  
  l = []
  thread = threading.Thread(target=gettextfromwebsitethread , args= (url,all_texts))
  thread.daemon = True
  thread.start()
  thread.join(10)

  if thread.is_alive():
        print("Function timed out")
  return all_texts



urls = googleSearch("python to print hello world")
all_texts = []  # This list will store all the texts

for url in urls:
   print(url)
   gettextfromwebsite(url , all_texts)
print (len(all_texts))
   



