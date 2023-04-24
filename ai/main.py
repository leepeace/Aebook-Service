from fastapi import FastAPI,File,UploadFile
from fastapi.responses import JSONResponse
from review_star_prediction import *
from isbn_ocr import *
from dotenv import load_dotenv
import os
import openai
import io
import base64
import cv2
import sys
import requests
import numpy as np

app = FastAPI()

#constant
STT_URL = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"

#api key
load_dotenv()
openai.api_key = os.getenv("SECRET_KEY")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

@app.get("/")
async def root():
    return {"message":"Hello World"}

#test
#e.g.:http://127.0.0.1:8000/hello/daehyuck
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message":f"Hello {name}"}


"""
input:mp3 file(keyword)
output:text
"""
@app.post("/reviews/sound")
async def sound_to_text(sound: UploadFile = File(...)):
    
    #read mp3 file to byte string
    data = await sound.read()
    
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    
    response = requests.post(STT_URL,  data=data, headers=headers)
    rescode = response.status_code
    
    if(rescode == 200):
        return response.text
    else:
        return "Error : " + response.text


@app.post("/reviews/gpt")
async def create_review(title:str, words: str, writer=None, char=None):
    
    # message 구성
    if writer != None and char != None:
        
        #default number of character value
        char = max(100,char)
            
        m = f"제목:{title}, 키워드:{words}, 작가:{writer}, 서평 {char}자 이내"
    
    elif writer == None:
        
        #default number of character value
        if char == None:
            char = 100
        else:
            char = max(100,char)
        
        m = f"제목:{title}, 키워드:{words}, 서평 {char}자 이내"
    
    elif char == None:
        
        m = f"제목:{title}, 키워드:{words}, 작가:{writer}, 서평 80자 이내"
    
    #chatgpt request
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": m}
    ]
    )
    
    #chatgpt response
    return completion.choices[0].message

#prediction review star point
"""
input: chatgpt review
output: string of star point(one of 1,2,3,4,5)
"""
@app.post("/reviews/point")
async def predict_star_point(review: str):

    #simple preprocessing review
    review = review.strip("\n").strip(" ")

    #transform review
    transform_review = tokenizer.batch_encode_plus([review],max_length=128,pad_to_max_length=True)

    #prepare input data
    token_ids = torch.tensor(transform_review['input_ids']).long()
    attention_mask = torch.tensor(transform_review['attention_mask']).long()

    #prediction
    output = star_model(token_ids, attention_mask)

    #for confidence
    #percentage_output = F.softmax(output, dim = 1)

    #get maximum confidence class 
    pred = output.cpu().detach().numpy()
    sorted_pred = np.argsort(pred,axis = 1)
    return str(sorted_pred[0][-1]+1)

#convert image to sketch
@app.post("/paintings/sketch")
async def image_to_sketch(image: UploadFile = File(...)):
    
    #read image data
    img = await image.read()
    
    #convert image to byte string
    img = np.fromstring(img,dtype=np.uint8)
    
    #read image
    img = cv2.imdecode(img,cv2.IMREAD_COLOR)
    
    #convert the color image to grayscale
    gray_image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    #apply inverted filter
    inverted_image = 255 - gray_image
    
    #apply gaussian blur
    blur = cv2.GaussianBlur(inverted_image,(21,21),0)
    
    #convert blur image to inverted blur
    inv_blur = 255 - blur
    
    #convert it to sketch image
    #sketch can be obtained by performing bit-wise division
    #between grayscale image and inverted-blur image
    sketch = cv2.divide(gray_image, inv_blur, scale = 256.0)
    
    #convert sketch image to binary string
    binary_sketch = cv2.imencode('.jpg',sketch)[1].tobytes()
    
    # encoding byte string to base64
    encoded = base64.b64encode(binary_sketch)
    
    # decoding base64 to ascii
    decoded = encoded.decode('ascii')
    
    #return json response
    return JSONResponse(decoded)


"""
input: isbn image
output: isbn string
"""
@app.post("/books/isbn")
async def isbn_detection(image: UploadFile = File(...)):
    
    #read image data
    img = await image.read()
    
    #convert image to byte string
    img = np.fromstring(img,dtype=np.uint8)
    
    #read image
    img = cv2.imdecode(img,cv2.IMREAD_COLOR)
    
    #detect
    result = ocr.ocr(img,cls = True)
    
    #find isbn string
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            
            #success
            if 'ISBN' in line[1][0]:
                
                #simple cleansing
                
                #case1 : ISBN 979-11-6050-443-9 (with white space)
                if line[1][0][4] == ' ':
                    
                    data = line[1][0][5:].replace('-','').strip()
                
                #case2 : ISBN979-11-6050-443-9 (no white space)
                elif line[1][0][4] >= '0' and line[1][0][4] <= '9':
                    
                    data = line[1][0][4:].replace('-','').strip()
                
                #case3 : unpredictable case
                else:
                    
                    data = line[1][0]
                    
                return {"status":1, "data":data} 
    
    #fail
    return {"status":0, "data":""} 
    