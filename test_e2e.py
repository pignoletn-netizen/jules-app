import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        # 1. Load homepage
        print("Navigating to http://127.0.0.1:3000...")
        await page.goto("http://127.0.0.1:3000")
        await page.wait_for_timeout(1000)

        # 2. Test Tab 1: Search species
        print("Testing species search for Textrix denticulata...")
        await page.click("button:has-text('Rechercher')")
        await page.wait_for_selector("text=CDnom INPN", timeout=10000)
        print("Species search completed successfully!")

        # 3. Switch to Tab 2: Inventory Analysis
        print("Switching to Tab 2...")
        await page.get_by_role("button", name="Onglet 2").click()
        await page.wait_for_timeout(500)

        # 4. Upload sample file
        print("Uploading sample inventory file...")
        await page.set_input_files("input[type='file']", "backend/data/sample_inventory.xlsx")
        await page.wait_for_timeout(500)

        # Click launch analysis
        print("Clicking launch R statistical analysis...")
        await page.get_by_role("button", name="Lancer l'Analyse Statistique R").click()
        await page.wait_for_selector("text=Analyse terminée avec succès !", timeout=25000)
        print("Analysis completed successfully!")

        # Click on AFC tab
        await page.get_by_role("button", name="4. AFC & HCPC").click()
        await page.wait_for_timeout(1500)

        # Capture screenshot
        screenshot_path = "verification_e2e.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
