"""
Generate high-quality, realistic AI-style text for files 182-1000 in dataset_text/ai/
These should sound like real ChatGPT/Gemini outputs - clear, structured, formal,
comprehensive with typical AI patterns (numbered lists, smooth transitions, hedging phrases).
"""
import os, random

output_dir = r"c:\voice-check\dataset_text\ai"

# ─── Topic pools ──────────────────────────────────────────────────────────────
TOPICS = [
    ("climate change", "global warming and its effects on ecosystems", "environmental science"),
    ("machine learning", "neural networks and deep learning algorithms", "artificial intelligence"),
    ("ancient rome", "the rise and fall of the Roman Empire", "history"),
    ("photosynthesis", "how plants convert sunlight into energy", "biology"),
    ("black holes", "the physics of gravitational singularities", "astrophysics"),
    ("the french revolution", "causes and consequences of the French Revolution", "history"),
    ("vaccines", "how vaccines work and their importance to public health", "medicine"),
    ("cryptocurrency", "blockchain technology and digital currencies", "finance"),
    ("the water cycle", "evaporation, condensation, and precipitation", "earth science"),
    ("mental health", "the importance of mental wellness and psychological support", "psychology"),
    ("supply chain", "how global supply chains function and their vulnerabilities", "economics"),
    ("the human genome", "DNA sequencing and genetic research", "genetics"),
    ("social media", "the impact of social media on society and communication", "sociology"),
    ("renewable energy", "solar, wind and hydroelectric power sources", "energy"),
    ("the industrial revolution", "mechanization and its economic impact", "history"),
    ("artificial intelligence ethics", "bias, fairness and accountability in AI systems", "ethics"),
    ("ocean acidification", "how CO2 is changing marine chemistry", "environmental science"),
    ("quantum computing", "quantum bits and superposition in computing", "physics"),
    ("the nervous system", "neurons, synapses and brain function", "biology"),
    ("global trade", "international trade agreements and their economic effects", "economics"),
    ("antibiotic resistance", "how bacteria evolve to defeat antibiotics", "medicine"),
    ("the solar system", "planets, moons and the structure of our solar system", "astronomy"),
    ("democracy", "principles of democratic governance and civic participation", "political science"),
    ("nutrition", "macronutrients, micronutrients and dietary balance", "health"),
    ("the Renaissance", "art, science and humanism in Renaissance Europe", "history"),
    ("cybersecurity", "threats, vulnerabilities and network protection strategies", "technology"),
    ("plate tectonics", "continental drift and geological processes", "earth science"),
    ("behavioral economics", "how psychology influences financial decision-making", "economics"),
    ("language acquisition", "how children and adults learn new languages", "linguistics"),
    ("the immune system", "how the body defends against pathogens", "biology"),
    ("urbanization", "the growth of cities and its social consequences", "sociology"),
    ("photovoltaic technology", "how solar panels convert light to electricity", "engineering"),
    ("the Silk Road", "ancient trade networks connecting East and West", "history"),
    ("ecosystem biodiversity", "species richness and ecological balance", "ecology"),
    ("inflation", "causes and effects of rising price levels", "economics"),
    ("stem cells", "types, uses and ethical considerations of stem cell research", "medicine"),
    ("deforestation", "causes and consequences of forest loss", "environment"),
    ("the Enlightenment", "reason, science and individual rights in 18th century Europe", "history"),
    ("space exploration", "the history and future of human spaceflight", "science"),
    ("cognitive biases", "common mental shortcuts and their effects on judgment", "psychology"),
]

# ─── Text templates ────────────────────────────────────────────────────────────
def make_intro(topic, desc):
    intros = [
        f"{topic.capitalize()} is a subject that has garnered significant attention in recent decades. At its core, {desc} represents one of the most compelling areas of inquiry for researchers and practitioners alike.",
        f"Understanding {topic} is essential in today's rapidly changing world. {desc.capitalize()} touches on fundamental questions that affect both individuals and society as a whole.",
        f"The study of {topic} has evolved considerably over the past century. Scholars now recognize that {desc} involves a complex interplay of factors that cannot be easily reduced to simple explanations.",
        f"Few topics in {desc.split('and')[0].strip()} are as consequential as {topic}. A thorough examination reveals layers of complexity that reward careful analysis.",
        f"When examining {topic}, it is important to consider both the historical context and the contemporary implications. {desc.capitalize()} shapes policy, research agendas, and everyday decision-making.",
    ]
    return random.choice(intros)

