const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  // Create a dummy image
  fs.writeFileSync('dummy.jpg', Buffer.from('ffd8ffe000104a46494600010101004800480000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc0001108000a000a03012200021101031101ffc4001500010100000000000000000000000000000002ffc40014100100000000000000000000000000000000ffc4001501010100000000000000000000000000000002ffc40014110100000000000000000000000000000000ffda000c03010002110311003f00a000', 'hex'));

  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('dialog', async dialog => {
      console.log('DIALOG:', dialog.message());
      await dialog.dismiss();
  });

  await page.goto('http://127.0.0.1:5000/deepfake-ui/index.html', { waitUntil: 'networkidle0' });
  
  // Set localStorage API key to pretend we're logged in
  await page.evaluate(() => {
      localStorage.setItem('api_key', 'test_key');
  });

  // Upload file
  const fileInput = await page.$('#fileInput');
  await fileInput.uploadFile('dummy.jpg');
  console.log("Uploaded file");

  // Check if button is enabled
  const btnDisabled = await page.evaluate(() => document.getElementById('btnAnalyze').disabled);
  console.log("Is analyze button disabled?", btnDisabled);

  // Click analyze
  await page.click('#btnAnalyze');
  console.log("Clicked analyze");

  // Wait for result
  await new Promise(r => setTimeout(r, 2000));
  
  const result = await page.evaluate(() => document.getElementById('classificationResult').innerText);
  console.log("Result:", result);

  await browser.close();
})();
