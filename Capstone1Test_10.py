#!/usr/bin/env python
# coding: utf-8

# In[12]:


import tkinter as tk
    
from tkinter.font import Font
from gtts import gTTS    #gTTS install 필요
from playsound import playsound    #playsound install 필요
from PIL import Image
from PIL import ImageGrab
from pygame import mixer  # pygame install 필요
from pytesseract import * # tesseract 응용 프로그램 설치 필요
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'  # 테서렉트가 설치된 경로를 지정해줘야 작동한다.

import random
import time
import threading
import os
import configparser
import sys
import requests, bs4


# In[15]:


# 전역변수 설정

word_txt, meaning_txt, spelling_txt, w_note = [], [] ,[], [] # 선언 및 초기화 해준다.

def read_words():  # 리스트에 새롭게 입력된 단어 집어넣기
    file_path = os.getcwd()
    f = open(file_path + "/Words.txt", 'r')

    word_txt = f.readlines()  # 한 줄을 한 개의 요소로 리스트에 전부 담는다.
    print('현재 저장된 단어의 갯수는 :', len(word_txt))    # 저장된 단어의 수가 나올 것.

    meaning_txt = [0 for i in range(len(word_txt))]
    spelling_txt = [0 for i in range(len(word_txt))]  # 이만큼 인덱스를 넓혀주지 않으면 out of range 나옴.

    for i in range(0, len(word_txt)):
        meaning_txt[i] = word_txt[i].split(' ')[0]   # meaning_txt 에 한글뜻이 전부 담긴다.
        spelling_txt[i] = word_txt[i].split(' ')[1]   #spelling_txt에 스펠링이 전부 담긴다.
    
    print(meaning_txt)
    print(spelling_txt)
    f.close()
    return word_txt, meaning_txt, spelling_txt  # 리턴 해줘야 계속 갱신된다.

word_txt, meaning_txt, spelling_txt = read_words()


# In[27]:


#class 를 이용한 프레임 전환법
    
class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.title('Helper')              # 창 제목 설정
        self.geometry("300x200+1570+30")   # 창 크기 (너비x높이+x좌표+y좌표)
        self.resizable(False, False)   # 창 크기 조절 여부        
        
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
        
#####################################################################################################################################
######################################################### 암기모드  #################################################################
#####################################################################################################################################        