def make_body(topic, field):
    sections = [
        f"From a {field} perspective, several key mechanisms are at work. First, the foundational principles must be clearly understood before examining their broader applications. Researchers have identified multiple contributing factors, each of which plays a distinct role in shaping outcomes. Second, empirical evidence consistently supports the view that {topic} has measurable, real-world consequences. Studies conducted across diverse populations and settings have yielded broadly consistent findings, lending confidence to current theoretical frameworks. Finally, practical implications must be considered. Policymakers, educators, and industry leaders are increasingly called upon to make evidence-based decisions informed by the latest scholarship.",

        f"To fully appreciate the significance of {topic}, one must consider it from multiple angles. Historically, this subject was poorly understood, and early theories often failed to account for the full range of observed phenomena. Over time, advances in methodology and data collection have enabled more nuanced and accurate models. Today, the prevailing consensus among experts in {field} holds that a multi-factorial approach is necessary. No single variable is sufficient to explain the complexity at play. Instead, researchers must account for interactions between biological, social, economic, and technological systems.",

        f"There are several important dimensions to consider when discussing {topic}. The first concerns the underlying mechanisms: how and why does this phenomenon occur? The second relates to scale: does it operate at the individual level, the community level, or globally? The third involves time: are we examining short-term fluctuations or long-term trends? Each of these dimensions offers a different lens through which {field} professionals can interpret the evidence. Integrating these perspectives yields a richer and more complete understanding.",

        f"Research in the field of {field} has shed considerable light on {topic}. Longitudinal studies, meta-analyses, and controlled experiments have all contributed to the body of knowledge. Key findings suggest that early intervention tends to produce the most significant outcomes, that systemic factors often outweigh individual-level variables, and that context matters enormously when applying general principles to specific cases. These insights have practical implications for how institutions design programs, allocate resources, and evaluate effectiveness.",
    ]
    return random.choice(sections)

def make_conclusion(topic):
    conclusions = [
        f"In summary, {topic} is a multifaceted subject that demands careful, evidence-based inquiry. As our understanding deepens, it becomes increasingly clear that simplistic approaches are inadequate. Moving forward, collaboration across disciplines will be essential to address the most pressing challenges and opportunities that {topic} presents.",
        f"To conclude, the study of {topic} reveals both the complexity of the underlying systems and the importance of informed, thoughtful engagement. Whether one approaches this topic as a student, a professional, or a concerned citizen, the insights available are both intellectually enriching and practically valuable.",
        f"Ultimately, {topic} sits at the intersection of theory and practice, science and policy, individual experience and collective outcome. Continued research, open dialogue, and a commitment to evidence are the best tools we have for navigating its challenges and harnessing its potential.",
        f"The evidence makes clear that {topic} deserves sustained attention and investment. As the body of knowledge continues to grow, so too does our capacity to respond effectively. The path forward requires interdisciplinary collaboration, rigorous methodology, and a genuine commitment to translating research into action.",
    ]
    return random.choice(conclusions)

def generate_ai_text():
    topic_tuple = random.choice(TOPICS)
    topic, desc, field = topic_tuple
    
    intro = make_intro(topic, desc)
    body = make_body(topic, field)
    conclusion = make_conclusion(topic)
    
    # Sometimes add a numbered list (very AI-like)
    if random.random() < 0.45:
        items = [
            f"Understanding the foundational principles of {topic}",
            f"Analyzing empirical evidence from {field} research",
            f"Evaluating the policy and practical implications",
            f"Considering ethical and social dimensions",
            f"Applying findings to real-world contexts",
        ]
        chosen = random.sample(items, k=random.randint(3, 4))
        list_block = "\n\nKey areas of focus include:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(chosen))
        return f"{intro}\n\n{body}{list_block}\n\n{conclusion}"
    else:
        return f"{intro}\n\n{body}\n\n{conclusion}"

# ─── Write files ───────────────────────────────────────────────────────────────
count = 0
for i in range(182, 1001):
    path = os.path.join(output_dir, f"{i}.txt")
    text = generate_ai_text()
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    count += 1

print(f"Done. Regenerated {count} AI text files (182–1000) with high-quality content.")
