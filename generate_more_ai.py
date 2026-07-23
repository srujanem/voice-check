"""
Generate 1,888 high-quality AI-style text samples (files 1002–2889)
to balance the dataset with the 2,889 human samples.
"""
import os, random

output_dir = r"c:\voice-check\dataset_text\ai"
os.makedirs(output_dir, exist_ok=True)

# Find starting index
existing = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
start_idx = 1002
for f in existing:
    try:
        idx = int(f.split('.')[0])
        if idx >= start_idx:
            start_idx = idx + 1
    except ValueError:
        pass

TARGET = 2889  # match human count

# ── Topic pools ──────────────────────────────────────────────────────────────
science_topics = [
    ("photosynthesis", "Plants convert sunlight into chemical energy through photosynthesis. This process occurs in the chloroplasts and involves two stages: the light-dependent reactions and the Calvin cycle. During the light-dependent reactions, water molecules are split, releasing oxygen as a byproduct. The Calvin cycle uses carbon dioxide from the atmosphere to produce glucose, which serves as the primary energy source for the plant."),
    ("Newton's laws", "Newton's three laws of motion form the foundation of classical mechanics. The first law states that an object at rest stays at rest unless acted upon by an external force. The second law establishes that force equals mass multiplied by acceleration (F=ma). The third law asserts that for every action there is an equal and opposite reaction, which explains phenomena ranging from rocket propulsion to everyday walking."),
    ("cell division", "Cell division is a fundamental biological process that allows organisms to grow, repair, and reproduce. Mitosis produces two genetically identical daughter cells and is responsible for growth and tissue repair. Meiosis, on the other hand, produces four genetically unique gametes through two rounds of division and is essential for sexual reproduction. The regulation of cell division is critical, as errors can lead to cancer."),
    ("gravity", "Gravity is the fundamental force of attraction between objects with mass. Described by Einstein's general theory of relativity as the curvature of spacetime, it governs the motion of planets, stars, and galaxies. On Earth, gravity gives objects weight and causes them to fall at approximately 9.8 meters per second squared. The escape velocity — the speed needed to break free from Earth's gravitational field — is approximately 11.2 kilometers per second."),
    ("DNA replication", "DNA replication is the process by which a cell copies its genetic information before cell division. The double helix unwinds as helicase breaks the hydrogen bonds between base pairs. DNA polymerase then adds complementary nucleotides to each template strand in the 5' to 3' direction. This semi-conservative process ensures that each daughter cell receives an identical copy of the genome, with one original strand and one newly synthesized strand."),
    ("ecosystems", "An ecosystem encompasses all living organisms in a given area along with their physical environment. Energy flows through ecosystems via food chains and food webs, starting with primary producers that convert solar energy into organic matter. Decomposers play a crucial role by breaking down dead organic matter and recycling nutrients. The balance of an ecosystem depends on biodiversity, and the removal of keystone species can cause cascading effects throughout the entire system."),
    ("electric circuits", "Electric circuits provide pathways for current to flow from a power source through various components. In a series circuit, components are connected end-to-end, so the same current flows through each element. In a parallel circuit, components share the same two nodes, providing multiple paths for current and allowing each component to operate independently. Ohm's Law (V = IR) relates voltage, current, and resistance and is fundamental to circuit analysis."),
    ("human digestive system", "The human digestive system is responsible for breaking down food into nutrients that the body can absorb. The process begins in the mouth, where salivary amylase starts breaking down carbohydrates. Food travels down the esophagus to the stomach, where it is mixed with gastric acid and enzymes. The small intestine is the primary site of nutrient absorption, while the large intestine absorbs water and prepares waste for elimination."),
    ("climate change", "Climate change refers to long-term shifts in global temperatures and weather patterns. While natural factors contribute to climate variability, human activities such as burning fossil fuels, deforestation, and industrial processes have significantly accelerated warming since the industrial revolution. The increased concentration of greenhouse gases traps more heat in the atmosphere, leading to rising sea levels, more frequent extreme weather events, and disruptions to ecosystems worldwide."),
    ("chemical bonds", "Chemical bonds are the forces that hold atoms together in molecules and compounds. Ionic bonds form when electrons are transferred from one atom to another, creating oppositely charged ions that attract each other. Covalent bonds involve the sharing of electrons between atoms, resulting in stable molecules. The properties of a substance — including its melting point, solubility, and electrical conductivity — are largely determined by the types and strengths of the chemical bonds it contains."),
]