class StartPage(tk.Frame):  # 암기모드
    
    def matching(self):
        with open("sorted_text.txt", "rt", encoding="UTF8") as fr:
            allWords = fr.read()
        allWords = allWords.split("₩n")
                    
        with open("newwords.txt", "w", encoding='utf-8') as fw:
            i = 0
            for word in allWords:
                i = 1 + i
                result1, result2 = self.getDaumDic(word)
                if result1 == "None" or result2 == "None" or len(word) < 2:
                    continue
                fw.write(result1 + " " + result2 + "\n")

                if i > 30:  # 30개 이상으로 매칭시키지 않음. 너무 오래걸리기 때문.
                    break
                    
        with open('newwords.txt','rt', encoding='utf-8') as f:
            randomLine = random.choice(list(f.readlines())).splitlines()[0]
            print('random string : ',randomLine)
        
        text = randomLine.split()
        return text[0], text[1:]
    
    
    def getDaumDic(self, word):   # 다음 사전 크롤링으로 한글 뜻 가져오기
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
        url = 'https://dic.daum.net/search.do?q={}'.format(word)
        res = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(res.text, "html.parser")

        # Get Word
        try:
            text1 = soup.find("span", class_="txt_emph1").getText()
        except:
            text1 = "None"

        # Get Meaning
        try:
            tag2 = soup.find("ul", class_="list_search")
            tag2 = tag2.find("span", class_="txt_search")
            text2 = ' '.join(tag2.getText().split()).replace('\n', '')
        except:
            text2 = "None"

        return text1, text2

    
    def capture(self):   # 현재 화면을 그대로 캡쳐해서 img.png 라는 파일명으로 저장한다.
        print('캡쳐를 실행한다.')
        img=ImageGrab.grab()
        saveas="{}{}".format('img','.png')
        img.save(saveas)

        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath('__file__')) + os.sep + 'property.ini')

        img = Image.open('img.png')
        print('저장이 완료됐다.')

        outText = image_to_string(img, lang='eng', config='--psm 1 -c preserve_interword_spaces=1')
        with open('img_to_text.txt', 'w', encoding='utf-8') as f:
                f.write(outText)

        with open('img_to_text.txt', 'rt', encoding='UTF8') as f:
            lines = f.readlines()

        with open('sorted_text.txt', 'w', encoding='UTF8') as f:
            for line in lines :
                t = line.strip().split(' ')
                for tt in t :
                    if(tt != '') :
                        f.write(tt + '₩n')
                        
    
    def speak(self, text_kr, text_en, mode):
        file_path = os.getcwd() + '/voicefiles/'
        if mode == 0: #단어 순환하는 일반모드
            text_en = text_en.replace('\n','')  # 이걸 안해주면 경로를 읽을때 오류난다. 왜냐면 마지막 글자가 개행문자라서.
            if os.path.isfile(file_path + text_en+'.mp3') == True:  # 이미 저장된 단어가 있으면 실행만. 
                print("이미 있다. 실행만.")
                playsound(file_path + text_en+'.mp3')
            elif os.path.isfile(file_path + text_en+'.mp3') == False:
                print("저장 실행")
                tts_en = gTTS(text=text_en, lang='en')
                tts_kr = gTTS(text=str(text_kr), lang='ko')
                tts_en.save(file_path + text_en+'.mp3')
                f = open(file_path + text_en+'.mp3', 'wb')
                tts_en.write_to_fp(f)
                tts_kr.write_to_fp(f)
                f.close()
                playsound(file_path + text_en+'.mp3')
                
        elif mode == 1: #테서렉트 이용한 스캔모드
            print('같은 파일이 있나요? : ', os.path.isfile(file_path + 'temp_sound.mp3'))
            if os.path.isfile(file_path + 'temp_sound.mp3') == True:
                os.remove(file_path + 'temp_sound.mp3')
                print('삭제했습니다')
            
            print("음성파일 저장 실행")
            file_path = os.getcwd() + '/voicefiles/'
            print('text_kr :' , text_kr)
            print('text_en :' , text_en)

            none_text = 'There are no words in memory'
            tts = gTTS(text=none_text, lang='en')
            tts_en = gTTS(text=text_en, lang='en')
            tts_kr = gTTS(text=str(text_kr), lang='ko')
            tts.save(file_path + 'temp_sound.mp3')
            print("저장했습니다")
            with open(file_path + 'temp_sound.mp3' ,'wb') as f:
                tts_en.write_to_fp(f)
                tts_kr.write_to_fp(f)
                
            playsound(file_path + 'temp_sound.mp3', True)
            os.remove(file_path + 'temp_sound.mp3')  # 이용한 뒤 삭제
            print('삭제했습니다')

    
    def show_word(self, countdown):  # timer 가 실행시키는 함수. # 단어를 띄워주는 함수는 여기서 전부 실행된다.!!
        showing_time = self.var.get()
        sound_on = self.sound_Check.get()
        scanning_on = self.scan_Check.get()
        
        if showing_time == 0:    # 0이면 아예 함수를 실행하지 않는다.
            print("show_word 함수가 더이상 반복되지 않습니다.")
            return
        
        else: 
            if countdown <= 0:  # 0일때 라벨을 바꿔준다.
                print('소리를 켰는지?' , sound_on)
                print('스캔모드 on? ' , scanning_on)
                
                if scanning_on == 1:  # 1이면 스캔모드
                    self.capture()
                    text_en, text_kr = self.matching()  # 매칭함수에서 한글과 영어뜻 받아온다.
                    text_kr = ' '.join(text_kr)
                    
                    print('text_kr 의 길이는 몇인지? : ', len(text_kr))
                    if len(text_kr) >= 0 and len(text_kr) < 8:
                        self.show_meaning.config(font = self.label_font, width = 11)
                    elif len(text_kr) >=8 and len(text_kr) < 10:
                        self.show_meaning.config(font = self.label_font_small, width = 15)
                    elif len(text_kr) >=1 and len(text_kr) < 13:
                        self.show_meaning.config(font = self.label_font_tiny, width = 19)
                    elif len(text_kr) >=13:                    
                        text_kr = text_kr[:12] + '\n' + text_kr[12:]
                        self.show_meaning.config(font = self.label_font_tiny, width = 19)
                        
                    self.show_meaning.config(text = text_kr)  # 크롤링 한 뜻과 스캔한 영단어를 출력
                    self.show_spelling.config(text = text_en)     
                        
                    if sound_on == 1:  # 소리 버튼이 켜져있으면 읽는 함수도 같이 실행 
                        self.speak(text_kr, text_en, scanning_on)    
                    countdown = showing_time  # 이걸 써줘야 타이머가 순환한다.
                
                elif scanning_on == 0:  # 0이면 저장된 단어를 출력하는 순환모드.
                    self.show_meaning.config(font = self.label_font, width = 11) # 스캔모드에서 설정된 폰트값을 기본값으로 설정
                
                    self.list_index = random.randint(0, len(word_txt) - 1)  # 0 부터 word_txt의 줄 수 만큼 랜덤한 수 저장                
                    self.show_meaning.config(text = meaning_txt[self.list_index])  # 랜덤하게 라벨 바꿔준다.
                    self.show_spelling.config(text = spelling_txt[self.list_index]) 
                
                    if sound_on == 1:  # 소리 버튼이 켜져있으면 읽는 함수도 같이 실행
                        self.speak(meaning_txt[self.list_index], spelling_txt[self.list_index], scanning_on)
                
                    countdown = showing_time  # 이걸 써줘야 타이머가 순환한다.
            
            value="다음 단어까지 : "+ str(countdown) + "초"
            self.interval_sec.config(text=value)            
            print("기다려야 하는 시간 : {}".format(countdown))
            
            countdown -= 1 # 1초마다 카운트다운 세는거.
            self.working = self.after(1000, lambda:self.show_word(countdown)) # 1초마다 계속 이 함수를 실행.

    
    def select(self, *args):  # 몇 초 간격으로 단어가 바뀔건지 정하는 스케일바가 실행하는 함수
        showing_time = self.var.get() 
        
        if showing_time == 0:
            self.interval_sec.config(text = "-------- 정지 --------")
            print("스케일 0 찍음. 정지")
            
            self.show_meaning.config(state = 'disabled')
            self.show_spelling.config(state = 'disabled')
            
        # 최초로 1회 실시하는 이유는 else 에 cancel 을 먼저 만나야 하기 때문에.    
        elif self.first_switch == False:
            
            self.show_meaning.config(state = 'active')
            self.show_spelling.config(state = 'active')
            
            self.working = self.after(1000, lambda:self.show_word(showing_time))  # 최초로 1회 실시. 
            self.first_switch = True  # 다신 이 elif 분기로 들어오지 않음. 그래서 최초1회만 실시하게됨.
            print("최초1회실시 switch 는 지금" , self.first_switch)
            
        else:
            print("스케일 조정됨")
        
            value="다음 단어까지 : "+ str(showing_time) + "초"   # 얘내가 필요한이유는 스케일 조절하는 '즉시' 바뀌기위해.
            self.interval_sec.config(text=value)
            
            self.show_meaning.config(state = 'active')
            self.show_spelling.config(state = 'active')
            
            if self.working is not None:  # 재귀함수가 실행중이라면, 스케일을 조작했을때 즉시 캔슬한다.
                self.after_cancel(self.working)
                self.working = None
                print("즉시 캔슬 실행")
                
            self.working = self.after(1000, lambda:self.show_word(showing_time))
            
    
    def __init__(self, master):
        global word_txt, meaning_txt, spelling_txt
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self, width = 300, height = 200)
        
        self.first_switch = False # 처음엔 False 인데 스케일 건드리면 True
        
        self.var=tk.IntVar()  # 클래스 변수 선언으로 select 함수에서도 사용 가능. 
        self.sound_Check = tk.IntVar()
        self.scan_Check = tk.IntVar()

        self.label_font = ('Helvetica', 20, 'bold')       
        self.label_font_small = ('Helvetica', 16, 'bold')
        self.label_font_tiny = ('Helvetica', 12, 'bold')
        self.list_index = random.randint(0, len(word_txt) - 1)  # 0 부터 word_txt의 줄 수 만큼 랜덤한 수 저장
                 
        self.pg1 = tk.Button(self, text="입력 모드", command=lambda: master.switch_frame(PageOne)) # 입력모드로 가는 버튼
        self.pg1.place(x=237, y=174) # 버튼 위치 배정
        self.pg2 = tk.Button(self, text="시험 모드", command=lambda: master.switch_frame(PageTwo)) # 시험모드로 가는 버튼
        self.pg2.place(x=1, y=174)
        
        self.show_meaning = tk.Label(self, text = meaning_txt[self.list_index], 
                                     justify = 'center', width = 11, font = self.label_font, state = 'disabled')
        self.show_meaning.place(x=50, y=30)  # 암기모드에서 뜻 라벨

        self.show_spelling = tk.Label(self, text = spelling_txt[self.list_index], 
                                      width = 11, font = self.label_font, state = 'disabled')
        self.show_spelling.place(x=50, y=105)  # 암기모드에서 스펠링 라벨     
        
        self.interval_sec = tk.Label(self, text="스케일 조정하여 표시")
        self.interval_sec.place(x = 95, y = 174)        

        # scale 값의 텀 만큼 self.show_word 함수를 실행해라.
        self.sec_scale=tk.Scale(self, variable=self.var, command=self.select, orient="vertical", showvalue=False, 
            tickinterval=10, from_=0, to=60, length=160, sliderlength=20, resolution=5)  # 출력 반복 간격 설정 스케일
        self.sec_scale.place(x = 250 , y = 3)
        
        self.scan_ckbtn=tk.Checkbutton(self, text='스캔', variable=self.scan_Check)
        self.scan_ckbtn.place(x=2, y=2)
        
        self.sound_ckbtn=tk.Checkbutton(self, text='소리', variable=self.sound_Check)
        self.sound_ckbtn.place(x=2, y=22)
        
