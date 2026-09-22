const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const SCREENSHOTS_DIR = path.join(__dirname, 'reports', 'screenshots');
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function runAutomation() {
  console.log('===============================================================');
  console.log('🚀 SMART UNIVERSITY AUTOMATION: E2E AUTOMATION TASK EXECUTION');
  console.log('===============================================================\n');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 850 });

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Filter non-fatal browser resource warnings
      if (!text.includes('favicon') && !text.includes('net::ERR_FAILED')) {
        errors.push(`[Console Error] ${text}`);
      }
    }
  });
  page.on('pageerror', err => {
    errors.push(`[Runtime Exception] ${err.message}`);
  });

  try {
    // -------------------------------------------------------------
    // TASK 1: ADMIN WORKFLOW & AUDIT PORTAL
    // -------------------------------------------------------------
    console.log('📌 [TASK 1] ADMIN PORTAL AUTOMATION');
    console.log('  ➜ Navigating to Login Page (http://localhost:5173/login)...');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '01_login_page.png') });

    async function loginAs(email, password, expectedPath) {
      await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
      await page.waitForSelector('#login-username');
      
      // Clear inputs
      await page.click('#login-username', { clickCount: 3 });
      await page.keyboard.press('Backspace');
      await page.type('#login-username', email);

      await page.click('#login-password', { clickCount: 3 });
      await page.keyboard.press('Backspace');
      await page.type('#login-password', password);

      await page.click('#login-submit-btn');

      // Wait for React Router client-side transition to dashboard
      await page.waitForFunction(
        path => window.location.pathname.startsWith(path),
        { timeout: 10000 },
        expectedPath
      );
      await new Promise(r => setTimeout(r, 1000));
    }

    // -------------------------------------------------------------
    // TASK 1: ADMIN WORKFLOW & AUDIT PORTAL
    // -------------------------------------------------------------
    console.log('📌 [TASK 1] ADMIN PORTAL AUTOMATION');
    console.log('  ➜ Navigating to Login Page (http://localhost:5173/login)...');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '01_login_page.png') });

    console.log('  ➜ Authenticating as Admin (admin / Admin@1234)...');
    await loginAs('admin', 'Admin@1234', '/dashboard/admin');
    console.log(`  ✓ Successfully logged in! Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '02_admin_dashboard.png') });

    const adminRoutes = [
      { name: 'Admissions & Allocation', path: '/dashboard/admin/admission', shot: '03_admin_admission.png' },
      { name: 'Subject Attendance', path: '/dashboard/admin/attendance', shot: '04_admin_attendance.png' },
      { name: 'Dual-Threshold Results', path: '/dashboard/admin/results', shot: '05_admin_results.png' },
      { name: 'Students Directory', path: '/dashboard/admin/students', shot: '06_admin_students.png' },
      { name: 'Faculty Directory', path: '/dashboard/admin/faculty', shot: '07_admin_faculty.png' },
      { name: 'Departments & Courses', path: '/dashboard/admin/departments', shot: '08_admin_departments.png' },
      { name: 'Fee Ledger', path: '/dashboard/admin/fees', shot: '09_admin_fees.png' },
      { name: 'RPA Bot Logs', path: '/dashboard/admin/bot-logs', shot: '10_admin_bot_logs.png' },
      { name: 'System Notifications', path: '/dashboard/admin/notifications', shot: '11_admin_notifications.png' },
    ];

    for (const route of adminRoutes) {
      console.log(`  ➜ Verifying Admin Task: ${route.name} (${route.path})...`);
      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle2' });
      await new Promise(r => setTimeout(r, 600));
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, route.shot) });
      console.log(`    ✓ Loaded ${route.name}`);
    }

    // -------------------------------------------------------------
    // TASK 2: FACULTY WORKFLOW & ACADEMIC INGESTION PORTAL
    // -------------------------------------------------------------
    console.log('\n📌 [TASK 2] FACULTY PORTAL AUTOMATION');
    console.log('  ➜ Signing out from Admin session...');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload({ waitUntil: 'networkidle2' });

    console.log('  ➜ Authenticating as Faculty (rajesh.sharma@faculty.edu)...');
    await loginAs('rajesh.sharma@faculty.edu', 'Faculty@123', '/dashboard/faculty');
    console.log(`  ✓ Successfully logged in as Faculty! Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '12_faculty_dashboard.png') });

    const facultyRoutes = [
      { name: 'Attendance Uploader', path: '/dashboard/faculty/attendance', shot: '13_faculty_attendance.png' },
      { name: 'Marks Processor', path: '/dashboard/faculty/marks', shot: '14_faculty_marks.png' },
      { name: 'Enrolled Students Roster', path: '/dashboard/faculty/students', shot: '15_faculty_students.png' },
      { name: 'Faculty Profile', path: '/dashboard/faculty/profile', shot: '16_faculty_profile.png' },
    ];

    for (const route of facultyRoutes) {
      console.log(`  ➜ Verifying Faculty Task: ${route.name} (${route.path})...`);
      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle2' });
      await new Promise(r => setTimeout(r, 600));
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, route.shot) });
      console.log(`    ✓ Loaded ${route.name}`);
    }

    // -------------------------------------------------------------
    // TASK 3: STUDENT WORKFLOW & SELF-SERVICE PORTAL
    // -------------------------------------------------------------
    console.log('\n📌 [TASK 3] STUDENT PORTAL AUTOMATION');
    console.log('  ➜ Signing out from Faculty session...');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload({ waitUntil: 'networkidle2' });

    console.log('  ➜ Authenticating as Student (arjun.patel@student.edu)...');
    await loginAs('arjun.patel@student.edu', 'Student@123', '/dashboard/student');
    console.log(`  ✓ Successfully logged in as Student! Current URL: ${page.url()}`);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, '17_student_dashboard.png') });

    const studentRoutes = [
      { name: 'My Admission Record', path: '/dashboard/student/admission', shot: '18_student_admission.png' },
      { name: 'My Attendance & Alerts', path: '/dashboard/student/attendance', shot: '19_student_attendance.png' },
      { name: 'My Results & SGPA', path: '/dashboard/student/results', shot: '20_student_results.png' },
      { name: 'My Fee Invoices', path: '/dashboard/student/fees', shot: '21_student_fees.png' },
      { name: 'My Notification Inbox', path: '/dashboard/student/notifications', shot: '22_student_notifications.png' },
      { name: 'My Profile', path: '/dashboard/student/profile', shot: '23_student_profile.png' },
    ];

    for (const route of studentRoutes) {
      console.log(`  ➜ Verifying Student Task: ${route.name} (${route.path})...`);
      await page.goto(`http://localhost:5173${route.path}`, { waitUntil: 'networkidle2' });
      await new Promise(r => setTimeout(r, 600));
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, route.shot) });
      console.log(`    ✓ Loaded ${route.name}`);
    }

    console.log('\n===============================================================');
    console.log('🎉 ALL AUTOMATION TASKS EXECUTED SUCCESSFULLY!');
    console.log(`📸 23 Screenshot checkpoints saved to: ${SCREENSHOTS_DIR}`);
    if (errors.length > 0) {
      console.log(`⚠️ Warnings/Errors noted (${errors.length}):`);
      errors.forEach(e => console.log(`   - ${e}`));
    } else {
      console.log('✅ ZERO RUNTIME OR BROWSER CONSOLE ERRORS ENCOUNTERED!');
    }
    console.log('===============================================================\n');

  } catch (err) {
    console.error('❌ Automation Task Execution Failed:', err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runAutomation();