social_topics = [
    ("democracy", "Democracy is a system of government in which citizens exercise power through voting and elected representatives. It is founded on principles of political equality, freedom of speech, and the rule of law. Modern democracies typically feature separation of powers among legislative, executive, and judicial branches to prevent the concentration of authority. Participatory democracy encourages direct citizen engagement in decision-making, while representative democracy delegates authority to elected officials."),
    ("the French Revolution", "The French Revolution, which began in 1789, was a period of radical political and societal transformation in France. Driven by Enlightenment ideals of liberty, equality, and fraternity, the revolution dismantled the monarchy and aristocracy. Key events included the storming of the Bastille, the Declaration of the Rights of Man, and the Reign of Terror. The revolution profoundly reshaped European politics and laid the groundwork for modern democratic governance and nationalism."),
    ("economic inequality", "Economic inequality refers to the unequal distribution of income, wealth, and opportunities within a society. It is measured using tools such as the Gini coefficient, where a score of zero represents perfect equality and one represents maximum inequality. Research suggests that high levels of economic inequality can slow economic growth, reduce social mobility, and increase political instability. Policy responses include progressive taxation, investment in education, and strengthening social safety nets."),
    ("urbanization", "Urbanization is the process by which rural populations migrate to cities, leading to the growth of urban areas. This phenomenon is driven by the search for better economic opportunities, access to services, and improved living standards. While urbanization fuels economic development and innovation, it also presents challenges such as housing shortages, traffic congestion, environmental pollution, and the strain on public infrastructure. Sustainable urban planning is essential to manage these challenges effectively."),
    ("human rights", "Human rights are the fundamental rights and freedoms that belong to every person, regardless of nationality, gender, ethnicity, or religion. They are enshrined in documents such as the Universal Declaration of Human Rights, adopted by the United Nations in 1948. These rights include the right to life, freedom from torture, the right to education, and freedom of expression. The international community works through treaties, courts, and advocacy organizations to hold states accountable for protecting these rights."),
    ("the Industrial Revolution", "The Industrial Revolution, beginning in Britain in the late 18th century, transformed economies from agrarian to industrial systems. Powered by inventions such as the steam engine and the spinning jenny, mass production replaced cottage industries. While it generated enormous wealth and technological progress, it also caused significant social upheaval, including harsh working conditions, child labor, and rapid urbanization. It laid the foundation for modern capitalism and sparked labor movements advocating for workers' rights."),
    ("globalization", "Globalization refers to the increasing interconnectedness of economies, cultures, and populations across the world. Advances in transportation, communication technology, and trade agreements have accelerated the flow of goods, services, capital, and people across borders. While globalization has lifted millions out of poverty and fostered cultural exchange, it has also contributed to concerns about job displacement in developed nations, cultural homogenization, and the outsized influence of multinational corporations."),
    ("Indian independence", "India's independence on August 15, 1947, marked the end of nearly 200 years of British colonial rule. The independence movement was led by figures such as Mahatma Gandhi, who championed nonviolent civil disobedience, and Jawaharlal Nehru, who became India's first Prime Minister. The partition of the subcontinent into India and Pakistan resulted in one of the largest mass migrations in history and significant communal violence. India's constitution, adopted in 1950, established it as a sovereign, democratic republic."),
    ("the United Nations", "The United Nations was established in 1945 following World War II with the primary goal of maintaining international peace and security. Its charter is based on the principles of sovereign equality of member states, peaceful resolution of disputes, and respect for human rights. The UN's main bodies include the General Assembly, the Security Council, and the International Court of Justice. Through agencies such as UNICEF, WHO, and UNESCO, the UN addresses global challenges ranging from health and education to humanitarian crises."),
    ("nationalism", "Nationalism is the ideology that a group of people sharing a common identity, culture, or language should form or maintain their own state. It has been a powerful force in shaping modern history, driving independence movements and the unification of nations. However, extreme nationalism has also fueled conflicts, wars, and ethnic persecution. In the contemporary world, nationalism is in tension with internationalism and global cooperation, as nations navigate issues of sovereignty, immigration, and shared challenges like climate change."),
]

