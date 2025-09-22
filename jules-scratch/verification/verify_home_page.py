from playwright.sync_api import sync_playwright, expect, TimeoutError

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:5173/")

            heading = page.get_by_role("heading", name="⚡ CorakSmart ⚡")
            expect(heading).to_be_visible(timeout=5000) # Shorter timeout

            page.screenshot(path="jules-scratch/verification/verification.png")
            print("Screenshot taken successfully.")

        except TimeoutError:
            print("TimeoutError: The heading was not found. Saving page content for debugging.")
            html_content = page.content()
            with open("jules-scratch/verification/page_content.html", "w") as f:
                f.write(html_content)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
