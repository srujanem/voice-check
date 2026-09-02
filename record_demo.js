const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
    console.log('🎬 Starting automated browser screen recorder...');

    const videoDir = path.join(__dirname, 'recordings');
    if (!fs.existsSync(videoDir)) {
        fs.mkdirSync(videoDir, { recursive: true });
    }

    const browser = await chromium.launch({
        executablePath: 'C:\\Users\\sruja\\AppData\\Local\\ms-playwright\\chromium-1234\\chrome-win64\\chrome.exe',
        headless: true
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        recordVideo: {
            dir: videoDir,
            size: { width: 1280, height: 720 }
        }
    });

    const page = await context.newPage();

    console.log('🌐 Navigating to Image Detector on AuthGuard...');
    await page.goto('https://authguard.vercel.app/deepfake-ui/index.html', { waitUntil: 'networkidle' });

    await page.waitForTimeout(2000);

    console.log('🖱️ Hovering on upload box...');
    const dropZone = page.locator('#drop-zone');
    if (await dropZone.count() > 0) {
        await dropZone.hover();
        await page.waitForTimeout(1000);
    }

    console.log('📤 Uploading AI image sample...');
    const sampleImage = path.join(__dirname, 'dataset_custom', 'fake', 'ai_gen_0.jpg');
    const fallbackImage = path.join(__dirname, 'test.jpg');
    const imgToUpload = fs.existsSync(sampleImage) ? sampleImage : (fs.existsSync(fallbackImage) ? fallbackImage : null);

    if (imgToUpload) {
        const fileInput = page.locator('input[type="file"]');
        await fileInput.setInputFiles(imgToUpload);
        await page.waitForTimeout(2000);

        console.log('🔍 Clicking Analyze Image...');
        const analyzeBtn = page.locator('#btnAnalyze');
        if (await analyzeBtn.count() > 0) {
            await analyzeBtn.hover();
            await page.waitForTimeout(800);
            await analyzeBtn.click();
        }

        console.log('⏳ Waiting for AI analysis to complete...');
        // Wait up to 20s for results section to be visible
        try {
            await page.waitForSelector('#resultsSection:not(.hidden)', { timeout: 20000 });
            console.log('✅ Result appeared!');
            await page.waitForTimeout(2500);

            // Smooth scroll to results
            await page.evaluate(() => {
                window.scrollBy({ top: 350, behavior: 'smooth' });
            });
            await page.waitForTimeout(2000);

            // Hover on Mint / Anchor to Blockchain button
            const mintBtn = page.locator('#mint-report-btn');
            if (await mintBtn.count() > 0 && await mintBtn.isVisible()) {
                await mintBtn.hover();
                await page.waitForTimeout(2500);
            }
        } catch (e) {
            console.log('Note: Backend response timeout or already simulated. Capturing current view...');
            await page.waitForTimeout(3000);
        }
    }

    console.log('💾 Finishing recording...');
    await page.waitForTimeout(2000);

    const videoPath = await page.video().path();
    await context.close();
    await browser.close();

    console.log('🎉 Raw video saved at:', videoPath);

    // Copy to root directory and user Desktop
    const targetFile = path.join(__dirname, 'AuthGuard_LinkedIn_Demo.webm');
    fs.copyFileSync(videoPath, targetFile);
    console.log('📁 Video saved to project root:', targetFile);

    const userDesktop = path.join(process.env.USERPROFILE || 'C:\\Users\\sruja', 'Desktop', 'AuthGuard_LinkedIn_Demo.webm');
    try {
        fs.copyFileSync(videoPath, userDesktop);
        console.log('⭐ Video also copied directly to your Desktop:', userDesktop);
    } catch (err) {
        console.log('Could not copy to Desktop:', err.message);
    }
})();
