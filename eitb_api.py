import requests
from term_image.image import from_url
import subprocess
import os
from config import M3U_DOWNLOADER_PATH, MP4DECRYPTER_PATH, DECRYPT_KEY
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

eitb_platforms_api = {
   'etbon': 'https://etbon.eus/api/v1',
   'primeran' : 'https://primeran.eus/api/v1',
   'makusi': 'https://makusi.eus/api/v1',
}

SEARCH_API_REQUEST = '/search?q={query}&page={page}&pageSize={limit}'
SERIES_API_REQUEST = '/series/{series_slug}'
MOVIES_API_REQUEST = '/media/{movie_slug}'

HEADERS = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
   'Accept': 'application/json, text/plain, */*',
   'Accept-Language': 'eu,en-US;q=0.7,en;q=0.3'
}

class SearchResult:
   def __init__(self, id: int, title: str, media_type: str, description: str, platform: str, slug: str, sign_lang: bool, media_url: str = None):
      self.id = id
      self.title = title
      self.media_type = media_type
      self.description = description
      self.platform = platform
      self.slug = slug
      self.sign_lang = sign_lang
      self.media_url = media_url
   def print_row(self):
      print(f"{self.title} | {self.media_type} | {self.description} | {self.platform} | {self.slug}")

class EpisodeDetails:
   def __init__(self, title: str, description: str, episode_number: int, season_number: int, slug: str):
      self.title = title
      self.description = description
      self.episode_number = episode_number
      self.season_number = season_number
      self.slug = slug

class SeasonDetails:
   def __init__(self, season_number: int, episodes: EpisodeDetails):
      self.season_number = season_number
      self.episodes = episodes

class MediaDetails:
   def __init__(self, id: int, title: str, media_type: str, description: str, production_year: int, platform: str, slug: str, media_url: str = None, seasons: SeasonDetails = None, age_rating: int = 0, audio_languages: list = None, subtitles: list = None):
      self.id = id
      self.title = title
      self.media_type = media_type
      self.description = description
      self.production_year = production_year
      self.platform = platform
      self.slug = slug
      self.image_url = media_url
      self.seasons = seasons or []
      self.age_rating = age_rating
      self.audio_languages = audio_languages or []
      self.subtitles = subtitles or []

   def print_pretty(self):
      print(f"Title: {self.title}")
      print(f"Type: {self.media_type}")
      print(f"Description: {self.description}")
      print(f"Year: {self.production_year}")
      print(f"Platform: {self.platform}")
      print(f"Slug: {self.slug}")
      print(f"Age Rating: {self.age_rating}")
      print(f"Audio Languages: {', '.join(self.audio_languages)}")
      print(f"Subtitles: {', '.join(self.subtitles)}")
      if self.media_type == 'Series':
         for season in self.seasons:
            print(f"  Season {season.season_number}:")
            for episode in season.episodes:
               print(f"    Episode {episode.episode_number}: {episode.title}")

def get_available_platforms() -> list:
   return list(eitb_platforms_api.keys())

def make_api_request(platform: str, request_path: str) -> dict:
   base_url = eitb_platforms_api.get(platform)
   if not base_url:
      raise ValueError(f"Unknown platform: {platform}")

   url = base_url + request_path
   response = requests.get(url, headers=HEADERS)
   response.raise_for_status()
   return response.json()

def search_media_json(platform: str, query: str, page: int, limit: int) -> dict:
   request_path = SEARCH_API_REQUEST.format(query=query, page=page, limit=limit)
   return make_api_request(platform, request_path)

def get_media_details_json(platform: str, media_type: str, slug: str) -> dict:
   request_path = ''
   if media_type == 'Series':
      request_path = SERIES_API_REQUEST.format(series_slug=slug)
   elif media_type == 'Movie':
      request_path = MOVIES_API_REQUEST.format(movie_slug=slug)
   else:
      raise ValueError(f"Unsupported media type: {media_type}")

   return make_api_request(platform, request_path)

def get_search_result_list(query: str, platform: str = None, page: int = 1, limit: int = 5) -> SearchResult:
   searchResults = []
   platforms = [platform] if platform else get_available_platforms()
   invalid = [p for p in platforms if p not in eitb_platforms_api]
   if invalid:
      raise ValueError(f"Unknown platform(s): {', '.join(invalid)}")

   for plat in platforms:
      search_results = search_media_json(plat, query, page, limit)
      for item in search_results.get('data', []):
         id = int(item.get('id'))
         title = item.get('title', 'N/A')
         media_type = item.get('collection', 'N/A')
         media_type = 'Series' if media_type == 'series' else 'Movie' if media_type == 'media' else media_type
         description = item.get('description', 'N/A') or 'N/A'
         slug = item.get('slug', 'N/A')
         sign_lang = slug.endswith("-kh")
         show_images = item.get('images', [])
         if len(show_images) > 1:
            media_url = show_images[1].get('file')
         else:
            media_url = show_images[0].get('file')

         result = SearchResult(id, title, media_type, description, plat, slug, sign_lang, media_url)
         searchResults.append(result)
   return searchResults

