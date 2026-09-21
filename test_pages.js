const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  // Go to login page
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
  
  // Log in
  await page.type('#login-username', 'admin');
  await page.type('#login-password', 'Admin@1234');
  await page.click('#login-submit-btn');
  
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  
  // Go to Admission
  await page.goto('http://localhost:5173/dashboard/admin/admission', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'reports/admin_admission.png' });
  
  // Go to Attendance
  await page.goto('http://localhost:5173/dashboard/admin/attendance', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'reports/admin_attendance.png' });

  // Go to Results
  await page.goto('http://localhost:5173/dashboard/admin/results', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'reports/admin_results.png' });
  
  await browser.close();
})();
