import re
import time
from ..custom_logger import log
from ..notifications import Common as common_message
def scroll_to_bottom(url, driver, scroll_pause_time, logging_locations):
 start_time = time.perf_counter()
 driver.get(url)
 current_elements_count = None
 new_elements_count  = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
 while new_elements_count != current_elements_count:
  current_elements_count = new_elements_count
  new_elements_count  = scroll_down(current_elements_count, driver, scroll_pause_time, logging_locations)
 return save_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations)
def scroll_down(current_elements_count, driver, scroll_pause_time, logging_locations):
 driver.execute_script('window.scrollBy(0, 50000);')
 time.sleep(scroll_pause_time)
 new_elements_count = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
 log(f'Found {new_elements_count} videos...', logging_locations)
 if new_elements_count == current_elements_count:
  log(common_message.no_new_videos_found(scroll_pause_time * 2), logging_locations)
  time.sleep(scroll_pause_time * 2)
  new_elements_count = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
  if new_elements_count == current_elements_count:
   log('Reached end of page!', logging_locations)
 return new_elements_count
def save_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations):
 elements   = driver.find_elements_by_xpath('//*[@id="video-title"]')
 end_time   = time.perf_counter()
 total_time = end_time - start_time - scroll_pause_time
 log(f'It took {total_time} seconds to find all {len(elements)} videos from {url}\n', logging_locations)
 return elements
def scroll_to_old_videos(url, driver, scroll_pause_time, logging_locations, file_name, txt_exists, csv_exists, md_exists):
 stored_in_txt = store_already_written_videos(file_name, 'txt') if txt_exists else set()
 stored_in_csv = store_already_written_videos(file_name, 'csv') if csv_exists else set()
 stored_in_md  = store_already_written_videos(file_name, 'md' ) if md_exists  else set()
 existing_videos = []
 if stored_in_txt: existing_videos.append(stored_in_txt)
 if stored_in_csv: existing_videos.append(stored_in_csv)
 if stored_in_md:  existing_videos.append(stored_in_md)
 if   len(existing_videos) == 3: visited_videos = existing_videos[0].intersection(existing_videos[1]).intersection(existing_videos[2])
 elif len(existing_videos) == 2: visited_videos = existing_videos[0].intersection(existing_videos[1])
 else:         visited_videos = existing_videos[0]
 log(f'Detected an existing file with the name {file_name} in this directory, checking for new videos to update {file_name}....', logging_locations)
 start_time    = time.perf_counter()
 found_old_videos = False
 while found_old_videos is False:
  found_old_videos = scroll_down_to_old_videos(driver, scroll_pause_time, visited_videos, logging_locations)
 return save_new_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations), stored_in_txt, stored_in_csv, stored_in_md
def store_already_written_videos(file_name, file_type):
 with open(f'{file_name}.{file_type}', 'r', encoding='utf-8') as file:
  if file_type == 'txt' or file_type == 'md': return set(re.findall('(https://www\.youtube\.com/watch\?v=.+?)(?:\s|\n)', file.read()))
  if file_type == 'csv':       return set(re.findall('(https://www\.youtube\.com/watch\?v=.+?),',   file.read()))
def scroll_down_to_old_videos(driver, scroll_pause_time, visited_videos, logging_locations):
 driver.execute_script('window.scrollBy(0, 50000);')
 time.sleep(scroll_pause_time * 2)
 new_elements_count = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
 log(f'Found {new_elements_count} videos...', logging_locations)
 if driver.find_elements_by_xpath('//*[@id="video-title"]')[-1].get_attribute('href') in visited_videos:
  return True
 return False
def save_new_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations):
 elements = driver.find_elements_by_xpath('//*[@id="video-title"]')
 end_time = time.perf_counter()
 total_time = end_time - start_time - scroll_pause_time
 log(f'It took {total_time} seconds to find {len(elements)} videos from {url}\n', logging_locations)
 return elements