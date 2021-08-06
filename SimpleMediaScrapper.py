from re import findall
from requests import get as get_request
from threading import Thread
from os.path import join
from os import mkdir

class MediaScrapper:
    def __init__(self, download_folder="", video_image_regex="", pages_regex_link=""):
        self.download_folder = download_folder + "/"
        self._video_image_regex_link = '<(video .*href=["\'](\S*)["\']|img .*src=["\'](\S*)["\'])' if video_image_regex =="" else video_image_regex
        self._pages_regex_link = '<a .*href=["\'](\S*)["\']' if pages_regex_link =="" else pages_regex_link
        self._requests_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        try: 
            mkdir(self.download_folder) 
        except OSError: 
            pass

    def get_media_links(self, url):
        try:
            res = get_request(url, headers=self._requests_headers)
            return findall(self._video_image_regex_link, res.text)
        except Exception:
            print(f"Could not request url : {url}")
            return ()

    def download_media(self, media_link):
        media_name = media_link.split('/')[-1]
        media_res = get_request(media_link)
        try:
            with open(join(self.download_folder, media_name),'wb') as f:
                f.write(media_res.content)
        except Exception:
            print(f"Could not save file {self.download_folder+media_name} !")

    def download_all_media(self, url, video_key_word="", image_key_word=""):
        media_urls = self.get_media_links(url)
        for main_group, video_link, image_link in media_urls:
            link = ""
            if video_link != '':
                if video_key_word.lower() in video_link.lower() or video_key_word == "":
                    link = video_link.split('?')[0]
            else:
                if image_key_word.lower() in image_link.lower() or image_key_word == "":
                    link = image_link.split('?')[0]
                
            if link != "":
                x = Thread(target=self.download_media, args=(link,), daemon=True)
                x.start()
    
    def download_all_media_pages(self, main_link, page_key_word="", video_key_word="", image_key_word=""):
        all_pages = []
        try:
            res = get_request(main_link, headers=self._requests_headers)
            all_pages = findall(self._pages_regex_link, res.text)
        except Exception:
            print(f"Could not request url: {main_link} !")
        
        for page_url in all_pages:
            if page_key_word.lower() in page_url.lower() or page_key_word == "":
                self.download_all_media(page_url, video_key_word, image_key_word)
        

ms = MediaScrapper(download_folder="media folder")
ms.download_all_media("https://pixabay.com/images/search/iphone%20wallpaper/")