technology_topics = [
    ("artificial intelligence", "Artificial intelligence (AI) refers to the simulation of human intelligence in machines programmed to think, learn, and problem-solve. Modern AI systems rely on machine learning, particularly deep learning, where neural networks with multiple layers are trained on vast datasets to recognize patterns. Applications of AI span numerous fields, including natural language processing, computer vision, robotics, and medical diagnostics. As AI capabilities grow, important ethical questions arise around bias, accountability, privacy, and the future of work."),
    ("blockchain technology", "Blockchain is a decentralized digital ledger that records transactions across a network of computers in a way that is secure, transparent, and immutable. Each block in the chain contains a set of transactions and is cryptographically linked to the previous one, making it extremely difficult to alter past records. Originally developed to underpin Bitcoin, blockchain technology now has diverse applications in supply chain management, healthcare records, smart contracts, and digital identity verification."),
    ("machine learning", "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from data without being explicitly programmed for each task. Supervised learning uses labeled training data to teach a model to make predictions, while unsupervised learning discovers hidden patterns in unlabeled data. Reinforcement learning trains agents through a system of rewards and penalties. Machine learning powers recommendation systems, fraud detection, autonomous vehicles, and many other technologies that have become integral to modern life."),
    ("renewable energy", "Renewable energy is derived from naturally replenishing sources such as sunlight, wind, water, and geothermal heat. Unlike fossil fuels, these sources produce little to no greenhouse gas emissions, making them essential for combating climate change. Solar photovoltaic and wind turbine technologies have seen dramatic cost reductions over the past decade, making them increasingly competitive with conventional energy. Challenges remain in grid integration and energy storage, but continued innovation is rapidly addressing these obstacles."),
    ("cybersecurity", "Cybersecurity encompasses the practices and technologies designed to protect computer systems, networks, and data from unauthorized access, theft, and damage. Common threats include malware, phishing attacks, ransomware, and denial-of-service attacks. As digital infrastructure becomes more critical to society, the consequences of cyberattacks grow more severe. Effective cybersecurity requires a layered approach including firewalls, encryption, multi-factor authentication, regular software updates, and employee training to recognize social engineering tactics."),
    ("the internet of things", "The Internet of Things (IoT) refers to the network of physical devices embedded with sensors, software, and connectivity that enables them to collect and exchange data. From smart home appliances and wearable fitness trackers to industrial sensors and connected vehicles, IoT devices are transforming how we interact with the physical world. While IoT offers tremendous benefits in efficiency and convenience, it also raises significant concerns about data privacy, security vulnerabilities, and the management of massive amounts of generated data."),
    ("quantum computing", "Quantum computing harnesses the principles of quantum mechanics to process information in fundamentally different ways from classical computers. Unlike classical bits, which represent either 0 or 1, quantum bits (qubits) can exist in a superposition of both states simultaneously. This allows quantum computers to perform certain calculations exponentially faster than classical counterparts. Potential applications include breaking current encryption methods, accelerating drug discovery, and optimizing complex logistical systems, though practical large-scale quantum computers remain a significant engineering challenge."),
    ("social media impact", "Social media platforms have fundamentally transformed how people communicate, consume information, and form social identities. These platforms enable rapid information sharing, community building, and political mobilization on a global scale. However, they also contribute to challenges such as the spread of misinformation, online harassment, filter bubbles that reinforce existing beliefs, and negative impacts on mental health, particularly among young users. The regulation of social media platforms has become a pressing policy issue for governments worldwide."),
    ("data privacy", "Data privacy concerns the right of individuals to control how their personal information is collected, used, and shared by organizations. With the exponential growth of digital data, protecting personal information has become increasingly challenging. Regulations such as the European Union's General Data Protection Regulation (GDPR) and California's Consumer Privacy Act (CCPA) set standards for data handling and give individuals rights over their data. Despite regulatory efforts, data breaches, invasive tracking practices, and the monetization of personal data remain pervasive concerns."),
    ("autonomous vehicles", "Autonomous vehicles use a combination of sensors, cameras, radar, and artificial intelligence to navigate roads without human input. They are typically classified on a scale from Level 0 (no automation) to Level 5 (full automation). Proponents argue that self-driving cars will dramatically reduce traffic accidents, most of which are caused by human error, while improving mobility for elderly and disabled individuals. Challenges to widespread adoption include technological limitations in complex environments, regulatory frameworks, liability questions, and public trust."),
]

