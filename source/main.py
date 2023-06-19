import pandas as pd
import openai
import googletrans
from urllib import request
from PIL import Image
from io import BytesIO
import os

from datetime import datetime

prompt1 = '''Q. 아래 뜻을 가진 단어를 가지고 장면을 설명하는 글을 한문장으로 작성해줘.
** 단어 **
[word]
** 뜻 **
[meaning]
A.
'''

if __name__ == "__main__":
    mypath = os.getcwd() + '\\'

    print("ImgAI Prompt maker")
    print("INSTAGRAM: ai.tame.tips")

    print(mypath+'api_key.txt')
    if os.path.isfile(mypath+'api_key.txt'):
        with open(mypath+'api_key.txt', 'rt') as f:
            openai.api_key = f.readline()
    else:
        f = open(mypath+"api_key.txt", 'w')
        f.close()
        input("api_key.txt 파일에 OpenAI API키를 작성해서 저장해주세요.")
        exit()

    file_name = input("단어장 파일명을 입력하세요(ex: 1171710_12.xls): ")
    
    try:
        print(mypath+file_name)
        df = pd.read_excel(mypath+file_name)
    except:
        input("옳은 파일명인지 확인후 다시 실행해주세요.")
        exit()

    res_string = []
    dt_now = datetime.now()
    today = dt_now.strftime("%Y-%m-%d_%H%M%S")

    for i in range(len(df)):
        # 프롬프트 제작
        first_prompt = prompt1.replace('[word]',df['어휘'].iloc[i]).replace('[meaning]',df['뜻풀이'].iloc[i])

        # GPT 결과 받아오기
        try:
            result = openai.ChatCompletion.create(
                model= "gpt-3.5-turbo",
                messages= [
                    {"role":"user", "content":first_prompt}
                ]
            )
        except:
            input("Chat GPT 프롬프트 생성에 실패했습니다.\n옳은 API 키인지 확인해주세요.")
            exit()
            

        second_prompt = result.choices[0]['message']['content']

        # DALLE 결과 받아오기
        # translate prompt
        try:
            translator = googletrans.Translator()
            eng_res = translator.translate(second_prompt, "en").text
        except:
            input("구글 번역중 문제가 생겼습니다.\n개발자에게 문의하세요.\nmolllab@kakao.com")
            exit()

        # generate image
        # check box data need...
        try:
            response = openai.Image.create(
                prompt=eng_res,
                n=1,
                size="512x512",
            )
        except:
            input("DALL-E2가 이미지 생성에 실패했습니다.\n옳은 API 키인지 확인해주세요.")
            exit()

        image_url = response["data"][0]["url"]

        res = request.urlopen(image_url).read()
        img = Image.open(BytesIO(res))
        title = df["어휘"].iloc[i].replace("\n", "")
        img.save(mypath+f'{i}_{title}.png')

        res_string.append(title+":"+second_prompt)

        with open(mypath+f'prompt_{today}.txt', 'w') as f:
            f.write('\n'.join(res_string))
