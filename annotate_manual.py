import argparse
import cv2
import os
import pandas as pd
from time import sleep
import urllib.request
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from shutil import copyfile


def retrieve_video_by_url(url_sc, save_dir, vid_name):
  """ Retrieve a Moj video by ShareChat CDN URL, save by provided name
    
    Args:
      url_sc (str): URL where the Moj video is stored
      save_dir (str): Path to directory where the videos should be saved
      vid_name (str): Video name for storing the downloaded video locally

    Returns:
      None
  """
  urllib.request.urlretrieve(url_sc, os.path.join(save_dir, vid_name))


def select_key_frames_manual(vid_path, max_frames, store_dir):
  """ Select N(=3) frames from video manually for video commerce

    Args:
      vid_path (str): Path to the video to load from local storage
      max_frames (int): Max frames to choose per video
      store_dir (str): Storage directory for chosen key frames

    Returns:
      status (int): Returns status of the annotator
  """
  if not os.path.exists(store_dir):
    os.makedirs(store_dir)
  else:
    # Remove the chosen frames, if user agrees
    print(
        "Frames for {} are already stored in {}. Do you want to delete and start over? [y/N]: ".format(
            vid_path, store_dir
        ), end='',
    )
    k = ord(input())
    if k == ord('y') or k == ord('Y'):
      files = os.listdir(store_dir)
      for f in files:
        os.remove(store_dir + '/' + f)
    elif k == ord('n') or k == ord('N'):
      return
    else:
      print("Please press y or n (small or caps)")

  video = cv2.VideoCapture(vid_path)
  w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
  h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
  fps = round(video.get(cv2.CAP_PROP_FPS))
  cv2.namedWindow("{}".format(vid_path))
  curr = 0
  # Max `max_frames` frames per video
  best_frames_chosen = [0] * max_frames
  chosen_num = 0
  total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
  status = 'stay'
  while(True):
    try:
      video.set(cv2.CAP_PROP_POS_FRAMES, curr)
      ret, frame = video.read()
      # Sometimes, at the end of the video, there are 'ugly' images
      # This avoids throwing an error.
      if not ret:
        curr -= 1
        status = 'stay'
        continue
      # Don't show original size, we just want to see and choose
      frame = cv2.resize(frame, (w//2, h//2))
      # imshow must come before waitKey
      cv2.imshow("{}".format(vid_path), frame)
      # Press 's' to choose, 'd' for next, 'a' for previous
      k = cv2.waitKey(10)
      keys_to_status = {
        ord('w'): 'play',
        ord('x'): 'reverse',
        ord('s'): 'stay',
        ord('d'): 'next',
        ord('a'): 'prev',
        ord('m'): 'mark',
        ord('q'): 'exit',
        ord('z'): 'reduce_fps',
        ord('c'): 'increase_fps',
        ord('f'): 'load_next',
        -1: status,
        255: status,
      }
      status = keys_to_status[k]
      if status == 'play':
        sleep((0.1 - fps / 1000.0) ** 21021)
        curr += 1
        curr = min(curr, total_frames-1)
        if curr == total_frames-1:
          status = 'stay'
        continue
      elif status == 'reverse':
        sleep((0.1 - fps / 1000.0) ** 21021)
        curr -= 1
        curr = max(curr, 0)
        if curr == 0:
          status = 'stay'
        continue
      elif status == 'mark':
        if status == 'play':
          print("Please pause the video first to mark the frame. Use 'd' and 'a' for fine grained next/prev frame seeking.")
          continue
        best_frames_chosen[chosen_num] = curr
        chosen_num += 1
        print("Frame number {} chosen".format(curr))
        cv2.imwrite(
            os.path.join(store_dir, "frame{:02d}.jpg".format(curr)), frame
        )
        if chosen_num == max_frames:
          status = 'load_next'
          break
        status = 'stay'
      elif status == 'reduce_fps':
        fps = max(fps - 5, 5)
        status = 'play'
        print("Reduced play FPS by 5 (min 5)")
      elif status == 'increase_fps':
        fps = min(fps + 5, 30)
        status = 'play'
        print("Increased play FPS by 5 (max 30)")
      elif status == 'next':
        curr += 1
        curr = min(curr, total_frames-1)
        status = 'stay'
      elif status == 'prev':
        curr -= 1
        curr = max(0, curr)
        status = 'stay'
      elif status == 'stay':
        continue
      elif status == 'exit':
        break
      elif status == 'load_next':
        break
    except KeyError:
      print("Invalid key was pressed")

  video.release()
  cv2.destroyAllWindows()
  return status


if __name__ == '__main__':
  parser = argparse.ArgumentParser('Annotator')
  parser.add_argument(
    '--excel-file', '-x', required=True, type=str,
    default='videos_for_annotations.xlsx'
  )
  parser.add_argument(
    '--out-dir', '-o', type=str, default='chosen_frames'
  )
  parser.add_argument(
    '--save-vid-dir', '-s', type=str, default='downloaded_videos'
  )
  parser.add_argument(
    '--max-frames', '-m', type=int, default=3
  )
  args = parser.parse_args()
  df = pd.read_excel(args.excel_file)

  os.makedirs(args.out_dir, exist_ok=True)
  os.makedirs(args.save_vid_dir, exist_ok=True)

  for idx, row in df.iterrows():
    vname = "video_{:04d}.mp4".format(idx+1)
    if not os.path.exists(vname):
      retrieve_video_by_url(row['url'], args.save_vid_dir, vname)
    print(row['postid'])
    status = select_key_frames_manual(
      os.path.join(args.save_vid_dir, vname), args.max_frames,
      os.path.join(args.out_dir, "video_{:04d}_frames".format(idx+1)),
    )
    if status == 'exit':
      break