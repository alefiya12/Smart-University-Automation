const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Set viewport for a desktop view
  await page.setViewport({ width: 1280, height: 800 });
  
  // Go to login page
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'reports/login_page.png' });
  
  // Log in
  await page.type('#login-username', 'admin');
  await page.type('#login-password', 'Admin@1234');
  await page.click('#login-submit-btn');
  
  // Wait for navigation
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'reports/admin_dashboard.png' });
  
  await browser.close();
})();
