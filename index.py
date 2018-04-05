import os
import subprocess
import time
import datetime
from wand.color import Color
from wand.display import display
from wand.drawing import Drawing
from wand.image import Image

# 每一行最多35个字
line_word_num = 35
# 行首空50px 
line_block = 50 
# 行高50px
line_height = 20
# 行间距20px
line_split = 20
# 每帧图片高度
image_height = 400
# 每帧图片宽度
image_width = 900  


def read_word(filename):
    words = []
    with open(filename) as file:
        for line in file.readlines():
            if line.strip().replace(os.linesep,''):
                words.append(line.strip().replace(os.linesep,''))
    return words

def draw_one_picture(filename,words,offset,height=400,width=900):
    with Color("#FFFACD") as bg:
        with Image(width=width,height=height,background=bg) as image:
            draw = Drawing()
            draw.font = './fonts/dq.otf'
            draw.font_size = 20
            line = 0
            for word in words:
                word_len = len(word) 
                for i in range((word_len // line_word_num) + 1):
                    line_word = word[i*line_word_num:(i+1)*line_word_num]
                    y = line_block + line * line_split - offset 
                    if y < 0:
                        y = 0
                    if i == 0:
                        draw.text(line_block, y, line_word)
                    else:
                        draw.text(line_split, y, line_word)
                    draw(image)
                    # display(image)
                    line = line + 1
            image.save(filename=filename)


if __name__ == '__main__':
    words = read_word("./word.txt")
    video_time = 1
    video_fps = 30
    offset = image_height // (video_fps * video_time)
    timestamp = int(time.time())
    dir_name = './imgs_{0}'.format(timestamp)
    os.makedirs(dir_name)
    for i in range(video_fps * video_time) :
        filename = './imgs_{0}/{1}.jpg'.format(timestamp,i+1)
        now_off = offset * i 
        draw_one_picture(filename,words,now_off)
    result_name = datetime.datetime.now().strftime('%Y-%m-%d')
    print("ffmpeg -f image2 -i ./imgs_{0}/%d.jpg ./results/{1}.mp4".format(timestamp,result_name))
    p = subprocess.Popen("ffmpeg -f image2 -i ./imgs_{0}/%d.jpg ./results/{1}.mp4".format(timestamp,result_name),shell=True)
    p.wait()
    print('生成文件名为',result_name)
