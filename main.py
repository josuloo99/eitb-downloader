from eitb_api import *

M3U_DOWNLOADER_PATH=None
MP4DECRYPTER_PATH=None
DECRYPT_KEY=None

from typing import Callable, Any

def interactive_search(
    page_size: int = 10
):
   """
   Generic interactive search with pagination.

   Args:
   search_fn: Function that takes search term and returns results
   display_fn: Function to format each result for display
   page_size: Number of results per page
   """
   search_term = input("Idatzi bilatu nahi duzuna: ").strip()

   if not search_term:
      return None

   results = get_search_result_list(search_term)

   if not results:
      print("Ez da emaitzik aurkitu.")
      return None

   current_page = 0
   total_pages = (len(results) - 1) // page_size + 1

   while True:
      # Calculate page bounds
      start = current_page * page_size
      end = min(start + page_size, len(results))
      page_results = results[start:end]

      print(f"\n{'─'*60}")
      print(f"Emaitzak {start+1}-{end} / {len(results)} (Orria {current_page+1}/{total_pages}) | KH: Keinu Hizkuntza")
      print(f"{'─'*60}")

      for i, result in enumerate(page_results, start + 1):
         print_text = f"  [{i:2}] {result.title} ({result.media_type}) {result.platform}"
         if result.sign_lang:
            print_text = print_text + (f" (KH)")
         print(print_text)

      print(f"{'─'*60}")
      nav = []
      if current_page > 0:
         nav.append("[A]urrekoa")
      if current_page < total_pages - 1:
         nav.append("[H]urrengoa")
      nav.extend(["[#] Aukeratu", "[I]rten"])
      print(f"  {' | '.join(nav)}")

      choice = input("\nAukera: ").strip().lower()
      if choice == 'i':
         return None
      elif choice == 'h' and current_page < total_pages - 1:
         current_page += 1
      elif choice == 'a' and current_page > 0:
         current_page -= 1
      elif choice.isdigit():
         idx = int(choice) - 1
         if 0 <= idx < len(results):
               return results[idx]
         print("Aukera ez da baliozkoa")
      else:
         print("Aukera ez da baliozkoa")

if __name__ == "__main__":
   selected = interactive_search(
      page_size=10
   )

   if selected:
      media_details = get_details(selected)
      render_image_from_url(selected.media_url)
      media_details.print_pretty()

      print("\n")

      download_options = []

      if selected.media_type == "Movie":
         download_options.append("[D] Deskargatu filma")
      else:
         download_options.append("[A] Deskargatu serie osoa")
         download_options.append("[D <denboraldia> <kapituluak>] Deskargatu kapitulua(k) (adibidez: D 1 1,2,3)")

      print(f"  {' | '.join(download_options)}")

      choices = input("\nAukera: ").strip().lower().split(" ")

      if not choices:
         print("Aukera ez da baliozkoa")
      elif selected.media_type == "Movie" and choices[0] == "d":
         download_video(media_details.platform, media_details.slug, f"{media_details.title} [{media_details.production_year}]")
      elif selected.media_type == "Series" and choices[0] == "a":
         download_multiple(media_details)
      elif selected.media_type == "Series" and choices[0] == "d":
         try:
            season_number = int(choices[1])
            episode_str = choices[2]
            episode_numbers = [int(e.strip()) for e in episode_str.split(',')]
            download_multiple(media_details, selected_season=season_number, selected_episodes=episode_numbers)
         except:
            print("Aukera ez da baliozkoa")