def render_image_from_url(image_url: str):
   try:
      img = from_url(image_url)
      img.draw()
   except Exception as e:
      print(f"Error rendering image: {e}")

def get_details(data: SearchResult) -> MediaDetails:
   id = data.id
   title = data.title
   media_type = data.media_type
   platform = data.platform
   description = data.description
   slug = data.slug
   media_url = data.media_url
   seasons = []
   age_rating = None
   audio_languages = []
   subtitles = []

   media_info_json = get_media_details_json(platform, media_type, slug)

   if media_info_json:
      # Common fields
      production_year = int(media_info_json.get('production_year', 0))
      age_rating = media_info_json.get('age_rating', None)
      if age_rating is not None:
         age_rating = int(age_rating.get('age', None))

      audio_languages_json = media_info_json.get('audios', [])
      audio_languages = []
      for audio in audio_languages_json:
         lang = audio.get('label', 'N/A')
         audio_languages.append(lang)

      # Series specific fields
      if media_type == 'Series':
         seasons_data = media_info_json.get('seasons', [])
         seasons = []
         for season in seasons_data:
            season_number = int(season.get('number'))
            episodes_list = []
            for episode in season.get('episodes', []):
               ep_title = episode.get('title', 'N/A')
               ep_description = episode.get('description', 'N/A') or 'N/A'
               ep_number = int(episode.get('episode_number', 0))
               ep_slug = episode.get('slug', 'N/A')
               episode_details = EpisodeDetails(ep_title, ep_description, ep_number, season_number, ep_slug)
               episodes_list.append(episode_details)
            seasons.append(SeasonDetails(season_number, episodes_list))

         subtitles_lenguages_json = media_info_json.get('subtitles', [])
         subtitles = []
         for subtitle in subtitles_lenguages_json:
            label = subtitle.get('label', 'N/A')
            subtitles.append(label)

      # Movie specific fields
      elif media_type == 'Movie':
         subtitles_lenguages_json = media_info_json.get('subtitles', [])
         subtitles = []
         for subtitle in subtitles_lenguages_json:
            language = subtitle.get('language', None)
            if language:
               label = language.get('label', 'N/A')
               subtitles.append(label)

      return MediaDetails(id, title, media_type, description, production_year, platform, slug, media_url, seasons, age_rating, audio_languages, subtitles)

   else:
      raise ValueError("Unsupported media type")

def get_episode_slug(media_details: MediaDetails, season_number: int, episode_number: int):
   for season in media_details.seasons:
      if season.season_number == season_number:
         for episode in season.episodes:
            if episode.episode_number == episode_number:
               return episode.slug
   return None

def download_multiple(media_details: MediaDetails, selected_season: int = None, selected_episodes: list = None, max_workers: int = 3):
   if not os.path.exists(media_details.title):
      os.makedirs(media_details.title)

   download_tasks = []

   for season in media_details.seasons:
      if selected_season and season.season_number != selected_season:
         continue
      season_path = f"{media_details.title}/Season {season.season_number}"
      if not os.path.exists(season_path):
         os.makedirs(season_path)
      for episode in season.episodes:
         if selected_episodes and episode.episode_number not in selected_episodes:
            continue
         ep_num = episode.episode_number if episode.episode_number != 0 else episode.slug
         filename = f"{ep_num}. {episode.title}"
         file_path = f"{media_details.title}/Season {season.season_number}"
         download_tasks.append((media_details.platform, episode.slug, file_path, filename))

   with ThreadPoolExecutor(max_workers=max_workers) as executor:
      futures = [executor.submit(download_video, *task) for task in download_tasks]
      for future in futures:
         future.result()

def download_video(domain, video_id, path = "./", in_name=None):
   """
   Downloads and decrypts video using N_m3u8DL-RE based on a specific URL structure.
   """
   name = in_name if in_name else video_id
   manifest_url = f"https://{domain}.eus/manifests/{video_id}/eu/widevine/dash.mpd"

   command = [
      M3U_DOWNLOADER_PATH,
      manifest_url,
      "--save-dir", path,
      "--save-name", name,
      "--key", DECRYPT_KEY,
      "--decryption-binary-path", MP4DECRYPTER_PATH,
      "--auto-select",
      "-mt",
      "-M", "format=mp4",
      "--del-after-done",
      "--check-segments-count", "false"
   ]

   print(f"Processing: {name}...")
   result = subprocess.run(command)

   if result.returncode != 0:
      print(f"ERROR: Something went wrong with {name}!")

   return result.returncode