const puppeteer = require('puppeteer');


(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https:///www.python.org/');
  await page.screenshot({ path: 'pythonorg.png'});
  await browser.close();
})();

