from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import os
import re
import yt_dlp as youtube_dl

RESET = "\033[0m"
PURPLE = "\033[34m"
GREEN = "\033[32m"

def clean_url(url):
    return re.sub(r'&pp=[^&]*', '', url)

def get_video(playlist_url, max_videos):
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(playlist_url)

    time.sleep(5) 

    video_links = set()  
    last_count = 0
    
    while len(video_links) < max_videos:
        elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/watch?v=")]')
        for element in elements:
            href = element.get_attribute('href')
            if href:
                clean_href = clean_url(href)
                if clean_href.startswith("https://www.youtube.com/watch?v=") and 'index=' in clean_href:
                    video_links.add(clean_href)
                    if len(video_links) >= max_videos:
                        break

        current_count = len(video_links)
        if current_count > last_count:
            percentage = (current_count / max_videos) * 100
            sys.stdout.write(f"\rProgress: {current_count}/{max_videos} ({percentage:.2f}%)")
            sys.stdout.flush()
            last_count = current_count

        if len(video_links) < max_videos:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(5) 

    driver.quit()

    limited_video_links = list(video_links)[:max_videos]

    print(f"\nCollected {len(limited_video_links)} video links out of requested {max_videos}.")

    return limited_video_links

def download(video_links, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    print(f"\n{PURPLE}Number of videos to download: {len(video_links)}{RESET}")

    for i, link in enumerate(video_links, start=1):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'format': 'best',
                'noplaylist': True, 
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print(f"{PURPLE}Downloading video {i}/{len(video_links)}: {link}{RESET}")
                ydl.download([link])
                print(f"{GREEN}Downloaded {i}/{len(video_links)}: {link}{RESET}")
        except Exception as e:
            print(f"Failed to download video {i}/{len(video_links)}: {link}\nError: {e}")

if __name__ == "__main__":
    playlist_url = input("Enter the YouTube playlist URL: ")
    max_videos = int(input("Enter the maximum number of videos to retrieve: "))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(script_dir, "downloads")
    
    video_links = get_video(playlist_url, max_videos)
    
    if len(video_links) < max_videos:
        print(f"\nWarning: The playlist only contains {len(video_links)} video(s), which is less than the requested {max_videos}.")

    print(f"\nVideo links in the playlist (up to {len(video_links)}):")
    
    for i, link in enumerate(video_links, start=1):
        print(f"{i}. {link}")

    download(video_links, download_dir)
