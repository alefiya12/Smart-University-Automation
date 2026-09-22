const puppeteer = require('puppeteer');

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function setHud(page, message) {
  try {
    await page.evaluate((msg) => {
      let hud = document.getElementById('rpa-live-hud');
      if (!hud) {
        hud = document.createElement('div');
        hud.id = 'rpa-live-hud';
        hud.style.position = 'fixed';
        hud.style.top = '16px';
        hud.style.right = '24px';
        hud.style.zIndex = '9999999';
        hud.style.background = 'linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%)';
        hud.style.color = '#38BDF8';
        hud.style.padding = '12px 22px';
        hud.style.borderRadius = '32px';
        hud.style.boxShadow = '0 10px 30px rgba(0,0,0,0.35)';
        hud.style.fontFamily = 'system-ui, -apple-system, sans-serif';
        hud.style.fontSize = '14px';
        hud.style.fontWeight = '600';
        hud.style.display = 'flex';
        hud.style.alignItems = 'center';
        hud.style.gap = '10px';
        hud.style.border = '1px solid rgba(56, 189, 248, 0.4)';
        hud.style.pointerEvents = 'none';
        hud.style.transition = 'all 0.3s ease';
        document.body.appendChild(hud);
      }
      hud.innerHTML = `<span style="font-size: 16px;">⚡ RPA BOT LIVE:</span> <span style="color: #ffffff;">${msg}</span>`;
    }, message);
  } catch (e) {}
}

async function smoothScroll(page) {
  try {
    await page.evaluate(async () => {
      window.scrollBy({ top: 350, behavior: 'smooth' });
      await new Promise(r => setTimeout(r, 600));
      window.scrollBy({ top: -350, behavior: 'smooth' });
    });
  } catch (e) {}
}

