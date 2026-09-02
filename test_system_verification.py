import requests
import os
import glob
import time
import json

BASE_URL = "http://localhost:5000"

def run_tests():
    print("=" * 60)
    print("      AUTHGUARD MULTI-MODAL MODEL VERIFICATION SUITE")
    print("=" * 60)

    # 1. Health Check
    print("\n[1/6] Testing Server Health & Connectivity...")
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"  -> Health Status: {r.status_code} | Response: {r.json()}")
        assert r.status_code == 200, "Health check failed"
    except Exception as e:
        print(f"  -> FAILED: {e}")
        return

    # 2. Text Model Verification
    print("\n[2/6] Testing Text AI Detection Engine (TF-IDF + Heuristics + Language)...")
    human_text = "The solar system consists of the Sun and the objects that orbit it, either directly or indirectly."
    ai_text = "In today's fast-paced digital era, it is of paramount importance to delve into the intricate nuances of sustainable development to foster a holistic paradigm shift."
    
    # Test Human Text
    r_human = requests.post(f"{BASE_URL}/predict_text", json={"text": human_text})
    print(f"  -> Human Text Test Status: {r_human.status_code}")
    if r_human.status_code == 200:
        d = r_human.json()
        print(f"     Verdict: {d.get('prediction')} | Prob Human: {d.get('prob_human')}% | Confidence: {d.get('confidence')}%")

    # Test AI Text
    r_ai = requests.post(f"{BASE_URL}/predict_text", json={"text": ai_text})
    print(f"  -> AI Text Test Status: {r_ai.status_code}")
    if r_ai.status_code == 200:
        d = r_ai.json()
        print(f"     Verdict: {d.get('prediction')} | Prob AI: {d.get('prob_ai')}% | Confidence: {d.get('confidence')}%")

    # 3. Image Model Verification (ConvNeXt Pro + ViT + CNN Ensemble + FFT + ELA)
    print("\n[3/6] Testing Image Forensics Engine (ConvNeXt Pro + ViT Ensemble + FFT + ELA)...")
    fake_images = glob.glob("dataset_image/fake/*.jpg") + glob.glob("dataset_image/fake/*.png")
    real_images = glob.glob("dataset_image/real/*.jpg") + glob.glob("dataset_image/real/*.png")

    if fake_images:
        img_path = fake_images[0]
        print(f"  -> Testing AI Image sample: {os.path.basename(img_path)}")
        with open(img_path, 'rb') as f:
            r_img = requests.post(f"{BASE_URL}/predict_image", files={"image": f})
        print(f"     Status: {r_img.status_code}")
        if r_img.status_code == 200:
            d = r_img.json()
            forensics = d.get('forensic_data', {})
            print(f"     Verdict: {d.get('prediction')} | Confidence: {d.get('confidence')}%")
            print(f"     Ensemble Scores -> ConvNeXt Pro: {forensics.get('convnext_prob_human')}% | ViT: {forensics.get('vit_prob_human')}% | FFT: {forensics.get('fourier_prob_human')}%")

    if real_images:
        img_path = real_images[0]
        print(f"  -> Testing Real Image sample: {os.path.basename(img_path)}")
        with open(img_path, 'rb') as f:
            r_img = requests.post(f"{BASE_URL}/predict_image", files={"image": f})
        print(f"     Status: {r_img.status_code}")
        if r_img.status_code == 200:
            d = r_img.json()
            forensics = d.get('forensic_data', {})
            print(f"     Verdict: {d.get('prediction')} | Confidence: {d.get('confidence')}%")
            print(f"     Ensemble Scores -> ConvNeXt Pro: {forensics.get('convnext_prob_human')}% | ViT: {forensics.get('vit_prob_human')}% | FFT: {forensics.get('fourier_prob_human')}%")

    # 4. Voice / Audio Model Verification
    print("\n[4/6] Testing Voice / Audio Deepfake Classifier...")
    audio_files = glob.glob("dataset/ai/*.mp3") + glob.glob("*.wav")
    if audio_files:
        audio_path = audio_files[0]
        print(f"  -> Testing Audio sample: {os.path.basename(audio_path)}")
        with open(audio_path, 'rb') as f:
            r_audio = requests.post(f"{BASE_URL}/predict_voice", files={"audio": f})
        print(f"     Status: {r_audio.status_code}")
        if r_audio.status_code == 200:
            d = r_audio.json()
            print(f"     Verdict: {d.get('prediction')} | Prob Real: {d.get('prob_real')}% | Prob Fake: {d.get('prob_fake')}% | Confidence: {d.get('confidence')}%")
    else:
        print("  -> No audio test file found.")

    # 5. Video Deepfake Detection Verification
    print("\n[5/6] Testing Video Deepfake Pipeline (Frame Extraction + Multi-frame Scan)...")
    video_files = glob.glob("dataset/human/*.mp4")
    if video_files:
        video_path = video_files[0]
        print(f"  -> Submitting Video Task: {os.path.basename(video_path)}")
        with open(video_path, 'rb') as f:
            r_vid = requests.post(f"{BASE_URL}/predict_video", files={"video": f})
        print(f"     Submission Status: {r_vid.status_code} | Task ID: {r_vid.json().get('task_id')}")
        if r_vid.status_code == 202:
            task_id = r_vid.json().get('task_id')
            print("     Waiting for asynchronous video analysis completion...")
            for _ in range(15):
                time.sleep(2)
                r_status = requests.get(f"{BASE_URL}/video_status/{task_id}")
                st = r_status.json()
                if st.get('status') == 'COMPLETED' or 'prediction' in st:
                    print(f"     ✅ Video Analysis Complete -> Verdict: {st.get('prediction')} | Confidence: {st.get('confidence')}%")
                    break
                elif st.get('status') == 'FAILED':
                    print(f"     ❌ Video Analysis Failed: {st.get('error')}")
                    break
                else:
                    print(f"     Status: {st.get('status')}...")
    else:
        print("  -> No video test file found.")

    # 6. Watermark Creation & Verification
    print("\n[6/6] Testing Cryptographic Watermark System...")
    dummy_img = fake_images[0] if fake_images else None
    if dummy_img:
        with open(dummy_img, 'rb') as f:
            r_create = requests.post(f"{BASE_URL}/create_watermark", files={"image": f})
        if r_create.status_code == 200:
            watermarked_bytes = r_create.content
            print("     ✅ Watermark successfully created and embedded.")
            r_verify = requests.post(f"{BASE_URL}/verify_watermark", files={"image": ("protected.png", watermarked_bytes, "image/png")})
            print(f"     Watermark Verification Status: {r_verify.status_code} | Response: {r_verify.json()}")

    print("\n" + "=" * 60)
    print("         ALL MODEL VERIFICATION TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