#####################################################################################################################################
######################################################### 입력모드  #################################################################
#####################################################################################################################################

class PageOne(tk.Frame):  # 입력모드     
    
    def save_mean(self, enter_value):   # 뜻을 입력받고 meaning 에 저장  # 입력모드 Entry 이다.
        self.meaning = tk.Entry.get(self.word_mean_enter)
        self.check_mean.config(text='입력한 뜻 : ' + self.meaning)
        print(self.meaning)
        self.save_word.config(text = '저장')
    
    def save_spelling(self, enter_value):   # 스펠링을 입력받고 meaning 에 저장  # 입력보드 Entry
        self.spelling = tk.Entry.get(self.word_spelling_enter)
        self.check_spelling.config(text='입력한 스펠링 : ' + self.spelling)
        print(self.spelling)
        self.save_word.config(text = '저장')
        
    def save_to_txt(self, meaning, spelling, event=_):  # 마우스로 저장할 경우 event는 필요하지 않으니 _ 값 처리.
        global word_txt, meaning_txt, spelling_txt  # 전역 스페이스에 있는 변수 사용하겠다고 알려주는거.
        
        if meaning == '' or spelling == '':  # 아무것도 입력하지 않고 저장했을 때
            self.save_word.config(text = '뜻과 스펠링을 전부 입력해주세요.')
            
        elif meaning_txt.count(meaning) != 0 and spelling_txt.count(spelling+'\n') != 0: # 이미 있는 단어를 저장하려 했을 때
            self.save_word.config(text = '이미 있는 단어&뜻 입니다.')
            
        else:   # 아무 이상 없이 저장
            file_path = os.getcwd()
            f = open(file_path + "/Words.txt", 'a')
            f.write(meaning + ' ' + spelling + '\n')
            f.close()
            
            self.save_word.config(text = '저장 완료')
            self.word_mean_enter.delete(0, 99)  # Entry 내에 0부터 99자 내에 있는건 다 지워버린단 뜻.
            self.word_spelling_enter.delete(0, 99)
            self.check_mean.config(text = "입력한 뜻 : ")
            self.check_spelling.config(text = "입력한 스펠링 : ")
            word_txt, meaning_txt, spelling_txt = read_words()  # 세 전역변수를 갱신시킨다.
            self.meaning, self.spelling = '', ''  # 저장 버튼을 계속 눌러서 똑같은 변수가 계속 저장되는걸 방지
            
    
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self, width = 300, height = 200)
        
        self.meaning, self.spelling = '', '' # 변수 초기화 준다. 그래야 예전에 입력한 단어가 바로 저장되는걸 방지
        # Pageone 클래스에서 사용할 변수로 meaning 과 spelling 앞에 self.를 붙였다. 
        # 그거로만 사용하니까 클래스 내 함수마다 통용되더라. << 클래스변수라서
        
        tk.Button(self, text='←', command=lambda: master.switch_frame(StartPage)).place(x=0, y=0) # 뒤로가는 버튼
        
        self.enter_new_word = tk.Label(self, text = "단어의 뜻과 스펠링을 입력하세요.") # 라벨 생성
        self.enter_new_word.place(x=60, y=10)

        self.word_mean = tk.Label(self, text = "한글뜻 : ", anchor = 'e') # 라벨 생성
        self.word_mean.place(x=30, y=45, width=65)

        self.check_mean = tk.Label(self, text = "입력한 뜻 : ") # 라벨 생성
        self.check_mean.place(x=90, y=70)

        self.word_spelling = tk.Label(self, text = "스펠링 : ",  anchor = 'e') # 라벨 생성
        self.word_spelling.place(x=30, y=95, width=65)

        self.check_spelling = tk.Label(self, text = "입력한 스펠링 : ") # 라벨 생성
        self.check_spelling.place(x=90, y=120)
        
        self.word_mean_enter = tk.Entry(self)  # Entry 생성
        self.word_mean_enter.bind("<Return>", self.save_mean)
        self.word_mean_enter.place(x=100, y=45) 

        self.word_spelling_enter = tk.Entry(self)   # Entry 생성
        self.word_spelling_enter.bind("<Return>", self.save_spelling)
        self.word_spelling_enter.place(x=100, y=95) 
        
        # event 인자를 함수는 갖는데 얘는 그걸 발생시키지 않아서 키워드 인자를 사용했다.
        self.save_word = tk.Button(self, text = '저장', anchor = 'center', takefocus = True
                                  ,command = lambda:self.save_to_txt(meaning=self.meaning, spelling=self.spelling))
        self.save_word.place(x=50, y=150, width=200)
        # lambda 이용해서 엔터 치는거로도 버튼이 작동해서 단어 저장하는 함수로 인자 보낼 수 있게 하기. event 인자를 보내는게 핵심
        self.save_word.bind("<Return>", lambda event:self.save_to_txt(event=event,meaning=self.meaning, spelling=self.spelling))
        
