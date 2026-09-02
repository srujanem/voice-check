import os
import io
import asyncio
import tarfile
import urllib.request
import edge_tts
from tqdm import tqdm

DATASET_DIR = 'dataset'
HUMAN_DIR = os.path.join(DATASET_DIR, 'human')
AI_DIR = os.path.join(DATASET_DIR, 'ai')

os.makedirs(HUMAN_DIR, exist_ok=True)
os.makedirs(AI_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. AI VOICE SYNTHESIS (Edge Neural TTS)
# -------------------------------------------------------------
VOICES = [
    'en-US-GuyNeural',
    'en-US-JennyNeural',
    'en-US-AriaNeural',
    'en-US-DavisNeural',
    'en-US-AmberNeural',
    'en-US-AndrewNeural',
    'en-US-BrianNeural',
    'en-US-ChristopherNeural',
    'en-US-EmmaNeural',
    'en-US-EricNeural',
    'en-US-MichelleNeural',
    'en-US-RogerNeural',
    'en-GB-SoniaNeural',
    'en-GB-RyanNeural',
    'en-GB-LibbyNeural',
    'en-AU-NatashaNeural',
    'en-AU-WilliamNeural',
    'en-CA-ClaraNeural',
    'en-CA-LiamNeural',
    'en-IN-NeerjaNeural',
    'en-IN-PrabhatNeural',
]

PHRASES = [
    'Artificial intelligence is transforming modern computer vision and natural language processing.',
    'The weather forecast predicts light rain and moderate temperatures across the region today.',
    'Please make sure your seatbelts are fastened securely before takeoff and during turbulence.',
    'Deep learning models require balanced training datasets with clean audio samples.',
    'The financial market experienced significant gains following the quarterly economic report.',
    'Could you please explain the difference between convolutional neural networks and transformers?',
    'Every morning, she enjoys a hot cup of black coffee while reading the daily newspaper.',
    'The autonomous vehicle successfully navigated through heavy downtown traffic without incident.',
    'Recent advances in audio forensic analysis allow us to detect cloned speech patterns.',
    'Biometric verification systems rely on acoustic frequency analysis to confirm identity.',
    'The library offers thousands of digital books and research journals for all registered students.',
    'Renewable energy sources such as solar and wind power are becoming increasingly affordable.',
    'Cybersecurity experts recommend enabling two-factor authentication on all sensitive accounts.',
    'The chef prepared a gourmet meal featuring fresh organic vegetables and hand-made pasta.',
    'Voice authentication is widely used across banking applications to prevent identity fraud.',
    'The satellite captured high-resolution imagery of the coastal erosion and ocean currents.',
    'Machine learning algorithms can identify subtle mathematical anomalies in synthetic voice files.',
    'He decided to take an evening walk through the park to clear his mind after work.',
    'The international conference gathered researchers from over forty countries to discuss innovation.',
    'Effective communication requires active listening and clear articulation of ideas.',
    'The museum will host a special exhibition showcasing historic artifacts and photography.',
    'High frequency spectral components often reveal discrepancies in synthetic speech generation.',
    'They scheduled a follow-up meeting for next Tuesday to review the project milestones.',
    'The software update includes several performance enhancements and critical security patches.',
    'Clean audio signals with minimal background interference yield the highest classification accuracy.'
]

async def generate_ai_clip(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

async def build_ai_dataset(target_count=250):
    existing = len([f for f in os.listdir(AI_DIR) if f.endswith(('.mp3', '.wav', '.flac'))])
    needed = target_count - existing
    if needed <= 0:
        print(f'[AI Voices] Already have {existing} files in {AI_DIR}. Skipping generation.')
        return

    print(f"\n[AI Voices] Generating {needed} diverse AI voice samples...")
    clip_idx = existing + 1
    pbar = tqdm(total=needed, desc='Synthesizing AI Audio')
    
    idx = 0
    while clip_idx <= target_count:
        voice = VOICES[idx % len(VOICES)]
        phrase = PHRASES[idx % len(PHRASES)]
        out_file = os.path.join(AI_DIR, f'ai_sample_{clip_idx:04d}.mp3')
        try:
            await generate_ai_clip(phrase, voice, out_file)
            clip_idx += 1
            pbar.update(1)
        except Exception as e:
            await asyncio.sleep(0.5)
        idx += 1
    pbar.close()
    print(f'[AI Voices] Total AI samples ready: {len(os.listdir(AI_DIR))}')

# -------------------------------------------------------------
# 2. HUMAN VOICE HARVESTING (LibriSpeech OpenSLR Stream)
# -------------------------------------------------------------
def build_human_dataset(target_count=250):
    existing = len([f for f in os.listdir(HUMAN_DIR) if f.endswith(('.mp3', '.wav', '.flac'))])
    needed = target_count - existing
    if needed <= 0:
        print(f'[Human Voices] Already have {existing} files in {HUMAN_DIR}. Skipping download.')
        return

    print(f"\n[Human Voices] Streaming {needed} real human voice recordings from LibriSpeech...")
    url = 'https://www.openslr.org/resources/12/dev-clean.tar.gz'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    pbar = tqdm(total=needed, desc='Harvesting Human Audio')
    clip_idx = existing + 1

    try:
        with urllib.request.urlopen(req, timeout=30) as stream:
            with tarfile.open(fileobj=stream, mode='r|gz') as tar:
                for member in tar:
                    if member.isfile() and member.name.endswith('.flac'):
                        f_data = tar.extractfile(member).read()
                        out_path = os.path.join(HUMAN_DIR, f'human_sample_{clip_idx:04d}.flac')
                        with open(out_path, 'wb') as out_f:
                            out_f.write(f_data)
                        
                        clip_idx += 1
                        pbar.update(1)
                        if clip_idx > target_count:
                            break
    except Exception as e:
        print(f'[Human Voices] Download stream stopped: {e}')
    finally:
        pbar.close()

    print(f'[Human Voices] Total Human samples ready: {len(os.listdir(HUMAN_DIR))}')

# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
if __name__ == '__main__':
    print('=' * 60)
    print('  AUTONOMOUS DATASET BUILDER: VOICE DEEPFAKE DETECTION')
    print('=' * 60)
    
    build_human_dataset(target_count=250)
    asyncio.run(build_ai_dataset(target_count=250))

    print("\n" + "=" * 60)
    print("  DATASET GENERATION COMPLETE!")
    print(f"  Human Samples: {len(os.listdir(HUMAN_DIR))}")
    print(f"  AI Samples:    {len(os.listdir(AI_DIR))}")
    print("=" * 60)
    print("\nReady to train! Run: python train.py")
