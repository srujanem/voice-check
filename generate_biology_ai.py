"""Generate 1000 AI samples specifically about Biology/Science topics
to help the model distinguish between human-written textbooks and AI-generated biology text.
"""
import os, random

output_dir = r"c:\voice-check\dataset_text\ai"
start_idx = 5001
target = 6000

biology_topics = [
    ("Photosynthesis", "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy. It occurs in two main stages: the light-dependent reactions and the Calvin cycle. Chlorophyll absorbs light primarily in the red and blue regions of the electromagnetic spectrum. The overall equation involves carbon dioxide and water reacting to form glucose and oxygen. This process is the ultimate source of energy for nearly all life on Earth and is responsible for maintaining atmospheric oxygen levels."),
    ("Cell division", "Cell division is the process by which a parent cell divides into two or more daughter cells. In eukaryotes, there are two distinct types of cell division: a vegetative division called mitosis, and a reproductive division called meiosis. Mitosis results in two genetically identical daughter cells, maintaining the diploid chromosome number. Meiosis involves two rounds of division, producing four haploid gametes with genetic variation due to crossing over and independent assortment. Proper regulation of the cell cycle is crucial to prevent uncontrolled proliferation, which characterizes cancer."),
    ("Genetics", "Genetics is the study of genes, genetic variation, and heredity in living organisms. Gregor Mendel's foundational work with pea plants established the laws of Mendelian inheritance, demonstrating that traits are passed from parents to offspring in discrete units. DNA, the molecular basis of heredity, consists of a double helix composed of four nucleotide bases. Genes provide the instructions for synthesizing proteins through the processes of transcription and translation. Mutations in the DNA sequence can introduce new genetic variations, which are the raw material for evolutionary change."),
    ("Nervous system", "The human nervous system is a complex network of neurons and glial cells that coordinates the body's voluntary and involuntary actions. It is divided into the central nervous system, comprising the brain and spinal cord, and the peripheral nervous system, which includes all other neural tissue. Neurons communicate via electrical impulses called action potentials and chemical signals called neurotransmitters crossing synapses. The autonomic nervous system further subdivides into the sympathetic (fight or flight) and parasympathetic (rest and digest) branches, maintaining homeostasis across physiological systems."),
    ("Endocrine system", "The endocrine system is a chemical messenger system consisting of feedback loops of hormones released by internal glands directly into the circulatory system. Major endocrine glands include the hypothalamus, pituitary, thyroid, parathyroids, adrenals, pineal body, and the reproductive organs. Hormones regulate a vast array of physiological processes including metabolism, growth and development, tissue function, sleep, and mood. Unlike the nervous system, which operates via rapid electrical signals, the endocrine system's effects are generally slower to initiate but longer-lasting in duration."),
    ("Evolution", "Biological evolution is the change in the heritable characteristics of biological populations over successive generations. Natural selection, a key mechanism of evolution formulated by Charles Darwin, posits that individuals with traits advantageous to their environment are more likely to survive and reproduce. Over time, this differential reproductive success leads to adaptation and speciation. Evidence for evolution comes from diverse fields including paleontology, comparative anatomy, embryology, and molecular biology. Genetic drift and gene flow also contribute significantly to evolutionary changes in populations."),
    ("Ecology", "Ecology is the scientific study of the interactions among organisms and their biophysical environment. An ecosystem consists of all the living organisms (biotic factors) in a given area interacting with the non-living physical environment (abiotic factors). Energy flows through ecosystems unilaterally, entering primarily as sunlight and dissipating as heat, while nutrients are continuously cycled. Population dynamics, community interactions such as predation and symbiosis, and the impacts of human activities on biodiversity are central themes in ecological research."),
    ("Digestive system", "The digestive system breaks down food into simple nutrients such as carbohydrates, fats, and proteins that can be absorbed into the bloodstream. Mechanical digestion begins in the mouth with chewing, while chemical digestion involves enzymes like amylase and pepsin. The stomach uses gastric acid to further break down proteins. The small intestine is the primary site for nutrient absorption, utilizing villi and microvilli to maximize surface area. The large intestine primarily absorbs water and forms solid waste for excretion."),
    ("Cardiovascular system", "The cardiovascular system, or circulatory system, comprises the heart, blood vessels, and blood. Its primary function is to transport oxygen, nutrients, hormones, and cellular waste products throughout the body. The heart, a muscular organ, functions as a dual pump, driving blood through the pulmonary circuit to the lungs for oxygenation and the systemic circuit to the rest of the body. Arteries carry blood away from the heart under high pressure, while veins return blood to the heart, often utilizing valves to prevent backflow."),
    ("Respiratory system", "The human respiratory system facilitates the exchange of gases between the body and the environment. Air enters through the nasal cavity, travels down the trachea, and branches into bronchi and bronchioles before reaching the alveoli in the lungs. Oxygen diffuses across the thin alveolar walls into the surrounding capillaries, binding to hemoglobin in red blood cells. Simultaneously, carbon dioxide diffuses from the blood into the alveoli to be exhaled. The diaphragm, a dome-shaped muscle, drives the ventilation process by altering thoracic volume."),
]

intros = [
    "In the context of biological sciences, ",
    "When examining the complex mechanisms of life, ",
    "One of the fundamental concepts in biology is that ",
    "From a scientific perspective, ",
    "Modern biological understanding dictates that ",
]

outros = [
    " These processes highlight the intricate complexity and efficiency of biological systems.",
    " Continued research in this area promises to yield further insights into the fundamental mechanisms of life.",
    " This topic remains a vibrant area of study with significant implications for medicine and biotechnology.",
    " Understanding these dynamics is essential for addressing many of the challenges in contemporary biology.",
]

generated = 0
for idx in range(start_idx, target + 1):
    topic, base_text = random.choice(biology_topics)
    intro = random.choice(intros)
    outro = random.choice(outros)
    
    text = intro + base_text + outro
    
    out_path = os.path.join(output_dir, f"{idx}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    generated += 1
    if generated % 200 == 0:
        print(f"  Generated {generated} files (up to index {idx})...")

print(f"\nDone! Generated {generated} new AI biology samples (files {start_idx}-{target}).")
print(f"Total AI samples now: {target}")
