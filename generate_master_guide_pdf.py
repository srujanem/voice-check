import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "AuthGuard / VoiceCheck — Master Architecture & Interview Defense Guide")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, text)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — PREPARED FOR TECHNICAL INTERVIEW DEFENSE")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.restoreState()

def build_pdf(filename="AuthGuard_Master_Architecture_and_Interview_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0f172a")
    c_accent = colors.HexColor("#0284c7")
    c_secondary = colors.HexColor("#0369a1")
    c_dark = colors.HexColor("#1e293b")
    c_light = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#e2e8f0")

    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    
    style_cover_sub = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=c_accent,
        spaceAfter=12
    )

    style_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_secondary,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=4
    )

    style_body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )

    style_callout = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0369a1")
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    story = []

    story.append(Paragraph("AUTHGUARD / VOICECHECK", style_cover_title))
    story.append(Paragraph("Full Technical Architecture, Signal Forensics & Interview Defense Master Guide", style_cover_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceAfter=8))

    exec_summary_text = "<b>System Overview:</b> AuthGuard is an enterprise-grade multimodal synthetic media detection platform engineered to identify deepfake images, cloned human voices, AI-generated text (ChatGPT/Gemini/Claude), and manipulated videos. Built with a hybrid cloud architecture combining a lightweight Vercel Edge frontend with a self-healing on-premise Python WSGI engine, the platform executes both deep neural network inference (EfficientNet, Transformers) and classical physical signal processing (2D-FFT VAE Grid Forensics, Error Level Analysis, MFCC acoustic modeling)."
    summary_table = Table([[Paragraph(exec_summary_text, style_callout)]], colWidths=[7.0 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#bae6fd")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. The 30-Second Elevator Pitch (Memorize This)", style_h1))
    pitch_text = "<i>\"I designed and built <b>AuthGuard</b>, a multimodal AI forensics platform that detects synthetic media across four distinct domains: images, voice, text, and video. Unlike naive classifiers that rely solely on black-box neural networks, AuthGuard utilizes a <b>dual-layer ensemble</b> that pairs deep learning with physical signal forensics—including 2D Fast Fourier Transform analysis to detect high-frequency VAE grid artifacts in modern diffusion models, and Mel-Frequency Cepstral Coefficients to spot vocoder phase distortions in synthetic audio. The platform is deployed on a hybrid cloud architecture with sub-4-second inference latencies.\"</i>"
    story.append(Paragraph(pitch_text, style_body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. System Architecture & Tech Stack Breakdown", style_h1))
    story.append(Paragraph("AuthGuard is designed as a decoupled <b>Hybrid Cloud System</b> to host multi-gigabyte machine learning models without incurring heavy recurring GPU cloud hosting costs.", style_body))
    
    arch_data = [
        [Paragraph("Tier / Layer", style_table_header), Paragraph("Technologies", style_table_header), Paragraph("Key Responsibilities & Architectural Design", style_table_header)],
        [
            Paragraph("<b>Frontend Edge</b>", style_table_cell),
            Paragraph("HTML5, CSS3, Vanilla JS (ES6+), Vercel Edge CDN", style_table_cell),
            Paragraph("Zero-dependency high-speed static delivery, interactive forensic UI, Grad-CAM visualizer, client-side auto-discovery failover (server-config.js).", style_table_cell)
        ],
        [
            Paragraph("<b>Ingress & Tunnel</b>", style_table_cell),
            Paragraph("Cloudflare Tunnel (cloudflared), CORS Proxy", style_table_cell),
            Paragraph("Encrypted reverse tunnel routing browser traffic to dedicated compute; automated DNS registration with sub-3s health checking.", style_table_cell)
        ],
        [
            Paragraph("<b>WSGI Web Server</b>", style_table_cell),
            Paragraph("Waitress WSGI (Multi-threaded Production Server)", style_table_cell),
            Paragraph("Replaces development servers to prevent Python Global Interpreter Lock (GIL) deadlocks under heavy OpenMP/TensorFlow execution.", style_table_cell)
        ],
        [
            Paragraph("<b>Backend Core</b>", style_table_cell),
            Paragraph("Python 3, Flask (Blueprints), Flask-Limiter", style_table_cell),
            Paragraph("Modular microservices routing (/predict_image, /predict_voice, /predict_text, /predict_video, /api/infer), rate limiting, JWT auth.", style_table_cell)
        ],
        [
            Paragraph("<b>AI / ML Engine</b>", style_table_cell),
            Paragraph("TensorFlow, PyTorch, Transformers, Scikit-learn", style_table_cell),
            Paragraph("EfficientNet-B0 CNN, HuggingFace Sequence Classification, Grad-CAM explainability, and multi-model feature blending.", style_table_cell)
        ],
        [
            Paragraph("<b>Signal Forensics</b>", style_table_cell),
            Paragraph("OpenCV, Librosa, NumPy, SciPy (FFT / ELA)", style_table_cell),
            Paragraph("2D-FFT Laplacian spectral analysis, Error Level Analysis (ELA), YCbCr chrominance variance, MFCC 40-band acoustic extraction.", style_table_cell)
        ],
        [
            Paragraph("<b>Process Daemon</b>", style_table_cell),
            Paragraph("Python Watchdog, Win32 WMI Detachment", style_table_cell),
            Paragraph("24/7 background self-healing monitor that automatically respawns crashed processes and updates dynamic DNS records.", style_table_cell)
        ]
    ]

    t_arch = Table(arch_data, colWidths=[1.1 * inch, 1.8 * inch, 4.1 * inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Deep Dive into the 4 Detection Modules (The ML & Physics Core)", style_h1))
    
    story.append(Paragraph("A. Image Forensics Engine: Dual-Layer Spatial + Frequency Ensemble", style_h2))
    story.append(Paragraph("""
    Standard deepfake detectors fail on state-of-the-art diffusion models (Midjourney v6, Dall-E 3, Gemini Imagen) because they only analyze spatial pixels. AuthGuard implements a <b>mathematical dual-layer defense</b>:<br/>
    <b>1. Spatial Deep Learning + Grad-CAM Explainability:</b> Uses a fine-tuned EfficientNet-B0 backbone to extract semantic high-level features. Integrated with <b>Gradient-weighted Class Activation Mapping (Grad-CAM)</b>, the engine calculates the gradient of the predicted class score with respect to the feature maps of the final convolutional layer to generate an XAI heatmap showing manipulated areas.<br/>
    <b>2. 2D Fast Fourier Transform (2D-FFT) & VAE Grid Analysis:</b> Latent Diffusion Models generate images in compressed latent space and decode them via a <b>Variational Autoencoder (VAE)</b> in 8x8 pixel blocks, leaving an imperceptible high-frequency grid. AuthGuard passes the image through a Laplacian high-pass filter, computes 2D-FFT, zeros low frequencies, and calculates the <b>Max-to-Mean Ratio</b> of spectral projections. If ratio &gt; <b>1.95</b>, it overrides CNN predictions to catch zero-day diffusion deepfakes.<br/>
    <b>3. Error Level Analysis (ELA):</b> Resaves the image at 90% JPEG quality and analyzes the difference matrix to spot foreign compression artifacts.
    """, style_body))

    story.append(Paragraph("B. Voice Cloning Detection Engine: Acoustic Vocoder Fingerprinting", style_h2))
    story.append(Paragraph("""
    Neural text-to-speech vocoders (ElevenLabs, Tortoise-TTS) generate realistic speech but leave distinct spectral phase irregularities. AuthGuard extracts <b>40 Mel-Frequency Cepstral Coefficients (MFCCs)</b> matching the human psychoacoustic scale, calculates <b>Spectral Centroid & Rolloff</b> to detect synthetic frequency drops, measures <b>Zero-Crossing Rate (ZCR)</b> to expose artificial breath sounds, and analyzes <b>Chroma STFT</b> for robotic pitch flattening.
    """, style_body))

    story.append(Paragraph("C. Text / LLM Content Detection Engine: Perplexity & Burstiness", style_h2))
    story.append(Paragraph("""
    Distinguishes human prose from LLMs (ChatGPT, Claude, Gemini) through statistical linguistics:<br/>
    &bull; <b>Perplexity (Surprise Factor):</b> Measures how predictable the next token is. LLMs select mathematically probable tokens (low, uniform perplexity); humans introduce creative vocabulary (high perplexity).<br/>
    &bull; <b>Burstiness (Structural Variance):</b> Measures the standard deviation of sentence lengths and syntactic cadence. AI generates uniform sentences (low burstiness); humans alternate short and long sentences (high burstiness).
    """, style_body))

    story.append(Paragraph("D. Video & Cryptographic Watermark Engines", style_h2))
    story.append(Paragraph("""
    &bull; <b>Video Deepfake Analyzer:</b> Samples video frames temporally via OpenCV (cv2.VideoCapture), executes batch image forensics, and applies sliding-window temporal consistency aggregation.<br/>
    &bull; <b>Cryptographic Watermarking:</b> Injects tamper-evident digital signatures into authentic exports, enabling instant O(1) verification that bypasses heavy neural inference.
    """, style_body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Key Engineering Challenges Solved (Your Interview Stories)", style_h1))
    story.append(Paragraph("Interviewer: <i>\"Tell me about a difficult technical challenge you encountered and how you solved it.\"</i>", style_body))

    challenges = [
        (
            "Challenge 1: Zero-Shot Failure on Modern Diffusion Models (Gemini / Midjourney)",
            "<b>Situation:</b> The CNN classified a photorealistic Gemini-generated image as 95% Human because the model was trained on older GAN datasets and lacked modern diffusion artifacts.<br/>"
            "<b>Action:</b> Researched Latent Diffusion Model architectures and identified their 8x8 VAE spatial decoding signature. Engineered a 2D-FFT Laplacian spectral analysis pipeline in NumPy/OpenCV that detects periodic grid spikes in high-frequency projections.<br/>"
            "<b>Result:</b> The VAE detector identified the Gemini image with a spectral spike ratio of 2.19 (threshold 1.95), successfully overriding the CNN and correctly classifying it as AI-generated with 85% confidence."
        ),
        (
            "Challenge 2: Python GIL Deadlocks in Multi-Threaded WSGI Environment",
            "<b>Situation:</b> The Flask development server froze and threw 60-second timeouts / \"Failed to fetch\" errors whenever concurrent requests or heavy image inferences were triggered.<br/>"
            "<b>Action:</b> Diagnosed that Flask default server deadlocked under Python Global Interpreter Lock (GIL) and OpenMP thread contention during simultaneous TensorFlow Grad-CAM calculations. Migrated backend to production Waitress WSGI and tuned thread isolation.<br/>"
            "<b>Result:</b> Inference response latency dropped from over 40 seconds to under 4.5 seconds with zero server freezes or memory leaks."
        ),
        (
            "Challenge 3: Cloudflare IPv6 Origin Resolution (530 Origin Error)",
            "<b>Situation:</b> The Cloudflare reverse tunnel returned \"530 Origin Unreachable\" errors when routing browser requests from the Vercel frontend to the local backend.<br/>"
            "<b>Action:</b> Traced network packets and discovered that on Windows, \"localhost\" resolved to IPv6 (::1), while the Flask server was bound strictly to IPv4 (127.0.0.1). Updated cloudflared configurations to bind directly to IPv4 loopback and configured Flask-CORS headers.<br/>"
            "<b>Result:</b> Flawless cross-origin communication between authguard.vercel.app and the local compute engine."
        ),
        (
            "Challenge 4: Vercel 100MB Deployment Constraint (Hybrid Cloud Architecture)",
            "<b>Situation:</b> Deployments to Vercel failed due to the platform 100MB project build limit, as multi-gigabyte dataset folders and heavy model binaries were accidentally tracked in git.<br/>"
            "<b>Action:</b> Architected a Hybrid Cloud solution: decoupled the static UI from heavy compute, executed git cache pruning (git rm --cached), established strict .vercelignore rules, and routed inference requests over secure tunnels to local GPU hardware.<br/>"
            "<b>Result:</b> Reduced deployment bundle from 476MB to 23.3MB (95% reduction), achieving instant Vercel edge deployment."
        )
    ]

    for title, text in challenges:
        c_table = Table(
            [[Paragraph(f"<b>{title}</b>", style_body_bold)], [Paragraph(text, style_body)]],
            colWidths=[7.0 * inch]
        )
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('BACKGROUND', (0,1), (-1,1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, c_border),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 8))

    story.append(Paragraph("5. Ready-to-Use Resume Section", style_h1))
    resume_text = """
    <b>AuthGuard — Multimodal AI Deepfake & Synthetic Media Forensic Suite</b><br/>
    <i>Tech Stack: Python, Flask, Waitress WSGI, TensorFlow, PyTorch, OpenCV, Librosa, NumPy, JavaScript, Vercel</i><br/>
    &bull; Architected a multimodal synthetic media detection platform analyzing deepfake images, cloned voice audio, AI text, and video files with sub-4s latency.<br/>
    &bull; Implemented a dual-layer image forensics pipeline combining fine-tuned EfficientNet-B0 with 2D Fast Fourier Transform (FFT) high-frequency analysis and Error Level Analysis (ELA) to detect latent VAE grid artifacts.<br/>
    &bull; Engineered explainable AI (XAI) capabilities using Grad-CAM heatmaps via TensorFlow GradientTape to visualize manipulated image regions for end users.<br/>
    &bull; Built an acoustic feature extraction pipeline using Librosa (MFCCs, Spectral Centroids, Zero-Crossing Rate) to identify neural vocoder phase artifacts in voice clones.<br/>
    &bull; Deployed a hybrid cloud infrastructure with an Edge-hosted Vercel frontend communicating with a self-healing on-premise WSGI backend via automated Cloudflare tunnels and custom Python watchdog services.
    """
    resume_table = Table([[Paragraph(resume_text, style_body)]], colWidths=[7.0 * inch])
    resume_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#faf5ff")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#e9d5ff")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(resume_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("6. Top 10 Technical Interview Questions & Model Answers", style_h1))

    qa_list = [
        ("Q1: Why combine Deep Learning with Classical Signal Processing (FFT/ELA)?",
         "Pure deep learning models suffer from distribution shifts—when a new generator (like Midjourney v6) releases, the CNN has never seen its style and fails. Classical signal processing operates on physical invariants: camera optical physics (ELA) and mathematical autoencoder sampling artifacts (2D-FFT). Combining both provides robust zero-shot detection."),
        ("Q2: How does Grad-CAM explainability work?",
         "Grad-CAM computes the gradient of the winning class score with respect to the feature activation maps in the final convolutional layer. These gradients are globally pooled to create importance weights, which linearly combine the feature maps into a 2D spatial heatmap showing the exact pixel regions that influenced the decision."),
        ("Q3: What is the purpose of MFCCs in voice deepfake detection?",
         "Mel-Frequency Cepstral Coefficients represent the short-term power spectrum of sound, mapped to the non-linear human hearing frequency curve. Neural vocoders struggle to perfectly model the subtle vocal tract transitions and turbulent phase noise of real vocal cords, which shows up as statistical anomalies across the 40 MFCC bands."),
        ("Q4: How do Perplexity and Burstiness detect AI-written text?",
         "Perplexity measures the log-likelihood of token sequences. Because LLMs sample from high-probability distributions, their output has low, smooth perplexity. Burstiness measures sentence length and structure variance. Humans write with high burstiness (mixing short and long sentences), while LLMs produce uniform sentence lengths."),
        ("Q5: Why did you choose a Hybrid Cloud architecture over pure cloud hosting?",
         "Hosting large PyTorch and TensorFlow models on dedicated GPU cloud instances costs upwards of $50-$200/month. By hosting the static frontend on Vercel global CDN and routing inference to dedicated local compute via secure Cloudflare Tunnels, we achieve enterprise performance with $0 infrastructure costs."),
        ("Q6: How did you prevent Cross-Origin Resource Sharing (CORS) security issues?",
         "Configured Flask-CORS on the backend to dynamically whitelist the Vercel origin (authguard.vercel.app), handle HTTP preflight OPTIONS requests, and validate Content-Type and Authorization headers."),
        ("Q7: What is Error Level Analysis (ELA) and how does it detect manipulation?",
         "ELA works by resaving an image at a known lossy compression level (e.g. 90%) and analyzing the difference matrix. Because digital sensors introduce uniform compression degradation across the entire frame, any pasted or synthetic insertion will have a noticeably different error rate than the surrounding pixels."),
        ("Q8: How did you ensure 24/7 backend reliability?",
         "Created a custom Python Watchdog daemon that monitors Flask and Cloudflare process IDs, executes recurring health check pings, automatically restarts failing processes, and dynamically patches frontend configuration files with newly allocated tunnel URLs."),
        ("Q9: What happens if an image is authenticated with your cryptographic watermark?",
         "The backend reads the raw byte stream for the embedded digital signature. If verified, it bypasses heavy GPU neural inference and returns a verified authentic response in under 50ms."),
        ("Q10: If you had another month to work on this project, what would you improve?",
         "I would implement audio temporal slicing for real-time streaming voice detection, train a multi-head Vision Transformer (ViT) on cross-generator diffusion datasets, and deploy the backend as a containerized Docker service on an auto-scaling Kubernetes cluster.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", style_body_bold))
        story.append(Paragraph(a, style_body))
        story.append(Spacer(1, 2.5))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: Generated {filename}")

if __name__ == "__main__":
    build_pdf()
