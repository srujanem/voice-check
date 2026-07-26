import requests

r = requests.get("https://authguard-cuejehgfd-srujanems-projects.vercel.app/document-ui/script.js")
print(r.text[:200])
if "Math.random()" in r.text:
    print("STILL MOCK SCRIPT ON VERCEL!")
else:
    print("NEW SCRIPT IS ON VERCEL!")
