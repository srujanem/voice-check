const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  // Create a valid 1x1 white JPEG image
  const imgData = Buffer.from('ffd8ffe000104a46494600010101006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc00011080001000103012200021101031101ffc4001f0000010501010101010100000000000000000102030405060708090affc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9ea00000000000000000000ffda000c03010002110311003f00a000', 'hex');
  fs.writeFileSync('test.jpg', imgData);

  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  
  // Expose function to log from page
  page.on('console', msg => console.log('LOG:', msg.text()));
  page.on('dialog', async dialog => {
      console.log('ALERT:', dialog.message());
      await dialog.dismiss();
  });

  console.log("Navigating...");
  await page.goto('http://127.0.0.1:5000/deepfake-ui/index.html', { waitUntil: 'networkidle0' });

  console.log("Setting API key...");
  await page.evaluate(() => {
      localStorage.setItem('api_key', 'test');
  });

  console.log("Uploading file...");
  const fileInput = await page.$('#fileInput');
  await fileInput.uploadFile('test.jpg');

  // Wait a bit for FileReader to load
  await new Promise(r => setTimeout(r, 1000));

  console.log("Checking if button is disabled...");
  const isDisabled = await page.evaluate(() => document.getElementById('btnAnalyze').disabled);
  console.log("Button disabled:", isDisabled);
  
  if (!isDisabled) {
      console.log("Clicking analyze...");
      await page.click('#btnAnalyze');
      await new Promise(r => setTimeout(r, 2000));
  } else {
      console.log("Button was still disabled! Why?");
      // Check displayPreview
      const previewSrc = await page.evaluate(() => document.getElementById('imagePreview').src);
      console.log("Preview SRC:", previewSrc ? previewSrc.substring(0, 30) + "..." : "none");
  }

  await browser.close();
})();
