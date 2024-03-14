from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
import requests
import pandas as pd
import supabase_keys as supa
import sys
from supabase import create_client, Client
import re
import time
import undetected_chromedriver as uc

url = "https://mangaplus.shueisha.co.jp/updates"

# driver = webdriver.Chrome(executable_path=r"/Users/brothersontech/Desktop/Programming/Portfolio/mangaDisplayProject/chromedriver")

#options = webdriver.ChromeOptions() 
#options.headless = True
#options.add_argument("start-maximized")
#options.add_experimental_option("excludeSwitches", ["enable-automation"])
#options.add_experimental_option('useAutomationExtension', False)
driver = uc.Chrome()

# driver = webdriver.Chrome()
driver.get(url)
# r = requests.get(url)

action = ActionBuilder(driver)
action.pointer_action.move_to_location(0, 50)
action.pointer_action.click()
action.perform()

# driver.implicitly_wait(10)
mangas = driver.find_elements(By.CLASS_NAME, "UpdatedTitle-module_titleWrapper_2EQIT")
# mangas = driver.find_elements(By.XPATH, "//*[contains(text(), 'Today')]")
newMangas = []
print(len(mangas))

for i in range(0, len(mangas)):
	if('UP' in str(mangas[i].get_attribute('innerText'))):
		newMangas.append(mangas[i])

print(len(newMangas))

listOfNewTitles = []
listOfMangaLinks = []
listOfMangaAuthors = []
listOfMangaImageURLs = []
listOfMangaDescUrls = []

animePlanetURL = "https://www.anime-planet.com/manga/"


for i in range(0, len(newMangas)):
	#Get titles
	mangaTitleElement = newMangas[i].find_element(By.CLASS_NAME, "UpdatedTitle-module_titleName_1QO_s")
	mangaTitle = mangaTitleElement.get_attribute('innerText')
	listOfNewTitles.append(mangaTitle)

	#Get authors
	#mangaAuthor = newMangas[i].find_element(By.CSS_SELECTOR, "div.UpdatedTitle-module_titleWrapper_2EQIT:nth-child(" + str(i+1) + ") > a:nth-child(1) > div:nth-child(1) > div:nth-child(2) > p:nth-child(2)").get_attribute('innerText')
	mangaAuthorElement = newMangas[i].find_element(By.CLASS_NAME, "UpdatedTitle-module_author_1ltec")
	mangaAuthor = (mangaAuthorElement.get_attribute('innerText'))
	listOfMangaAuthors.append(mangaAuthor)

	#Get Links:
	mangaLinkPrefix = "https://mangaplus.shueisha.co.jp"
	#mangaLinkElement = newMangas[i].find_element(By.CLASS_NAME, "UpdatedTitle-module_titleName_1QO_s")
	#mangaLink = newMangas[i].find_element(By.XPATH, "//*[@id='app']/div[2]/div/div[2]/div/div[4]/main/div[1]/div[1]/div/div[1]/a").get_attribute('href')
	mangaLink = newMangas[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
	print(mangaLink)
	# print(newMangas[i].find_element(By.CSS_SELECTOR, "div.UpdatedTitle-module_titleWrapper_2EQIT:nth-child(" + str(i+1) + ") > a:nth-child(1)").get_attribute('href'))
	listOfMangaLinks.append(mangaLink)

	#Get Image:
	mangaImgUrl = newMangas[i].find_element(By.TAG_NAME, "img").get_attribute('src')
	listOfMangaImageURLs.append(mangaImgUrl)

	
	mangaTitleMod = re.sub(r"[^a-zA-Z0-9]+", ' ', mangaTitle).strip()
	mangaTitleMod = mangaTitleMod.replace(' ', '-').lower()
	print(mangaTitleMod)

	mangaDescUrl = animePlanetURL + mangaTitleMod
	listOfMangaDescUrls.append(mangaDescUrl)
	

# for i in range(len(listOfNewTitles)):
# 	print(listOfNewTitles[i])
# 	print(listOfMangaAuthors[i])
# 	print("Link: " +  str(listOfMangaLinks[i]))
# 	print("IMG Link: " + str(listOfMangaImageURLs[i]))
# 	print("--------------")

#driver.close()
listOfMangaDesc = []
for url in listOfMangaDescUrls:
	print(url)
	driver.get(url)
	
	mangasDesc = driver.find_element(By.CLASS_NAME, "synopsisManga").get_attribute('innerText')
	listOfMangaDesc.append(mangasDesc)
	time.sleep(2)	

driver.close()
driver.quit()


dictManga = {'id': 1, 'title': listOfNewTitles, 'author': listOfMangaAuthors, 'url': listOfMangaLinks, 'img_url': listOfMangaImageURLs, 'manga_description': listOfMangaDesc}

df = pd.DataFrame(dictManga)
print(df)
df.reset_index(drop=True, inplace=True)



supaBaseURL = supa.SUPABASE_URL
supabaseKey = supa.SUPABASE_KEY

supaClient: Client = create_client(supaBaseURL, supabaseKey)
#clear db
supaClient.table('manga_table').delete().eq('id', 1).execute()

data = supaClient.table('manga_table').insert(df.to_dict('records')).execute()

