from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import translators.server as tss
from langdetect import detect
import http.client

openai.api_key = "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"

def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

def create_ip_ports_array(ip: str, *ports):
    array = []
    for port in ports:
        array.append(f"{ip}:{str(port)}")
    return array

app = FastAPI(
    title="ChatGPT",
    version="1.0.0")

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://192.168.0.200",
    "http://192.168.0.200:80"
    "http://192.168.0.200:3000"
    "http://192.168.0.41:3000",
    "http://192.168.0.41",
    "http://localhost"]

origins += get_self_public_ip()

origins += create_ip_ports_array(get_self_public_ip(), 3000, 8000, 80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS", "DELETE", "PUT"],
    allow_headers=["Access-Control-Allow-Headers",
                   'Content-Type',
                   'Authorization',
                   'Access-Control-Allow-Origin'])


@app.get("/")
async def index(
        request: Request,
        text: str,
):
    lang = detect(text)

    if lang != "en":
        text = tss.google(text, 'ru', 'en')
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )
    except openai.error.RateLimitError as err:
        return str(err)

    if lang != "en":
        return tss.google(response["choices"][0]["text"].replace("\n", ""), 'en', 'ru')
    else:
        return response["choices"][0]["text"].replace("\n", "")
