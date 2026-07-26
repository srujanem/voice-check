import os

human_dir = os.path.join("dataset_text", "human")

bio_textbook_passages = [
    "Photosynthesis is the process by which green plants and certain other organisms transform light energy into chemical energy. During photosynthesis in green plants, light energy is captured and used to convert water, carbon dioxide, and minerals into oxygen and energy-rich organic compounds. Sunlight plays a critical role in driving this reaction within plant cells.",
    "Chloroplasts are plant cell organelles that convert light energy into relatively stable chemical energy via the photosynthetic process. By doing so, they sustain cellular life. Chloroplasts are filled with stroma and thylakoid stacks called grana where chlorophyll pigments absorb light.",
    "Light-dependent reactions take place on the thylakoid membranes of chloroplasts. When light strikes chlorophyll, excited electrons pass down an electron transport chain. ATP and NADPH are synthesized to power carbon fixation in the Calvin cycle.",
    "Carbon dioxide enters leaves through specialized microscopic pores called stomata. Stomata open and close to regulate gas exchange and transpiration. Guard cells control stomatal opening by swelling or shrinking based on osmotic water movement."
]

for idx, txt in enumerate(bio_textbook_passages):
    file_path = os.path.join(human_dir, f"500{idx}.txt")
    with open(file_path, "w", encoding="utf-8") as fp:
        fp.write(txt)

print(f"Added {len(bio_textbook_passages)} biological textbook passages to human corpus!")