async function runLiveShowcase() {
  console.log('====================================================================');
  console.log('🎬 LAUNCHING LIVE RPA AUTOMATION SHOWCASE ON YOUR SCREEN');
  console.log('====================================================================\n');

  const browser = await puppeteer.launch({
    headless: false,
    slowMo: 45,
    defaultViewport: null,
    args: [
      '--window-size=1280,840',
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });

  const [page] = await browser.pages();
  await page.setViewport({ width: 1280, height: 800 });

  async function loginAs(username, password, roleLabel, expectedUrlPrefix) {
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await setHud(page, `Authenticating as ${roleLabel} (${username})...`);
    await wait(800);

    await page.waitForSelector('#login-username');
    await page.click('#login-username', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('#login-username', username, { delay: 40 });

    await page.click('#login-password', { clickCount: 3 });
    await page.keyboard.press('Backspace');
    await page.type('#login-password', password, { delay: 40 });

    await setHud(page, `Submitting credentials for ${roleLabel}...`);
    await wait(500);
    await page.click('#login-submit-btn');

    await page.waitForFunction(
      path => window.location.pathname.startsWith(path),
      { timeout: 12000 },
      expectedUrlPrefix
    );
    await wait(1000);
  }

  try {
    // -------------------------------------------------------------
    // ACT 1: ADMINISTRATOR WORKFLOW & BOT AUDIT
    // -------------------------------------------------------------
    console.log('🌟 [ACT 1] ADMINISTRATOR WORKSPACE & BOT AUDIT SUITE');
    await loginAs('admin', 'Admin@1234', 'System Administrator', '/dashboard/admin');

    await setHud(page, 'Admin Overview Dashboard: Real-time academic metrics');
    await smoothScroll(page);
    await wait(2000);

    const adminSections = [
      {
        name: 'Admissions & Quota Allocation Engine',
        url: '/dashboard/admin/admission',
        hud: 'Admission & Quota Allocation: Inspecting candidate staging ledger'
      },
      {
        name: 'Subject-Wise Matrix Attendance Module',
        url: '/dashboard/admin/attendance',
        hud: 'Attendance Automation: Ingestion processor & low attendance alert triggers'
      },
      {
        name: 'Dual-Threshold Results & Exam Standings',
        url: '/dashboard/admin/results',
        hud: 'Results Module: Dual-Threshold (Int 12/30, Ext 28/70) & Excel consolidated reports'
      },
      {
        name: 'Student Information Directory',
        url: '/dashboard/admin/students',
        hud: 'Student Directory: Academic standing & registered enrollment records'
      },
      {
        name: 'Faculty Members Directory',
        url: '/dashboard/admin/faculty',
        hud: 'Faculty Directory: Assigned departments and employee credentials'
      },
      {
        name: 'Departments & Course Configurations',
        url: '/dashboard/admin/departments',
        hud: 'Curriculum & Courses: Semester structures and minimum attendance rules'
      },
      {
        name: 'Fee Collections & Transaction Ledger',
        url: '/dashboard/admin/fees',
        hud: 'Financial Ledger: Invoice tracking and payment receipts'
      },
      {
        name: 'RPA Bot Execution Audit Logs',
        url: '/dashboard/admin/bot-logs',
        hud: 'RPA Bot Audit Center: Robot Framework execution logs & HTML viewers'
      },
      {
        name: 'Automated System Notifications Dispatch',
        url: '/dashboard/admin/notifications',
        hud: 'Notification Audit: Automated alerts dispatched to students & faculty'
      }
    ];

    for (const sec of adminSections) {
      console.log(`  ➜ [Admin] Showing ${sec.name}...`);
      await page.goto(`http://localhost:5173${sec.url}`, { waitUntil: 'networkidle2' });
      await setHud(page, sec.hud);
      await smoothScroll(page);
      await wait(2200);
    }

    // -------------------------------------------------------------
    // ACT 2: FACULTY PORTAL & ACADEMIC INGESTION
    // -------------------------------------------------------------
    console.log('\n🌟 [ACT 2] FACULTY INGESTION & CLASS MANAGEMENT PORTAL');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.reload({ waitUntil: 'networkidle2' });

    await loginAs('rajesh.sharma@faculty.edu', 'Faculty@123', 'Faculty Member (Prof. Rajesh)', '/dashboard/faculty');

    await setHud(page, 'Faculty Workspace: Active courses & student rosters');
    await wait(2000);

    const facultySections = [
      {
        name: 'Matrix Attendance Excel Processor',
        url: '/dashboard/faculty/attendance',
        hud: 'Faculty Attendance: Bulk matrix Excel uploader & bot execution logger'
      },
      {
        name: 'Dual-Threshold Marks Submission Module',
        url: '/dashboard/faculty/marks',
        hud: 'Examination Marks: Internal & External scores ingestion with instant validation'
      },
      {
        name: 'Course-Enrolled Student Directory',
        url: '/dashboard/faculty/students',
        hud: 'Student Roster: Active student enrollments and backlog filters'
      },
      {
        name: 'Faculty Profile & Credentials',
        url: '/dashboard/faculty/profile',
        hud: 'Faculty Profile: Department designation and verified credentials'
      }
    ];

    for (const sec of facultySections) {
      console.log(`  ➜ [Faculty] Showing ${sec.name}...`);
      await page.goto(`http://localhost:5173${sec.url}`, { waitUntil: 'networkidle2' });
      await setHud(page, sec.hud);
      await smoothScroll(page);
      await wait(2200);
    }

    // -------------------------------------------------------------
    // ACT 3: STUDENT SELF-SERVICE PORTAL
    // -------------------------------------------------------------
    console.log('\n🌟 [ACT 3] STUDENT SELF-SERVICE PORTAL');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.reload({ waitUntil: 'networkidle2' });

    await loginAs('arjun.patel@student.edu', 'Student@123', 'Enrolled Student (Arjun Patel)', '/dashboard/student');

    await setHud(page, 'Student Dashboard: Live GPA, attendance meter & exam alerts');
    await wait(2200);

    const studentSections = [
      {
        name: 'Student Admission & Verification Certificate',
        url: '/dashboard/student/admission',
        hud: 'Admission Record: Program allocation & PDF admission letter download'
      },
      {
        name: 'Subject-Wise Attendance Gauges & Warnings',
        url: '/dashboard/student/attendance',
        hud: 'Attendance Meter: 75% threshold gauges & warning advisory alerts'
      },
      {
        name: 'Examination Results & Official Marksheet',
        url: '/dashboard/student/results',
        hud: 'Results Card: Dual-Threshold breakdown, SGPA/CGPA & Marksheet PDF download'
      },
      {
        name: 'Student Fee Invoices & Payment Ledger',
        url: '/dashboard/student/fees',
        hud: 'Fee Ledger: Invoices, outstanding balances, and official fee receipts'
      },
      {
        name: 'Automated Advisory & Notification Inbox',
        url: '/dashboard/student/notifications',
        hud: 'Notification Center: Automated attendance warnings & result release notices'
      },
      {
        name: 'Personal Profile & Account Settings',
        url: '/dashboard/student/profile',
        hud: 'Student Profile: Academic enrollment info and security settings'
      }
    ];

    for (const sec of studentSections) {
      console.log(`  ➜ [Student] Showing ${sec.name}...`);
      await page.goto(`http://localhost:5173${sec.url}`, { waitUntil: 'networkidle2' });
      await setHud(page, sec.hud);
      await smoothScroll(page);
      await wait(2200);
    }

    await setHud(page, '🎉 RPA AUTOMATION SHOWCASE COMPLETE! System 100% operational.');
    await wait(3000);

    console.log('\n====================================================================');
    console.log('✅ LIVE AUTOMATION SHOWCASE COMPLETED SUCCESSFULLY!');
    console.log('====================================================================\n');

  } catch (err) {
    console.error('❌ Live Showcase Error:', err);
  } finally {
    await browser.close();
  }
}

runLiveShowcase();
