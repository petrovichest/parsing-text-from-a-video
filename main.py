import os
import re
from threading import Thread
from PIL import Image, ImageOps
import cv2
import pytesseract
import numpy as np
import datetime
import csv_controller


class VideoTextFinder:
    def __init__(self):
        # write your options
        self.video_path = 'video.mp4'
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        with open('path_black_list.txt', 'r', encoding='utf-8') as f:
            self.path_black_list = [x.strip() for x in f.read().split('\n') if x]

        # Directory for save and read frames from video
        self.frames_folder_path = './frames_test'
        # count of threads only for text recognize. Less than 10-15 threads recommended.
        self.threads_count = 10
        # get every frame you need
        self.get_every_this_frame = 10
        # frames per second in your video
        self.vide_fps = 60
        # just a warehouse of frames
        self.all_frames = []

    def video_create_frame_array(self):
        # create frames and crop if found template
        template = cv2.imread('template.jpg')
        self.video = cv2.VideoCapture(self.video_path)
        currentFrame = 1
        frame_number = 0
        while True:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            ret, frame = self.video.read()
            if not ret:
                break

            try:
                os.mkdir(self.frames_folder_path)
            except:
                pass

            name = self.frames_folder_path + '/frame_' + str(currentFrame) + '.jpg'
            print('Creating...' + name)
            Thread(target=self.save_thread, args=(name, frame, template, name)).start()
            print(f'frame num - {currentFrame}')
            currentFrame += 1
            frame_number += self.get_every_this_frame

        # When everything done, release the capture
        cv2.destroyAllWindows()
        print('parsing finished')

    def save_thread(self, name, frame, template, img_path):
        # saving frame
        cv2.imwrite(name, frame)
        # comment out the code below if you don't need to crop the image
        res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if self.texted_or_not(name, zip(*loc[::-1])):
            # crop border
            border = (0, 300, 0, 0)  # left, up, right, bottom
            im = Image.open(img_path)
            croped = ImageOps.crop(im, border)
            croped.save(img_path)

    def texted_or_not(self, name, ziped):
        for pt in ziped:
            print(name, 'texted')
            return True
        return False

    def get_frames_array_and_start_finder(self):
        self.frames_array = os.listdir(self.frames_folder_path)
        for thread_num in range(self.threads_count):
            Thread(target=self.one_thread_text_recognizer,
                   args=(self.frames_array[thread_num::self.threads_count], thread_num)).start()

    def one_thread_text_recognizer(self, frames, th_num):
        for frame in frames:
            self.frame_text_finder(f'{self.frames_folder_path}/{frame}')

    def frame_text_finder(self, path):
        if path in self.path_black_list:
            return
        self.path_black_list.append(path)
        with open('path_black_list.txt', 'a') as f:
            f.write(f'{path}\n')
        print(path)
        image = cv2.imread(path)
        text = pytesseract.image_to_string(image).strip()
        regex = re.compile('[^a-zA-Z]')
        text = regex.sub('', text)
        if text:
            # convert frame number to time
            time = int(path.split('_')[-1].strip('.jpg')) // (self.vide_fps // self.get_every_this_frame)
            print(time)
            frame_time = str(datetime.timedelta(seconds=time))
            print(frame_time, path, [text.strip('\n\x0c')])
            # saving text and time to csv file
            data = [[frame_time, text, path]]
            csv_controller.csv_writer(data)


if __name__ == '__main__':
    pr = VideoTextFinder()
    # open video and create frames
    pr.video_create_frame_array()
    # finding text on frames
    pr.get_frames_array_and_start_finder()
