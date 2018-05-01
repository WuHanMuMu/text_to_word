import datetime
import json
import os
import subprocess
import time

import requests
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
line_split = 30
# 每帧图片高度
image_height = 400
# 每帧图片宽度
image_width = 900  
# 视频帧数
video_fps = 30


def read_word(filename:str):
    words = []
    with open(filename,encoding='utf8') as file:
        for line in file.readlines():
            if line.strip().replace(os.linesep,''):
                words.append(line.strip().replace(os.linesep,''))
    return words


def cal_offset(words,video_time):
    lines = 0
    offset_result = []
    print(words)
    # 这里用每一行的字数 来 判断偏移值
    total = 0
    for word in words:
        lines = lines + len(word) // line_word_num + 1
        total = total + len(word)
    word_time = video_time / total
    # lines = len(words)// line_word_num  + 1
    # 总高度/页高 * 页高 / 时间
    print(lines)
    total_height = lines * line_height + lines * line_split
    # height 3900 
    print(total_height, video_time)
    offset = total_height / (video_time * video_fps)
    if total_height < image_height:
        offset = 0
    return offset


def cal_height(line):
    return (line + 1) * line_height + line * line_split


def cal_offset_v2(words,video_time):
    total = 0
    res = []
    for word in words:
        total = total + len(word)
    word_time = video_time / total
    print('totalheigth',cal_height(70))
    for index,val in enumerate(words):
        '''
            if index < 8:
                height = cal_height(index)
            else :
                height = cal_height(index)
        '''
        # print(index,val)
        if index < 8:
            height = cal_height(index)
        else :
            height = line_height
        # height = cal_height(len(val) // line_word_num + 1)
        time = len(val) * word_time
        
        print ('index====>',index,height,time)
        offset = height / (time * video_fps) / 3
        # res.append(offset)
        print(sum([offset] * (int(time * video_fps) + 1)))
        res = res + [offset] * (int(time * video_fps) + 1)
    return res


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
                    line = line + 1
                    if y < -10:
                        continue
                    if y > image_height:
                        break
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


def multi_voice(words,token):
    length = len(words)
    file_names = []
    def voice(word,token):
        tts_url = 'https://tsn.baidu.com/text2audio'
        params = {
            'tex':word,
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
        return False
    for i in range((length// 500 + 1)):
        i = int(i)
        word = words[ int(i * 500):int((i+1) * 500)]
        file_name = voice(word,token)
        if file_name:  
            file_names.append(file_name)
    result_voice_name = './voice/_{0}.mp3'.format(int(time.time()) + 100)
    format_name = '|'.join(file_names)
    p = subprocess.Popen('ffmpeg -i "concat:{0}" -c copy {1} -v 0'.format(format_name,result_voice_name),shell=True)
    p.wait()
    return result_voice_name


def get_the_voice(words):
    token_url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=MbzkUpa5EI2bdxNF9rOtDzIz&client_secret=9a7a60b57c108563faeb1eb134b32f3a'
    tts_url = 'https://tsn.baidu.com/text2audio'
    res = requests.get(token_url)
    data = res.json()
    token = data['access_token']
    total_word = ','.join(words) 
    if len(total_word) > 500 :
        file_name = multi_voice(total_word,token)
        return file_name
    else :
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
    data = str(data).replace("\\n",'').replace("\\r","")[2:-1]
    data = json.loads(data)
    audio_len = int(float(data['format']['duration'])) + 1
    return audio_len


if __name__ == '__main__':
    words = read_word("./word.txt")
    vioce_name = get_the_voice(words)
    print('生产音频文件',vioce_name)
    video_time = read_the_voice(vioce_name)
    print('生成音频长度为',video_time ,'秒')
    offset = cal_offset(words,video_time)
    offset = cal_offset_v2(words,video_time)
    # print("计算出每帧偏移值为",offset)
    timestamp = int(time.time())
    dir_name = './images/imgs_{0}'.format(timestamp)
    os.makedirs(dir_name)
    video_off = 0
    print(video_fps * video_time)
    print(sum(offset))
    for i in range(video_fps * video_time) :
        filename = './images/imgs_{0}/{1}.jpg'.format(timestamp,i+1)
        # now_off = int(offset[i] * i)
        video_off = video_off + offset[i]
        print('===>',i,video_off,int(video_off))
        draw_one_picture(filename,words,int(video_off))
    video_name = './video/{0}.mp4'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    # 这里因为码率的问题 只能吧文件改成mkv格式
    result_name = './results/{0}.mkv'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    # print("ffmpeg -f image2 -i ./imgs_{0}/%d.jpg ./results/{1}.mp4".format(timestamp,video_name))
    p = subprocess.Popen("ffmpeg -f image2 -i ./images/imgs_{0}/%d.jpg {1} -v 0".format(timestamp,video_name),shell=True,stdout=subprocess.PIPE)
    p.wait()
    print(p.communicate())
    print('生成文件名为',video_name)
    print("开始音频视频合并")
    
    p = subprocess.Popen('ffmpeg -i {0} -i {1} -strict -2 {2} -v 0'.format(os.path.abspath(video_name),os.path.abspath(vioce_name),os.path.abspath(result_name)),shell=True,stdout=subprocess.PIPE)
    p.wait()
    print("合并完成 视频名",result_name)
