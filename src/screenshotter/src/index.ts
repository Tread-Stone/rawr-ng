import puppeteer from "puppeteer";

const takeScreenshot = async (url: string) => {
    if (!url) {
        console.error('no url');
        process.exit(1);
    }

    const urlParsed = url.replace("https://", "");

    const browser = await puppeteer.launch({
        args: ["--no-sandbox"],
    });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.screenshot({ path: `test.png` });
    await browser.close();
};

const url = process.argv[2];
takeScreenshot(url);
