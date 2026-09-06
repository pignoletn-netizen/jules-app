import { chromium } from 'playwright';

async function verify() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  console.log('Navigating to home...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshot_home_clean.png', fullPage: true });

  console.log('Navigating to recap...');
  await page.goto('http://localhost:3000/pmu-recap', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshot_recap_clean.png', fullPage: true });

  console.log('Navigating to race desktop...');
  await page.goto('http://localhost:3000/race/21022025/R1/C1', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'screenshot_race_desktop_clean.png', fullPage: true });

  await browser.close();
  console.log('Verification screenshots taken successfully.');
}

verify().catch(console.error);
