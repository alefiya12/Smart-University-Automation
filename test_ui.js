const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('BROWSER_ERROR:', msg.text());
    }
  });
  page.on('pageerror', error => console.log('RUNTIME_ERROR:', error.message));
  
  console.log("Navigating to login...");
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
  
  console.log("Typing credentials...");
  await page.type('#login-username', 'admin@smartuni.edu');
  await page.type('#login-password', 'admin');
  await page.click('#login-submit-btn');
  
  console.log("Waiting for navigation...");
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  
  console.log("Current URL:", page.url());
  
  const routes = ['students', 'faculty', 'departments', 'fees'];
  for (const route of routes) {
    console.log(`Navigating to ${route}...`);
    await page.goto(`http://localhost:5173/dashboard/admin/${route}`, { waitUntil: 'networkidle2' });
    console.log(`${route} URL:`, page.url());
    // Give it a second to see if a runtime error throws
    await new Promise(r => setTimeout(r, 1000));
  }

  await browser.close();
  console.log("Done.");
})();
