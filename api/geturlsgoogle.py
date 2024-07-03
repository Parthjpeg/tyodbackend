import requests
from bs4 import BeautifulSoup
googleTrendsUrl = 'https://google.com'
response = requests.get(googleTrendsUrl)


# # # print(response.status_code)
# # # if response.status_code == 200:
# # #     g_cookies = response.cookies.get_dict()
# # # #AEC=AQTF6HxDo-Ho0BSdFz_biwGezViZckldJJ_HqkZ8mjykFG0lLgPMYVKJZ6A; NID=515=QDB_YhAD_zKaxYD137tZt8Vy2vCzLWnAsZYMs_A_sKWo7mlVTF55GR-OcrbkNOwTU1DjqLwepcd8tCMPjeAEOLj1GmJrNPcC99rht8jPNWq_m6djqDvyxJDtb101IgZl-WyZuPAUjEiGpUHSIJ5aW-nmmz7cLoEd7Q3kY4kLTgs
# # # print(g_cookies)
# # # cok = ""
# # # for key in g_cookies.keys():
# # #     cok=cok+key
# # #     cok=cok+"="
# # #     cok=cok+g_cookies.get(key)
# # #     cok=cok+";"


# # # cok = cok[:-1]
# # # print (cok)
# # # headers = {'User-agent': 'your bot 0.1' ,'Cookie': cok}
# # # page = requests.get("https://www.google.com/search?q=getting+links+from+a+google+search+page+python&rlz=1C1ONGR_enIN1055IN1055&oq=getting+links+from+a+google+search+&gs_lcrp=EgZjaHJvbWUqBwgBECEYoAEyCQgAEEUYORifBTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRifBdIBCTEwMDgyajBqN6gCALACAA&sourceid=chrome&ie=UTF-8" , headers=headers)
# # # print(page.content)
# # # soup = BeautifulSoup(page.text, 'html.parser')
# # # urls = []
# # # for link in soup.find_all('a'):
# # #     print(link.get('href'))
# # # print (urls)
# # from bs4 import BeautifulSoup
# # import requests
# # from nltk.corpus import stopwords
# # import enchant
# # from operator import itemgetter

# # userQuery = input("Enter your question")
# # userQuery=userQuery.replace(" ", "+")
# # print(userQuery)
# # def getUrls(userQuery):
# #     headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
# #     url= f'https://www.google.com/search?q={userQuery}&ie=utf-8&oe=utf-8&num=20'
# #     html = requests.get(url,headers=headers)
# #     soup = BeautifulSoup(html.text, 'html.parser')
# #     urldic = []
# #     urlset = set()
# #     for link in soup.find_all('a'):
# #         dataurl = {}
# #         if(type(link.get('href')) == str and link.get('href').startswith("http")):
# #             if (link.get('href').find("google") > 1 or link.get('href').find("youtube") > 1):
# #                 pass
# #             elif not link.get('href') in urlset:
# #                 urlset.add(link.get('href'))
# #                 dataurl = {"url" : link.get('href'), "dist" : enchant.utils.levenshtein(link.get('href'), userQuery)}
# #                 urldic.append(dataurl)
# #     newlist = sorted(urldic, key=itemgetter('dist'))
# #     return newlist


# import re
# text = " \n \n text with escape stuff"
# print(text)
# clean = re.sub(r"[^. 0-9a-z]", "", text, re.IGNORECASE)
# print(clean)


   