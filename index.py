import os
import subprocess
import time
import datetime
from wand.color import Color
from wand.display import display
from wand.drawing import Drawing
from wand.image import Image
import json
import requests


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


def get_the_voice(words):
    token_url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=MbzkUpa5EI2bdxNF9rOtDzIz&client_secret=9a7a60b57c108563faeb1eb134b32f3a'
    tts_url = 'https://tsn.baidu.com/text2audio'
    res = requests.get(token_url)
    data = res.json()
    token = data['access_token']
    params = {
        'tex':','.join(words),
        'tok':token,
        'cuid':'121212121212121212',
        'ctp':"1",
        'lan':"zh"
    }
    r = requests.get(tts_url,params=params)
    if r.headers['content-type'] == 'audio/mp3':
        file_name = './voice/_{0}.mp3'.format(int(time.time()))
        with open(file_name,'wb') as mp3:
            mp3.write(r.content)
        return file_name
    return None


def read_the_voice(file_name):
    p = subprocess.Popen('ffprobe -i {0} -print_format json  -show_format  -v 0 '.format(file_name),stdout=subprocess.PIPE,shell=True,bufsize=100000)
    p.wait()
    data = p.stdout.read()
    data = str(data).replace("\\n",'')[2:-1]
    data = json.loads(data)
    audio_len = int(float(data['format']['duration'])) + 1
    return audio_len

if __name__ == '__main__':
    words = read_word("./word.txt")
    vioce_name = get_the_voice(words)
    print('生产音频文件',vioce_name)
    video_time = read_the_voice(vioce_name)
    video_fps = 30
    offset = image_height // (video_fps * video_time)
    timestamp = int(time.time())
    dir_name = './imgs_{0}'.format(timestamp)
    os.makedirs(dir_name)
    for i in range(video_fps * video_time) :
        filename = './imgs_{0}/{1}.jpg'.format(timestamp,i+1)
        now_off = offset * i 
        draw_one_picture(filename,words,now_off)
    video_name = './video/{0}.mp4'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    # 这里因为码率的问题 只能吧文件改成mkv格式
    result_name = './results/{0}.mkv'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    # print("ffmpeg -f image2 -i ./imgs_{0}/%d.jpg ./results/{1}.mp4".format(timestamp,video_name))
    p = subprocess.Popen("ffmpeg -f image2 -i ./imgs_{0}/%d.jpg {1}".format(timestamp,video_name),shell=True,stdout=subprocess.PIPE)
    p.wait()
    print('生成文件名为',video_name)
    print("开始音频视频合并")
    
    p = subprocess.Popen('ffmpeg -i {0} -i {1} -strict -2 {2} '.format(os.path.abspath(video_name),os.path.abspath(vioce_name),os.path.abspath(result_name)),shell=True,stdout=subprocess.PIPE)
    p.wait()
    print("合并完成 视频名",result_name)
 
    
  
