# from fastapi import FastAPI, HTTPException    #define routes
# from fastapi.middleware.cors import CORSMiddleware #connect with frontend
# from pydantic import BaseModel  #define structure of data
# from googletrans import Translator, LANGUAGES   #translate using google
# from gtts import gTTS # text to spoken audio
# from fastapi.responses import StreamingResponse #return audio response as stream to the given route
# import io  #python input output

# app = FastAPI()

# origins = [
#     "http://localhost:3000",
#     "http://172.17.0.1:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# translator = Translator()

# class TranslationRequest(BaseModel):
#     text: str
#     source_lang: str
#     dest_lang: str

# class TextToSpeechRequest(BaseModel):
#     text: str
#     lang: str


# @app.get('/')
# def welcome():
#     return {'msg': 'Welcome to translator API backend.'}

# @app.get("/languages")
# def get_supported_languages():
#     return LANGUAGES

# @app.post("/translate")
# def translate_text(request: TranslationRequest):
#     translated = translator.translate(request.text, src=request.source_lang, dest=request.dest_lang)
#     return {"translated_text": translated.text}

# @app.post("/text-to-speech")
# def text_to_speech(request: TextToSpeechRequest):
#     tts = gTTS(text=request.text, lang=request.lang)
#     audio_file = io.BytesIO()
#     tts.write_to_fp(audio_file)
#     audio_file.seek(0)
#     return StreamingResponse(audio_file, media_type="audio/mpeg")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="localhost", port=8000)

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from fastapi.responses import StreamingResponse
import io
import speech_recognition as sr

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://172.17.0.1:3000",
    "http://127.0.0.1:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = Translator()

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    dest_lang: str

class TextToSpeechRequest(BaseModel):
    text: str
    lang: str

@app.get('/')
def welcome():
    return {'msg': 'Welcome to translator API backend.'}

@app.get("/languages")
def get_supported_languages():
    return LANGUAGES

@app.post("/translate")
def translate_text(request: TranslationRequest):
    translated = translator.translate(request.text, src=request.source_lang, dest=request.dest_lang)
    return {"translated_text": translated.text}

@app.post("/text-to-speech")
def text_to_speech(request: TextToSpeechRequest):
    tts = gTTS(text=request.text, lang=request.lang)
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return StreamingResponse(audio_file, media_type="audio/mpeg")

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()
    audio_data = await file.read()

    with open("temp_audio.webm", "wb") as f:
        f.write(audio_data)

    # Convert webm to wav using ffmpeg
    import subprocess
    subprocess.run(['ffmpeg', '-y', '-i', 'temp_audio.webm', 'temp_audio.wav'])

    with sr.AudioFile("temp_audio.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return {"text": text}
        except sr.UnknownValueError:
            raise HTTPException(status_code=400, detail="Speech not recognized")
        except sr.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
