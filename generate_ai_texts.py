import os
import random

topics = [
    "Artificial Intelligence", "Machine Learning", "Quantum Computing", "Renewable Energy", 
    "Space Exploration", "Deep Learning", "Data Science", "Cybersecurity", "Blockchain", 
    "Virtual Reality", "Augmented Reality", "Cloud Computing", "Internet of Things", 
    "5G Networks", "Autonomous Vehicles", "Robotics", "Biotechnology", "Genomics", 
    "Nanotechnology", "3D Printing", "Edge Computing", "Smart Cities", "Fintech",
    "Digital Twins", "Precision Medicine", "Neuromorphic Computing", "Natural Language Processing"
]

intros = [
    "The field of {topic} has seen rapid advancements in recent years.",
    "Understanding {topic} is crucial for navigating the modern technological landscape.",
    "When exploring {topic}, several key principles must be taken into account.",
    "{topic} represents a significant paradigm shift in how we approach problem-solving.",
    "A comprehensive analysis of {topic} reveals both opportunities and challenges.",
    "Recent developments in {topic} highlight a growing trend toward automated solutions.",
    "As {topic} continues to evolve, researchers are discovering novel applications."
]

bodies = [
    "Firstly, it leverages complex algorithms to process vast amounts of information efficiently. Additionally, researchers are constantly iterating on these models to improve accuracy. Furthermore, integration with existing systems requires careful planning and execution.",
    "One of the primary benefits is the automation of repetitive tasks, which frees up human resources for more creative endeavors. However, it is essential to consider the ethical implications and potential biases inherent in such systems. Regular audits and transparent methodologies are highly recommended.",
    "The underlying architecture is designed to be highly scalable and robust. By utilizing distributed networks, it minimizes latency and maximizes throughput. Consequently, organizations can achieve unprecedented levels of performance and reliability.",
    "Current trends indicate a move towards more decentralized and open-source frameworks. This democratization allows for wider participation and faster innovation cycles. As a result, the barrier to entry has significantly decreased for new developers and startups.",
    "At its core, the system relies on predictive modeling and statistical analysis. By identifying patterns in historical data, it can forecast future outcomes with a high degree of confidence. This capability is particularly valuable in dynamic and uncertain environments.",
    "To fully leverage this technology, organizations must prioritize data governance and security. Robust encryption protocols and access controls are fundamental to protecting sensitive information while still allowing for seamless collaboration across different departments."
]

conclusions = [
    "In conclusion, the ongoing evolution of {topic} will undoubtedly shape the future of society.",
    "Ultimately, the successful implementation of {topic} depends on continuous learning and adaptation.",
    "To summarize, while {topic} presents certain hurdles, its potential benefits are too significant to ignore.",
    "Looking ahead, {topic} is poised to become an integral part of our daily lives and professional workflows.",
    "Therefore, stakeholders must remain vigilant and proactive in guiding the development of {topic}.",
    "Ultimately, fostering a collaborative ecosystem will be key to unlocking the full potential of {topic}."
]

vocab = ["synergy", "paradigm", "scalability", "robustness", "dynamic", "optimization", "framework", "infrastructure", "methodology", "integration", "innovation", "algorithms", "automation"]

def generate_ai_text():
    topic = random.choice(topics)
    intro = random.choice(intros).format(topic=topic)
    body = random.choice(bodies)
    conclusion = random.choice(conclusions).format(topic=topic)
    
    # Add a bulleted list which is very common for AI
    bullets = "\n- " + "\n- ".join([f"Enhancing {random.choice(vocab)} through {random.choice(vocab)}" for _ in range(random.randint(2, 4))])
    
    return f"{intro}\n\n{body}\n\nKey considerations include:{bullets}\n\n{conclusion}"

output_dir = r"c:\voice-check\dataset_text\ai"
os.makedirs(output_dir, exist_ok=True)

# Generate files from 182 to 1000
for i in range(182, 1001):
    file_path = os.path.join(output_dir, f"{i}.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(generate_ai_text())

print(f"AI text files generated successfully up to 1000.")
