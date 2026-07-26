import os, random

out_dir = os.path.join("dataset_text", "ai_generated")
os.makedirs(out_dir, exist_ok=True)

ai_openers = [
    "In today's fast-paced world, {} plays a crucial role in modern society.",
    "Furthermore, it is essential to delve into the intricate nuances of {} to fully appreciate its implications.",
    "Understanding {} is paramount when examining the complex dynamics of contemporary science and technology.",
    "{} represents a fascinating interplay between fundamental principles and practical applications.",
    "In conclusion, the significance of {} cannot be overstated as it fosters continuous advancement.",
    "It is important to note that {} serves as a testament to human innovation and discovery.",
    "Moreover, the multifaceted nature of {} offers valuable insights into various academic disciplines.",
    "A thorough analysis of {} underscores the critical need for comprehensive research and development."
]

topics = [
    "artificial intelligence and machine learning algorithms",
    "photosynthesis and carbon fixation in green plants",
    "the French Revolution and its societal impact on Europe",
    "quantum computing and subatomic particle mechanics",
    "climate change, greenhouse gas emissions, and global warming",
    "cellular respiration, ATP synthesis, and mitochondrial function",
    "electric current, charge flow, and electromagnetic fields",
    "renewable energy, solar panels, and sustainable infrastructure",
    "blockchain technology, decentralized networks, and cryptography",
    "data science, big data analytics, and predictive modeling",
    "genetic engineering, CRISPR gene editing, and biotechnology",
    "neuroscience, brain plasticity, and cognitive development",
    "macroeconomics, inflation, and monetary policy",
    "space exploration, astrophysics, and dark matter",
    "cybersecurity, network firewalls, and encryption standards"
]

ai_bodies = [
    "Researchers and experts continuously highlight the transformational impact of these mechanisms. By leveraging structured methodology, efficiency is significantly enhanced across all operational boundaries.",
    "This process functions through interconnected pathways that optimize performance. The underlying framework ensures high accuracy while minimizing potential discrepancies in system execution.",
    "Key factors contributing to this phenomenon include structured variables, environmental conditions, and technological integration. Consequently, observing these parameters yields consistent empirical results.",
    "When evaluating the overall effect, one must consider both short-term outcomes and long-term consequences. This dual perspective enables a holistic understanding of the operational paradigm."
]

count = 0
for topic in topics:
    for opener in ai_openers:
        for body in ai_bodies:
            count += 1
            text = f"{opener.format(topic)} {body} Overall, this multifaceted approach demonstrates how key elements interact to shape contemporary standards."
            with open(os.path.join(out_dir, f"{count}.txt"), "w", encoding="utf-8") as fp:
                fp.write(text)

print(f"Generated {count} rich AI training samples in {out_dir}!")
