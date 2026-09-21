const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('BROWSER_CONSOLE:', msg.text()));
  page.on('pageerror', error => console.log('BROWSER_ERROR:', error.message));
  
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2' });
  
  await page.evaluate(() => {
    localStorage.setItem('access_token', 'fake_token');
    localStorage.setItem('user', JSON.stringify({id: 1, role: 'admin', username: 'admin'}));
  });
  
  await page.goto('http://localhost:5173/dashboard/admin', { waitUntil: 'networkidle2' });
  
  await browser.close();
})();