#####################################################################################################################################
######################################################### 시험모드  #################################################################
#####################################################################################################################################

class PageTwo(tk.Frame):  # 시험모드
    
    def test_start(self):   # Start 버튼 누르면 실행되는 함수
        global w_note
        
        print('테스트를 시작하지')
        w_note.clear()  # start 누르면 이전에 저장된오답노트용 인덱스는 전부 초기화
        self.start_button.config(state='disabled')
        self.radio1.config(state='disabled')
        self.radio2.config(state='disabled')
        self.radio3.config(state='disabled')
        self.radio4.config(state='disabled')
        self.radio5.config(state='disabled')
        self.put_answer.config(state='normal', bg='white')
        self.checkbutton1.config(state='normal')
        self.correct_or_wrong.config(text = '')
        self.wrong_note.config(state='disabled')
        print('word_txt의 길이 :', len(word_txt))
        
        test_number = self.RadioVariety_1.get()  # 시험 볼 단어 갯수 선택한 값 
        
        if test_number > len(word_txt) - 1:  # 시험볼 단어 갯수가 저장된 단어보다 많을 때 오류 배제
            print("시험볼게 너무많아요. 이만큼으로 줄임: ", len(word_txt))
            test_number = len(word_txt)

        c_n, w_n = 0, 0      # correct_nubmer, wrong_number, correct_percentage, wrong_percentage
        c_p, w_p = 0.0, 0.0  # 함수에 들어가기 전에 변수 선언해주자.
        meaning_or_spelling = random.randint(0, 1)  # 0 이 나오면 한글이, 1 이 나오면 스펠링이 문제로 나온다.
        
        if test_number == 1:  # 틀리면 곧바로 시험 끝 모드
            print("데스매치 시작")
            death_end = 50
            if len(word_txt) < death_end:
                death_end = len(word_txt)
                print("단어수가 50개보다 적네. death_end : ", death_end)
            death_order = random.sample(range(0, len(word_txt)), death_end)  # 50개씩 반복해서 랜덤으로 뽑아준다.
            # 이걸 왜 하느냐? 최소 50개씩 단위로는 중복되는 단어가 안나오게 할 수 있다.
            
            print('len(death_order) : ' ,len(death_order))
            print(death_order)
            print('death_order[0] :' ,death_order[0])  # 이게 처음
            print('death_order[-1] :' ,death_order[-1])  # 이게 마지막
            
            self.death_match(test_number, death_order, meaning_or_spelling, c_n, w_n, c_p, w_p, death_end)
        
        else:  # test_number 만큼 시험봐서 정답률, 오답률 체크해준다.
                        
            # order 리스트에 무작위로 test_number 만큼 겹치지 않는 숫자를 넣는다
            order = random.sample(range(0, len(word_txt)), test_number) 
            
            print('len(order) : ' ,len(order))
            print(order)
            print('order[0] :' ,order[0])  # 이게 처음
            print('order[test_number - 1] :' ,order[test_number - 1])  # 이게 마지막
            print(str(test_number) + "번 시험보자")
            
            self.testing(test_number, order, meaning_or_spelling, c_n, w_n, c_p, w_p)  # testing 함수로 진입한다
        
    def death_match(self, test_number, death_order, meaning_or_spelling, c_n, w_n, c_p, w_p, death_end, event=_):
        global hint_kr, hint_en, kr_or_en, w_note
        
        self.top_label.config(text = str(test_number)+"번 문제")
        self.answer = tk.Entry.get(self.put_answer)
        print("뭐라고 입력했나요? : ", self.answer)
        
        i = test_number - 1  # i 는 0부터 시작한다. 왜냐면 리스트의 인덱스 번호가 0부터 시작해야해서.  
        i = i % death_end  # test_number는 계속 증가하지만, i는 0~49 의 숫자를 유지해야하기때문에 나머지연산자 사용
        tem_i = i  # 답 체크할때 쓸 변수다.
        
        if test_number == 1:  # 첫번째 문제에선 필요없다.
            pass
        
        elif meaning_or_spelling == 0: # 스펠링이 맞았는지 확인하기
            if self.answer+'\n' == (spelling_txt[death_order[tem_i-1]].replace(' ', '')):
                self.correct_or_wrong.config(text = '정답입니다.')
                self.put_answer.config(bg='palegreen')
                c_n += 1                             # 맞았으니 correct_number +1
            else:
                self.correct_or_wrong.config(text = '답: ' + spelling_txt[death_order[tem_i-1]])     
                self.put_answer.config(bg='pink')
                w_n += 1                             # 틀렸으니 wrong_number +1
                w_note.append(death_order[tem_i-1])  # 오답노트용 전역변수 리스트에 현재 인덱스 저장

        
        elif meaning_or_spelling == 1:   # 뜻이 맞았는지 확인하기
            if self.answer == meaning_txt[death_order[tem_i-1]].replace(' ', ''):
                self.correct_or_wrong.config(text = '정답입니다.')
                self.put_answer.config(bg='palegreen')
                c_n += 1
            else:
                self.correct_or_wrong.config(text = '답: ' + meaning_txt[death_order[tem_i-1]]) 
                self.put_answer.config(bg='pink')
                w_n += 1
                w_note.append(death_order[tem_i-1])
                
        if i == 0 and test_number != 1:     # i 가 주어진 문제를 다풀어서 한 번 더 뒤섞고 i를 0으로 초기화시키는 과정 과정.
            # 가장 처음엔 test_number != 1 가 False 라서 통과하지 않는다. 이후 돌때마다 들어감.
            # 위에있는 정답체크 분기보다 아래에두어야 재귀함수를 돌때 오류나지 않음.
            tem_i = len(death_order)
            death_order = random.sample(range(0, len(word_txt)), death_end)
            print(death_order)
            
        if test_number == 1:  # 첫번째 문제에선 분모가 0인것을 방지
            total_n = 1
        else:
            total_n = c_n + w_n
            
        c_p = (c_n / (total_n)) * 100
        w_p = (w_n / (total_n)) * 100
        
        self.correct_number.config(text='맞춘 갯수: ' + str(c_n) + '개')        
        self.wrong_number.config(text='틀린 갯수: ' + str(w_n) + '개')
        self.correct_percentage.config(text='정답률: {:.1f}'.format(c_p) + '%')
        self.wrong_percentage.config(text='오답률: {:.1f}'.format(w_p) + '%')
            
        meaning_or_spelling = random.randint(0, 1)  # 0 이 나오면 한글이, 1 이 나오면 스펠링이    
        kr_or_en = meaning_or_spelling  # hint 함수에서 쓰기위해 전역변수로 전달
        test_number += 1  # 한바퀴 돌았을때 1 증가시켜준다.
            
        if w_n >= 1:   # 틀린 갯수가 1개 이상일 때 시험 종료
            print("시험 끝")
            self.radio1.config(state='normal')
            self.radio2.config(state='normal')
            self.radio3.config(state='normal')
            self.radio4.config(state='normal')
            self.radio5.config(state='normal')
            self.put_answer.config(state='disabled')
            self.checkbutton1.config(state='disabled')
            self.checkbutton1.deselect()
            self.show_hint.place(x=248, y=130)
            self.show_hint.config(text='hint↑', state='disabled')
            self.show_question.config(text = str(c_n) + '개 맞추셨습니다.')
            self.top_label.config(text = '시험이 끝났습니다.')
            self.wrong_note.config(state='active')
            self.put_answer.delete(0, 99)
            return        

        if meaning_or_spelling == 0:  # 한글 문제 제출
            print('death_order[i] : ',death_order[i])
            print('meaning_txt[death_order[i]] : ',meaning_txt[death_order[i]])
            print('spelling_txt[death_order[i]] : ',spelling_txt[death_order[i]])
            self.show_question.config(text = meaning_txt[death_order[i]]) 
            
            hint_kr = meaning_txt[death_order[i]]   # hint 함수에 변수 전달하기 위해 전역변수로 전달
            hint_en = spelling_txt[death_order[i]]
             
            self.put_answer.bind('<Return>',
                                 lambda event:[self.death_match(test_number, death_order, meaning_or_spelling,
                                                                c_n, w_n, c_p, w_p, death_end, event=event),
                                               self.hint(event=event)]) # lambda 함수 인자로 리스트를 쓰면 동시에 두 함수 실행 가능!!
            self.put_answer.delete(0, 99)  # Entry 칸을 싹 비워준다.
                    
        else:  # 영어 문제 제출
            print('death_order[i] : ',death_order[i])
            print('spelling_txt[death_order[i]] : ',spelling_txt[death_order[i]])
            print('meaning_txt[death_order[i]] : ',meaning_txt[death_order[i]])
            self.show_question.config(text = spelling_txt[death_order[i]]) 
            
            hint_kr = meaning_txt[death_order[i]]
            hint_en = spelling_txt[death_order[i]]
            
            self.put_answer.bind('<Return>',
                                 lambda event:[self.death_match(test_number, death_order, meaning_or_spelling,
                                                                c_n, w_n, c_p, w_p, death_end, event=event),
                                               self.hint(event=event)])
            self.put_answer.delete(0, 99)  # Entry 칸을 싹 비워준다.
            
                    
    def testing(self, test_number, order, meaning_or_spelling, c_n, w_n, c_p, w_p, event=_):  # test_start에서 이 함수로 넘어온다.
        global hint_kr, hint_en, kr_or_en, w_note
        
        test_number -= 1  # Entry에 엔터를 칠 때마다 다시 함수로 들어오면서 1씩 감소하다가 -1가 되면 퇴장한다.
        # 시작부터 -1 해주는 이유는 리스트에 -1 안해주고 넣으면 out of range 뜬다.

        self.top_label.config(text = str(test_number+1)+"번 남았습니다.")
        self.answer = tk.Entry.get(self.put_answer)
        print("뭐라고 입력했나요? : ", self.answer)
        
        i = test_number  # 계속 인덱스 번호로 쓰일건데 짧은 변수명이 좋아서 받아넣음.
        tem_i = i - 1  # 답 체크할때 쓸 변수다.
        
        if i == len(order) - 1:  # 첫번째 문제에선 필요없다.
            pass
        
        elif meaning_or_spelling == 0: # 스펠링이 맞았는지 확인하기
            if self.answer+'\n' == spelling_txt[order[tem_i+2]].replace(' ', ''):
                self.correct_or_wrong.config(text = '정답입니다.')
                self.put_answer.config(bg='palegreen')
                c_n += 1
            else:
                self.correct_or_wrong.config(text = '답: ' + spelling_txt[order[tem_i+2]])     
                self.put_answer.config(bg='pink')
                w_n += 1
                w_note.append(order[tem_i+2])
        
        elif meaning_or_spelling == 1:   # 뜻이 맞았는지 확인하기
            if self.answer == meaning_txt[order[tem_i+2]].replace(' ', ''):
                self.correct_or_wrong.config(text = '정답입니다.')
                self.put_answer.config(bg='palegreen')
                c_n += 1
            else:
                self.correct_or_wrong.config(text = '답: ' + meaning_txt[order[tem_i+2]]) 
                self.put_answer.config(bg='pink')
                w_n += 1
                w_note.append(order[tem_i+2])
        
        print('c_n는 몇이냐: ', c_n)
        print('w_n는 몇이냐: ', w_n)
        
        if i == len(order) - 1:  # 첫번째 문제에선 분모가 0인것을 방지
            total_n = 1
        else:
            total_n = c_n + w_n
            
        c_p = (c_n / (total_n)) * 100
        w_p = (w_n / (total_n)) * 100
        
        self.correct_number.config(text='맞춘 갯수: ' + str(c_n) + '개')        
        self.wrong_number.config(text='틀린 갯수: ' + str(w_n) + '개')
        self.correct_percentage.config(text='정답률: {:.1f}'.format(c_p) + '%')
        self.wrong_percentage.config(text='오답률: {:.1f}'.format(w_p) + '%')
        
        # 0,1 판별을 함수 내에서 다시 써줘야 엔터 쳤을 때 지난 문제가 0이었는지 1이었는지 알 수 있음.
        meaning_or_spelling = random.randint(0, 1)  # 0 이 나오면 한글이, 1 이 나오면 스펠링이    
        kr_or_en = meaning_or_spelling  # hint 함수에서 쓰기위해 전역변수로 전달
        
        if test_number <= -1:  # test_number 가 1씩 줄어들다가 0 아래로 가면 시험 끝
            print("시험 끝")
            self.radio1.config(state='normal')
            self.radio2.config(state='normal')
            self.radio3.config(state='normal')
            self.radio4.config(state='normal')
            self.radio5.config(state='normal')
            self.put_answer.config(state='disabled')
            self.checkbutton1.config(state='disabled')
            self.checkbutton1.deselect()
            self.show_hint.place(x=248, y=130)
            self.show_hint.config(text='hint↑', state='disabled')
            self.show_question.config(text = str(c_n) + '개 맞추셨습니다.')
            self.top_label.config(text = '시험이 끝났습니다.')
            self.wrong_note.config(state='active')
            self.put_answer.delete(0, 99)
            return        
        
        if meaning_or_spelling == 0:  # 한글 문제 제출
            print('order[i] : ',order[i])
            print('meaning_txt[order[i]] : ',meaning_txt[order[i]])
            print('spelling_txt[order[i]] : ',spelling_txt[order[i]])
            self.show_question.config(text = meaning_txt[order[i]]) 
            
            hint_kr = meaning_txt[order[i]]  # hint 함수에서 쓸 전역변수 보내기
            hint_en = spelling_txt[order[i]] 
            
            self.put_answer.bind('<Return>',
                                 lambda event:[self.testing(test_number, order,
                                                            meaning_or_spelling, c_n, w_n, c_p, w_p, event=event),
                                               self.hint(event=event)]) # lambda 함수 인자로 리스트를 쓰면 동시에 두 함수 실행 가능!!
            self.put_answer.delete(0, 99)  # Entry 칸을 싹 비워준다.
                    
        else:  # 영어 문제 제출
            print('order[i] : ',order[i])
            print('spelling_txt[order[i]] : ',spelling_txt[order[i]])
            print('meaning_txt[order[i]] : ',meaning_txt[order[i]])
            self.show_question.config(text = spelling_txt[order[i]]) 
            
            hint_kr = meaning_txt[order[i]]   # hint 함수에서 쓸 전역변수 보내기
            hint_en = spelling_txt[order[i]]
            
            self.put_answer.bind('<Return>',
                                 lambda event:[self.testing(test_number, order,
                                                            meaning_or_spelling, c_n, w_n, c_p, w_p, event=event),
                                               self.hint(event=event)])
            self.put_answer.delete(0, 99)  # Entry 칸을 싹 비워준다.

    
    def check(self):  # 몇 개를 시험볼 지 고르는 RadioButton을 누르면 실행하는 함수
        test_number = self.RadioVariety_1.get()
        if test_number == 1:
            self.top_label.config(text='틀릴 때 까지 시험을 봅니다.')
            self.start_button.config(state='active', activebackground = 'pale green', activeforeground = 'red')
        else:
            self.top_label.config(text=str(test_number) + '개를 선택했습니다.')
            self.start_button.config(state='active', activebackground = 'pale green', activeforeground = 'black')
            
            
    def english_hint(self, spelling):  # hint 함수에서 호출하는 영어힌트 주는 함수
        hint = []
        for w in list(spelling):
            hint.append(w)
    
        for i in range(1, len(spelling) - 2): # 첫번째, 끝 알파뱃만 냅두고 _ 로 바꿔서 반환.
            hint[i] = '_'
        return hint   
    
    
    def korean_hint(self, meaning):   # hint 함수에서 호출하는 한글힌트 주는 함수
        CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        r_list = []
        for w in list(meaning.strip()):
            if '가' <= w <= '힣':  # 유니코드상 '가' 부터 '힣' 이 한글모음 전체임.
                ch1 = (ord(w) - ord('가')) // 588    # 588번째마다 초성이 바뀐다.
                r_list.append(CHOSUNG_LIST[ch1])  
            else:
                r_list.append(w)  # 굳이 한글이 아닐 경우 append 할 필요는 없지만 그래도 넣었음.
        return r_list

            
    def hint(self, event=_):  # checkbutton 을 누르면 힌트를 출력시켜줌.
        global hint_kr, hint_en, kr_or_en
        flag = self.CheckVariety_1.get()        
        print("체크버튼누름", flag)        
        
        if flag == 1:   # 체크버튼이 눌려졌을때. 
            self.correct_or_wrong.place(x=20, y=130)
            self.correct_or_wrong.config(justify = 'left', width = 0)
            self.show_hint.place(x=130, y=130)
            self.show_hint.config(state='normal')
            
            if kr_or_en == 0: # 0.한글문제라면 영어힌트를 주고, 1.영어문제라면 한글힌트를 준다.
                hint_1 = self.english_hint(hint_en)
                del hint_1[-1]  # 가장 마지막 원소는 '\n' 이기때문에 없애준다.
                self.show_hint.config(text = '힌트: ' + ' '.join(hint_1))  
                # 배열이었던 hint_1 를 사이사이에 공백 하나 넣은 문자열로 출력한다.
                
            elif kr_or_en == 1: # 한글힌트를 준다.
                hint_2 = self.korean_hint(hint_kr)
                self.show_hint.config(text = '힌트: ' + ''.join(hint_2))
            
        elif flag == 0:  # 체크버튼을 해제했을때
            self.correct_or_wrong.place(x=100, y=130)
            self.correct_or_wrong.config(justify = 'center', width = 15)
            self.show_hint.place(x=248, y=130)
            self.show_hint.config(text='hint↑', state='disabled')
            
            
    def disable_button(self):
        self.wrong_note.config(state = 'disabled')  # 오답노트 버튼을 한 번 누르고 나면 더 누르지 못하게 한다.
        
        
    def __init__(self, master):
        global word_txt, meaning_txt, spelling_txt  # 전역변수에 있는 단어들 사용하자
        
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self, width = 300, height = 200)
        tk.Button(self, text="←", command=lambda: master.switch_frame(StartPage)).place(x=0, y=0) # 뒤로가기 버튼
    
        self.start_button = tk.Button(self, text="Start", state='disabled', command=self.test_start) # 시험을 시작하는 버튼
        self.start_button.place(x=265, y=0) 
    
        self.RadioVariety_1=tk.IntVar() # 이걸 써줘야 RadioButton 에서 누른 값을 받아들일 수 있다.
        self.CheckVariety_1=tk.IntVar() # 이걸 써줘야 CheckButton 에서 값을 받아들일 수 있다.
            
        self.show_question = tk.Label(self, text = '', justify = 'center', font = "Helvetica 16 bold", width = 15)
        self.show_question.place(x=50, y=60)
         
        self.put_answer = tk.Entry(self, font = "Helvetica 16 bold", justify = 'center', width = 17, state='disabled')  # Entry 생성
        self.put_answer.place(x=48, y=95) 
        
        self.radio1=tk.Radiobutton(self, text="10개", value=10, variable=self.RadioVariety_1, command=self.check)
        self.radio1.place(x=15, y=30)

        self.radio2=tk.Radiobutton(self, text="20개", value=20, variable=self.RadioVariety_1, command=self.check)
        self.radio2.place(x=70, y=30)

        self.radio3=tk.Radiobutton(self, text="50개", value=50, variable=self.RadioVariety_1, command=self.check)
        self.radio3.place(x=125, y=30)
        
        self.radio4=tk.Radiobutton(self, text="100개", value=100, variable=self.RadioVariety_1, command=self.check)
        self.radio4.place(x=180, y=30)
        
        self.radio5=tk.Radiobutton(self, text="∞", value=1, variable=self.RadioVariety_1, command=self.check)
        self.radio5.place(x=245, y=30)        
        
        self.top_label=tk.Label(self, text="몇 개를 시험보고 싶으신가요?", justify = 'center')
        self.top_label.place(x=28, y=7, width=237)
        
        self.correct_or_wrong = tk.Label(self, text = '', justify = 'center', width = 15)
        self.correct_or_wrong.place(x=100, y=130)
        
        self.correct_number = tk.Label(self, text = '맞춘 갯수:', justify = 'center')
        self.correct_number.place(x=20, y=155)
        
        self.wrong_number = tk.Label(self, text = '틀린 갯수:', justify = 'center')
        self.wrong_number.place(x=20, y=175)
        
        self.correct_percentage = tk.Label(self, text = '정답률:', justify = 'center')
        self.correct_percentage.place(x=130, y=155)
        
        self.wrong_percentage = tk.Label(self, text = '오답률:', justify = 'center')
        self.wrong_percentage.place(x=130, y=175)
        
        self.show_hint = tk.Label(self, text = 'hint↑', justify = 'left', state='disabled', fg = 'orange')
        self.show_hint.place(x=248, y=130)
        
        self.checkbutton1=tk.Checkbutton(self, variable=self.CheckVariety_1, fg = 'orange',
                                         state = 'disabled', command = self.hint)
        self.checkbutton1.place(x=265, y=95)
        
        self.wrong_note = tk.Button(self, text="틀린단어\n확인", 
                                    command=lambda:[create_window(), 
                                                    self.disable_button()], state='disabled') # 시험을 시작하는 버튼
        self.wrong_note.place(x=235, y=155) 
        
def create_window():
    global meaning_txt, spelling_txt, w_note
    window = tk.Toplevel()
    window.title("note")
    window.geometry("+1570+265")   # 창 크기 (너비x높이+x좌표+y좌표)
    window.resizable(False, False)
    
    for i in range(0, len(w_note)):  # 틀린 갯수만큼 라벨을 pack 해서 쌓는다.
        print(w_note[i])
        print(meaning_txt[w_note[i]], spelling_txt[w_note[i]].replace('\n',''))
        note=tk.Label(window, text= spelling_txt[w_note[i]].replace('\n','') + ' ' + meaning_txt[w_note[i]])
        note.pack()
        
if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()


# In[ ]:




