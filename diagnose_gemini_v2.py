"""
Targeted MailMind Gemini model test.
Reads GEMINI_API_KEY from .env, never prints the key.
"""
import json, os, urllib.error, urllib.request
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

key=os.getenv("GEMINI_API_KEY","").strip()
base="https://generativelanguage.googleapis.com/v1beta"
if not key:
    print("Missing GEMINI_API_KEY in .env"); raise SystemExit(1)

def call(model):
    payload={"contents":[{"parts":[{"text":"Write exactly: MailMind connection test passed."}]}],
             "generationConfig":{"temperature":0,"maxOutputTokens":30}}
    req=urllib.request.Request(f"{base}/models/{model}:generateContent",
        data=json.dumps(payload).encode(),
        headers={"x-goog-api-key":key,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as res:
            data=json.loads(res.read())
            text=data["candidates"][0]["content"]["parts"][0]["text"]
            return res.status,text
    except urllib.error.HTTPError as e:
        try: data=json.loads(e.read())
        except: data={}
        er=data.get("error",{})
        return e.code, f'{er.get("status","")} | {er.get("message","")}'
    except Exception as e:
        return "ERROR",str(e)

# These are text-capable models listed by the user's successful model-catalog call.
candidates=["gemini-3.8-flash","gemini-3.7-flash","gemini-3.6-flash"]
print("Testing only listed, text-generation Flash models, sequentially:")
for model in candidates:
    print(f"\n{model}:")
    status, result=call(model)
    print(f"HTTP {status}: {result}")
    if status == 200:
        print(f"\nSUCCESS MODEL: {model}")
        break
print("\nDone. API key was not displayed.")
