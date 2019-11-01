# import mistyPy
import misty
import os, requests, time
from xml.etree import ElementTree
import requests
from io import BytesIO
import time
import base64
import http.client
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

# The python interface is not working right now... so all commands need to be made with the API
# tempip = "192.168.43.62"
# misty = mistyPy.Robot(tempip)
def save_audio_to_misty(audio_name, ip_address):
    audioFilePath = audio_name
    with open(audioFilePath, "rb") as audio_file:
        byte_array = bytearray(audio_file.read())

    audio_name = 'temp.wav'
    new_string = ""
    for i in range(len(byte_array)):
        if i == (len(byte_array) - 1):
            new_string += str(byte_array[i])
        else:
            new_string += (str(byte_array[i]) + ",")

    url = "http://"+ip_address+"/api/audio"

    multipart_data = MultipartEncoder(
        fields={
                # a file upload field
                'file': ('temp.wav', open('temp.wav', 'rb'), 'audio/wav'),
                # plain text fields
                'FileName': 'temp.wav',
                'OverwriteExisting': 'true',
                'ImmediatelyApply': 'true',
               }
        )

    r = requests.post(url, data=multipart_data,
                      headers={'Content-Type': multipart_data.content_type})

    print(r.text)

def getTextFromImage(image_path, subscription_key):
    assert subscription_key
    vision_base_url = "https://centralus.api.cognitive.microsoft.com//vision/v2.0/"

    text_recognition_url = vision_base_url + "read/core/asyncBatchAnalyze"

    headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
    # Note: The request parameter changed for APIv2.
    # For APIv1, it is 'handwriting': 'true'.
    params = {'mode': 'Handwritten'}

    image_data = open(image_path, "rb").read()

    response = requests.post(text_recognition_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # Extracting handwritten text requires two API calls: One call to submit the
    # image for processing, the other to retrieve the text found in the image.

    # The recognized text isn't immediately available, so poll to wait for completion.
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
        print(analysis)
        time.sleep(1)
        if ("recognitionResults" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'Failed'):
            poll = False

    results = ""
    if ("recognitionResults" in analysis):
        # Extract the recognized text, with bounding boxes.
        for line in analysis["recognitionResults"][0]["lines"]:
            print(line["text"])
            results += line["text"] + " "

    print(results)
    return [results]


# ---------
class ImageContext(object):
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key

        self.vision_base_url = "https://centralus.api.cognitive.microsoft.com/vision/v2.0/describe?maxCandidates=1&language=en"

        self.headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
        self.params = {'visualFeatures': 'Categories,Description,Color'}

    def get_context(self, image_path):
        image_data = open(image_path, "rb").read()
        response = requests.post(self.vision_base_url, headers=self.headers, params=self.params, data=image_data)
        response.raise_for_status()

        # The 'analysis' object contains various fields that describe the image. The most
        # relevant caption for the image is obtained from the 'description' property.
        analysis = response.json()

        captionList = []
        for entry in analysis["description"]["captions"]:
            captionList.append(entry['text'])

        return captionList


class TextToSpeech(object):
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self.access_token = None
        fetch_token_url = "https://centralus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {'Ocp-Apim-Subscription-Key': self.subscription_key}
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    '''
    The TTS endpoint requires an access token. This method exchanges your
    subscription key for an access token that is valid for ten minutes.
    '''

    def get_token(self):
        fetch_token_url = "https://centralus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def say_this(self, text='Hello', filename=''):
        self.tts = text
        base_url = 'https://centralus.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, JessaRUS)')

        voice.text = self.tts
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)

        if filename == '':
            filename = 'temp'

        '''
        If a success response is returned, then the binary audio is written
        to file in your working directory. It is prefaced by sample and
        includes the date.
        '''
        if response.status_code == 200:
            # with open(filename + '.wav', 'wb') as audio:
            with open(filename + '.wav', 'wb') as audio:
                audio.write(response.content)
                print("Status code(" + str(response.status_code) + "): " + filename + ".wav is ready for playback.")
                return filename + '.wav'

        else:
            print("\nStatus code: " + str(
                response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")


# Get Image Context
# -----------------------------
mistyIPAddress = "192.168.43.62"
robot = misty.Robot(mistyIPAddress)


def moveHeadLeft():
    robot.moveHead(-29, -10, -80, 95)


def moveHeadRight():
    robot.moveHead(29, -10, 80, 95)


def moveHeadCenter():
    robot.moveHead(0, -7, 0, 95)

def readSomething():
    tts = TextToSpeech("9d116c1864e640c3b1b87a8c1dd74736")  # Cognitive Service Voice Service Subscription Key

    time.sleep(1)

    response = requests.get("http://" + mistyIPAddress + "/api/cameras/rgb?Base64=true")
    # response.raise_for_status()
    analysis = response.json()
    data = analysis
    b64data = data['result']['base64']

    imgdata = base64.b64decode(b64data)

    imgFile = open('./snapshot.jpg', 'wb')
    imgFile.write(imgdata)

    # Announce Text
    toAnnounce = ""
    for text in getTextFromImage("./snapshot.jpg",
                                 "9d116c1864e640c3b1b87a8c1dd74736"):  # Cognitive Service Vision Service Subscription Key
        print("---------" + text)
        toAnnounce += text + " or "

    if len(toAnnounce) > 4:
        fileName = tts.say_this(toAnnounce[0:-4])
        audioFilePath = fileName
        print(audioFilePath)

        save_audio_to_misty(fileName, mistyIPAddress)




try:
    while True:
        moveHeadLeft()
        time.sleep(4)
        moveHeadCenter()
        readSomething()
        moveHeadRight()
        time.sleep(4)
        moveHeadCenter()
        readSomething()
except KeyboardInterrupt:
    pass