health_topics = [
    ("mental health", "Mental health encompasses emotional, psychological, and social well-being, affecting how people think, feel, and behave in daily life. Conditions such as depression, anxiety, and schizophrenia are among the most common and debilitating illnesses worldwide. Effective treatments include psychotherapy, medication, lifestyle changes, and social support. Despite growing awareness, significant stigma surrounding mental illness prevents many people from seeking help. Integrating mental health services into primary healthcare systems is considered a critical step toward addressing this global health challenge."),
    ("vaccines", "Vaccines are biological preparations that stimulate the immune system to recognize and fight specific pathogens without causing the disease itself. They introduce antigens — weakened, killed, or partial forms of a pathogen — prompting the body to produce antibodies and establish immunological memory. Vaccines have been among the most effective public health interventions in history, eradicating smallpox and dramatically reducing diseases like polio, measles, and diphtheria. Herd immunity occurs when a sufficient proportion of a population is vaccinated, protecting even those who cannot receive vaccines."),
    ("nutrition", "Proper nutrition is fundamental to maintaining good health and preventing chronic disease. A balanced diet provides essential macronutrients — carbohydrates, proteins, and fats — as well as micronutrients like vitamins and minerals. Diets rich in fruits, vegetables, whole grains, and lean proteins are associated with reduced risk of heart disease, type 2 diabetes, and certain cancers. Processed foods high in added sugars, sodium, and saturated fats, on the other hand, contribute to obesity and metabolic disorders. Understanding nutritional science empowers individuals to make healthier dietary choices."),
    ("exercise and fitness", "Regular physical activity is one of the most effective ways to maintain physical and mental health. Exercise improves cardiovascular function, strengthens muscles and bones, regulates blood sugar levels, and reduces the risk of chronic diseases. The World Health Organization recommends that adults engage in at least 150 minutes of moderate-intensity aerobic activity per week. Beyond physical benefits, regular exercise has been shown to reduce symptoms of depression and anxiety, improve sleep quality, and enhance cognitive function."),
    ("infectious diseases", "Infectious diseases are illnesses caused by pathogenic microorganisms such as bacteria, viruses, fungi, and parasites that can spread between individuals. Transmission occurs through various routes including direct contact, respiratory droplets, contaminated water or food, and vectors like mosquitoes. Prevention strategies include vaccination, good hygiene practices, safe food handling, and vector control. The global response to infectious disease outbreaks requires coordinated international surveillance, rapid diagnostic capabilities, and equitable access to treatments and vaccines."),
]

