import requests

text = """BODY FLUIDS AND CIRCULATION 193
You have learnt that all living cells have to be provided with nutrients, O2
and other essential substances. Also, the waste or harmful substances
produced , have to be removed continuously for healthy functioning  of
tissues . It is therefore, essential to have efficient mechanism s for the
movement of these substances to the cells and from the cells. Different
groups of animals have evolved different methods for this transport. Simple
organisms like sponges and coelenterates circulate water from their
surroundings through their body cavities to facilitate the cells to exchange
these substances. More complex organisms use special fluids within their
bodies to transport such materials. Blood  is the most commonly used body
fluid by most of the higher organisms , including humans , for this
purpose. A nother body fluid, lymph , also helps in the transport of
certain substances. I n this chapter , you will learn about the composition
and properties of blood and lymph  (tissue fluid)  and the mechanism of
circulation of blood is also explained herein.
15.1 BLOOD
Blood is a special connective tissue consisting of a fluid matrix, plasma,
and formed elements.
15.1.1 Plasma
Plasma is a straw coloured, viscous fluid constituting nearly 55 per cent of
the blood. 90-92 per cent of plasma is water and proteins contribute 6-8
per cent of it. Fibrinogen, globulins and albumins are the major proteins.BODY FLUIDS AND CIRCULATIONCHAPTER   15
15.1 Blood
15.2 Lymph (T issue
Fluid)
15.3 Circulatory
Pathways
15.4 Double
Circulation
15.5 Regulation of
Cardiac
Activity
15.6 Disorders of
Circulatory
System
Reprint 2026-27"""

url = "http://localhost:5000/predict_text"

r1 = requests.post(url, json={"text": text})
print("Original Text AI Prob:", r1.json().get('prob_ai'))

clean_text = text.replace('\n', ' ')
r2 = requests.post(url, json={"text": clean_text})
print("Clean Text AI Prob:", r2.json().get('prob_ai'))
