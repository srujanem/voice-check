const fs = require('fs');
let content = fs.readFileSync('D:/voice-check/voice-check/theme.js', 'utf8');

const startIndex = content.indexOf('function getBotResponse(q) {');
const endIndex = content.indexOf('function handleSend() {');

if (startIndex !== -1 && endIndex !== -1) {
    const newBotResponse = `    function getBotResponse(q) {
        q = q.toLowerCase();
        
        if (q === 'hi' || q === 'hello' || q === 'hey' || q.includes('hi ') || q.includes('hello ') || q.includes('hey ')) {
            return "Hello! ?? I'm the AuthGuard AI Assistant. I can help you with questions about our detection models, pricing, API, batch analysis, URL scanning, or how everything works under the hood. What would you like to know?";
        }
        
        if (q.includes('who made') || q.includes('who created') || q.includes('founder') || q.includes('ceo') || q.includes('srujan') || q.includes('developer')) {
            return "AuthGuard (VoiceCheck) was created by **Srujan**. He built this platform to combat the rise of deepfakes and AI-generated misinformation!";
        }
        
        if (q.includes('price') || q.includes('pricing') || q.includes('cost') || q.includes('money') || q.includes('pay') || q.includes('subscription') || q.includes('free') || q.includes('plans')) {
            return "We offer 3 straightforward tiers:<br><br>?? <b>Free Plan:</b> Basic scans up to 5MB file sizes.<br>?? <b>Pro Plan ($19/mo):</b> Increased 50MB limits, Batch Analysis tools, and priority processing.<br>?? <b>Enterprise Plan ($99/mo):</b> Full programmatic API access for your own applications.";
        }
        
        if (q.includes('api') || q.includes('code') || q.includes('programmatic') || q.includes('integrate') || q.includes('endpoint')) {
            return "Developers love AuthGuard! By subscribing to our Enterprise plan ($99/mo), you gain full access to the AuthGuard REST API. You can securely send text, images, video, and audio to our endpoints and receive detailed AI probability scores in JSON format.";
        }
        
        if (q.includes('accuracy') || q.includes('accurate') || q.includes('trust') || q.includes('reliable') || q.includes('performance') || q.includes('good is')) {
            return "AuthGuard is incredibly accurate, averaging <b>96.8%</b> overall across all modalities.<br>??? Voice: 96.5%<br>??? Image: 96.8% (Just retrained!)<br>?? Text: 98.1%<br>?? Video: 94.8%";
        }
        
        if (q.includes('watermark') || q.includes('protect') || q.includes('signature') || q.includes('hide') || q.includes('invisible')) {
            return "Our <b>Authentic Watermark Creator</b> is a unique tool that embeds an invisible, tamper-proof cryptographic signature directly into your image's pixels. It proves permanently that the image was human-made and authenticated by AuthGuard.";
        }
        
        if (q.includes('voice') || q.includes('audio') || q.includes('speech') || q.includes('elevenlabs') || q.includes('clone') || q.includes('mp3') || q.includes('wav')) {
            return "The <b>Voice Detector</b> converts your audio into visual spectrograms and analyzes micro-frequencies. It easily flags AI voice clones from tools like ElevenLabs, PlayHT, and Murf.ai with 96.5% accuracy.";
        }
        
        if (q.includes('image') || q.includes('photo') || q.includes('picture') || q.includes('midjourney') || q.includes('dalle') || q.includes('dall-e') || q.includes('stable diffusion') || q.includes('jpeg') || q.includes('png')) {
            return "Our <b>Image Detector</b> analyzes pixel-level inconsistencies and compression artifacts using a highly trained EfficientNetB0 neural network. It catches MidJourney, DALL-E 3, and Stable Diffusion fakes with 96.8% accuracy. We just fed it 31 brand new edge cases today!";
        }
        
        if (q.includes('text') || q.includes('chatgpt') || q.includes('written') || q.includes('writing') || q.includes('essay') || q.includes('claude') || q.includes('gemini') || q.includes('gpt')) {
            return "Our <b>Text Detector</b> analyzes linguistic patterns, perplexity, and burstiness using a RoBERTa ensemble model. It excels at catching ChatGPT, Claude, and Gemini generated essays and articles with a stunning 98.1% accuracy rate.";
        }
        
        if (q.includes('video') || q.includes('deepfake') || q.includes('sora') || q.includes('runway') || q.includes('mp4') || q.includes('movie')) {
            return "The <b>Video Content Scanner</b> works by extracting frames from your video clip and analyzing both the visual anomalies (like weird blinking or blurring) and the audio track. It detects Deepfakes with 94.8% accuracy.";
        }
        
        if (q.includes('url') || q.includes('website') || q.includes('link') || q.includes('article') || q.includes('scan web')) {
            return "Don't want to copy and paste? Use our <b>URL Scanner</b>! Just paste a link to any news article or blog post, and we will automatically extract the text and analyze it for AI generation.";
        }
        
        if (q.includes('batch') || q.includes('bulk') || q.includes('multiple') || q.includes('many files') || q.includes('folder')) {
            return "Got a lot of files? The <b>Batch Analysis</b> tool (available on the Pro Plan) lets you upload up to 50 files at once. We'll scan them all simultaneously and generate a downloadable PDF report.";
        }
        
        if (q.includes('how does it work') || q.includes('how to use') || q.includes('instructions') || q.includes('steps') || q.includes('guide')) {
            return "It's simple!<br>1?? <b>Select a Tool</b> (Text, Image, Voice, etc.)<br>2?? <b>Upload</b> your file or paste your text.<br>3?? <b>Analyze</b> - our neural networks process it in seconds.<br>4?? <b>Review</b> the detailed probability breakdown!";
        }
        
        if (q.includes('privacy') || q.includes('secure') || q.includes('safe') || q.includes('data') || q.includes('save my file') || q.includes('steal')) {
            return "Your privacy is our top priority. Files you upload are processed securely in memory by our backend and are <b>never</b> permanently stored or used to train our models without your explicit consent.";
        }
        
        if (q.includes('login') || q.includes('sign in') || q.includes('account') || q.includes('register') || q.includes('dashboard') || q.includes('sign up')) {
            return "You can log in or register by clicking the 'Sign In' button in the top right corner of the navigation bar. Creating an account lets you view your past scan history!";
        }
        
        if (q.includes('history') || q.includes('past scans') || q.includes('previous') || q.includes('old scans')) {
            return "If you are logged into your account, all of your previous scans are securely saved to your personal Dashboard. You can access your history anytime to review past results.";
        }
        
        if (q.includes('who are you') || q.includes('what is authguard') || q.includes('what is voicecheck') || q.includes('about') || q.includes('your name')) {
            return "I am the AuthGuard AI Assistant! AuthGuard (also known as VoiceCheck) is the ultimate multi-modal AI detection suite built to secure the internet against deceptive AI content.";
        }
        
        if (q.includes('contact') || q.includes('support') || q.includes('feedback') || q.includes('help') || q.includes('email') || q.includes('issue') || q.includes('bug')) {
            return "Need help? You can use the 'Rate Your Experience' / Feedback form at the bottom of the homepage to send a direct email to our support team (srujanem222@gmail.com). We usually reply within 24 hours!";
        }
        
        if (q.includes('thank') || q === 'thanks' || q.includes('awesome') || q.includes('great') || q.includes('cool') || q.includes('good bot')) {
            return "You're very welcome! Feel free to ask if you need anything else.";
        }
        
        if (q.includes('bye') || q.includes('goodbye') || q.includes('see ya') || q.includes('cya')) {
            return "Goodbye! Stay safe out there on the internet! ???";
        }
        
        return "I'm specifically trained on AuthGuard's ecosystem. I can tell you about our Creator (Srujan), our exact Accuracy metrics, Pricing plans, the API, Privacy policies, or how our specific tools (like URL scanning and Batch analysis) work. Could you rephrase your question?";
    }
`;
    
    content = content.substring(0, startIndex) + newBotResponse + content.substring(endIndex);
    fs.writeFileSync('D:/voice-check/voice-check/theme.js', content, 'utf8');
    console.log("Successfully updated chatbot knowledge base.");
} else {
    console.log("Could not find boundaries.");
}