environment_topics = [
    ("deforestation", "Deforestation, the large-scale removal of forests, has severe environmental consequences. Forests act as carbon sinks, absorbing carbon dioxide from the atmosphere and mitigating climate change. Their destruction releases stored carbon, contributes to biodiversity loss, and disrupts water cycles. In the Amazon, for example, large-scale clearing for agriculture and ranching threatens one of the world's most biodiverse ecosystems. Addressing deforestation requires sustainable land management policies, support for indigenous land rights, and economic alternatives for local communities."),
    ("ocean pollution", "Ocean pollution poses a grave threat to marine ecosystems and the billions of people who depend on the sea for food and livelihoods. Major pollutants include plastic waste, agricultural runoff containing nitrogen and phosphorus that creates dead zones, oil spills, and industrial chemicals. Microplastics have been found in the deepest ocean trenches and in the bodies of marine organisms. Addressing ocean pollution requires international agreements, improved waste management systems, stricter regulations on industrial discharge, and a transition away from single-use plastics."),
    ("biodiversity", "Biodiversity refers to the variety of life on Earth at all levels, from genes to ecosystems. It encompasses the estimated 8.7 million species of plants, animals, fungi, and microorganisms, along with the ecosystems they form. High biodiversity ensures ecosystem resilience, provides resources for medicine and agriculture, and maintains natural processes like pollination and water purification. Human activities — including habitat destruction, pollution, invasive species, and climate change — are driving the sixth mass extinction, with species disappearing at rates far exceeding natural background levels."),
    ("water scarcity", "Water scarcity affects more than 40% of the global population and is projected to worsen as climate change alters precipitation patterns and increases evaporation. It occurs when the demand for fresh water exceeds the available supply in a region. Agriculture accounts for approximately 70% of global freshwater use, making improved irrigation efficiency critical. Solutions to water scarcity include desalination, water recycling, rainwater harvesting, and demand management through pricing and regulation. Equitable access to safe drinking water is recognized as a fundamental human right."),
    ("air quality", "Air quality refers to the condition of the air with respect to the concentration of pollutants that affect human health and the environment. Major air pollutants include particulate matter, nitrogen oxides, sulfur dioxide, carbon monoxide, and volatile organic compounds, largely produced by vehicles, industry, and agriculture. Poor air quality causes respiratory and cardiovascular diseases and is linked to millions of premature deaths annually. Urban areas are particularly affected, and improvements in public transportation, industrial regulation, and clean energy adoption are key strategies for improving air quality."),
]

all_topics = science_topics + social_topics + technology_topics + health_topics + environment_topics

# ── Sentence starters for variation ─────────────────────────────────────────
intros = [
    "", "", "",  # empty = just use topic text
    "To understand this topic fully, it is important to consider the key concepts involved. ",
    "In today's rapidly evolving world, this subject has become increasingly relevant. ",
    "This is a multifaceted topic that requires careful examination from multiple perspectives. ",
    "Let us explore the fundamental aspects of this important subject in a structured manner. ",
    "A comprehensive understanding of this topic requires us to examine both theoretical and practical dimensions. ",
]

outros = [
    "",  # no outro
    " In conclusion, a deeper understanding of this subject is essential for informed decision-making.",
    " It is evident that this topic will continue to shape our world in significant ways going forward.",
    " Continued research and public awareness are crucial to addressing the challenges in this field.",
    " Understanding these principles is foundational to making progress in this important area.",
]

generated = 0
idx = start_idx
needed = TARGET - (start_idx - 1)

print(f"Starting from index {start_idx}, need to generate {needed} files to reach {TARGET} total AI samples...")

while idx <= TARGET:
    topic_name, base_text = random.choice(all_topics)
    intro = random.choice(intros)
    outro = random.choice(outros)
    
    # Build the chunk
    chunk = intro + base_text + outro
    
    # Occasionally add a transition sentence
    if random.random() < 0.3:
        transitions = [
            f" Furthermore, it is worth noting that the implications of {topic_name} extend beyond the immediate context.",
            f" Additionally, ongoing developments in this field continue to expand our understanding of {topic_name}.",
            f" It is also important to consider the broader societal and environmental implications associated with {topic_name}.",
            f" Recent studies have further confirmed the significance of these factors in relation to {topic_name}.",
        ]
        chunk += random.choice(transitions)

    out_path = os.path.join(output_dir, f"{idx}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(chunk)
    
    idx += 1
    generated += 1
    if generated % 200 == 0:
        print(f"  Generated {generated} files (up to index {idx-1})...")

print(f"\nDone! Generated {generated} new AI samples.")
print(f"Total AI samples now: {idx - 1}")
