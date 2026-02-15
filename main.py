from eitb_api import *

M3U_DOWNLOADER_PATH=None
MP4DECRYPTER_PATH=None
DECRYPT_KEY=None

from typing import Callable, Any

def interactive_search(
    search_fn: Callable[[str], list],
    display_fn: Callable[[Any], str] = str,
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

   results = search_fn(search_term)

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

      print(f"\n{'─'*50}")
      print(f"Emaitzak {start+1}-{end} / {len(results)} (Orria {current_page+1}/{total_pages})")
      print(f"{'─'*50}")

      for i, result in enumerate(page_results, start + 1):
         print(f"  [{i:2}] {display_fn(result)}")

      print(f"{'─'*50}")
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
      search_fn=get_search_result_list,
      display_fn=lambda r: f"{r.title} ({r.media_type}) [{r.platform}]",
      page_size=10
   )

   if selected:
      details = get_details(selected)
      render_image_from_url(selected.media_url)
      details.print_pretty()