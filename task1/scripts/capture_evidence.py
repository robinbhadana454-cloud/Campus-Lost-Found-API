import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.abspath("screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def find_op(page, method: str, path: str):
    """Find the Swagger UI operation block by method and path."""
    for op in page.query_selector_all(".opblock"):
        p_elem = op.query_selector(".opblock-summary-path")
        m_elem = op.query_selector(".opblock-summary-method")
        if (
            m_elem
            and p_elem
            and m_elem.inner_text().strip().upper() == method.upper()
            and p_elem.inner_text().strip() == path
        ):
            return op
    return None


def open_and_try(page, op):
    """Ensure the opblock is opened and 'Try it out' is clicked."""
    if not op.evaluate("el => el.classList.contains('is-open')"):
        summary = op.query_selector(".opblock-summary")
        summary.click()
        page.wait_for_timeout(500)

    try_btn = op.wait_for_selector(".try-out__btn", timeout=3000)
    if try_btn and "Cancel" not in try_btn.inner_text():
        try_btn.click()
        page.wait_for_timeout(400)


def close_op(page, op):
    """Collapse the operation block."""
    if op.evaluate("el => el.classList.contains('is-open')"):
        summary = op.query_selector(".opblock-summary")
        summary.click()
        page.wait_for_timeout(400)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 950}, device_scale_factor=1.5)
        page = context.new_page()

        print("Navigating to Swagger UI at http://127.0.0.1:8000/docs...")
        page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
        page.wait_for_selector(".swagger-ui")
        page.wait_for_timeout(1000)

        # 0. Overview
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "00_swagger_ui_overview.png"), full_page=False)
        print("Captured: 00_swagger_ui_overview.png")

        # 1. POST /items (Create Item 1)
        print("Executing 01: POST /items...")
        op = find_op(page, "POST", "/items")
        open_and_try(page, op)
        textarea = op.wait_for_selector("textarea.body-param__text")
        create_payload = """{
  "title": "Blue Dell Inspiron 15 Laptop",
  "description": "Dell Inspiron 15-inch laptop inside black sleeve, left near charging port in Science Lab",
  "category": "Electronics",
  "location": "Science Block Lab 204",
  "reported_by": "Alex Morgan",
  "status": "Lost"
}"""
        textarea.fill(create_payload)
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_post_create_item.png"))
        print("Captured: 01_post_create_item.png")
        close_op(page, op)

        # 2. POST /items (Create Item 2)
        print("Executing POST /items for second item...")
        op = find_op(page, "POST", "/items")
        open_and_try(page, op)
        textarea = op.wait_for_selector("textarea.body-param__text")
        create_payload2 = """{
  "title": "Calculus 9th Edition Hardcover",
  "description": "Stewart Calculus textbook with yellow bookmark left on library desk",
  "category": "Documents",
  "location": "Central Library Desk 14",
  "reported_by": "Prof. David Clark",
  "status": "Found"
}"""
        textarea.fill(create_payload2)
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_post_second_item.png"))
        print("Captured: 02_post_second_item.png")
        close_op(page, op)

        # 3. GET /items (List all items)
        print("Executing 03: GET /items...")
        op = find_op(page, "GET", "/items")
        open_and_try(page, op)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_get_all_items.png"))
        print("Captured: 03_get_all_items.png")
        close_op(page, op)

        # 4. GET /items/{item_id} (Get Item 1)
        print("Executing 04: GET /items/{item_id}...")
        op = find_op(page, "GET", "/items/{item_id}")
        open_and_try(page, op)
        input_box = op.wait_for_selector("input[placeholder='item_id']")
        input_box.fill("1")
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_get_item_by_id.png"))
        print("Captured: 04_get_item_by_id.png")
        close_op(page, op)

        # 5. PUT /items/{item_id} (Update details/status)
        print("Executing 05: PUT /items/{item_id}...")
        op = find_op(page, "PUT", "/items/{item_id}")
        open_and_try(page, op)
        input_box = op.wait_for_selector("input[placeholder='item_id']")
        input_box.fill("1")
        textarea = op.wait_for_selector("textarea.body-param__text")
        update_payload = """{
  "status": "Returned",
  "location": "Campus Security Office (Claimed by owner)"
}"""
        textarea.fill(update_payload)
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "05_put_update_item.png"))
        print("Captured: 05_put_update_item.png")
        close_op(page, op)

        # 6. GET /items/status/{status} (Status filtering)
        print("Executing 06: GET /items/status/{status}...")
        op = find_op(page, "GET", "/items/status/{status}")
        open_and_try(page, op)
        input_box = op.wait_for_selector("input[placeholder='status']")
        input_box.fill("Returned")
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "06_filter_by_status.png"))
        print("Captured: 06_filter_by_status.png")
        close_op(page, op)

        # 7. GET /items/category/{category} (Category filtering)
        print("Executing 07: GET /items/category/{category}...")
        op = find_op(page, "GET", "/items/category/{category}")
        open_and_try(page, op)
        input_box = op.wait_for_selector("input[placeholder='category']")
        input_box.fill("Electronics")
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "07_filter_by_category.png"))
        print("Captured: 07_filter_by_category.png")
        close_op(page, op)

        # 8. Validation Error (422) - Invalid Status & Blank Title
        print("Executing 08: Validation Error (422)...")
        op = find_op(page, "POST", "/items")
        open_and_try(page, op)
        textarea = op.wait_for_selector("textarea.body-param__text")
        invalid_payload = """{
  "title": "",
  "description": "ab",
  "category": "Electronics",
  "location": "Cafeteria",
  "reported_by": "Anonymous",
  "status": "Stolen"
}"""
        textarea.fill(invalid_payload)
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "08_validation_error_422.png"))
        print("Captured: 08_validation_error_422.png")
        close_op(page, op)

        # 9. Error Handling: Item Not Found (404)
        print("Executing 09: Item Not Found (404)...")
        op = find_op(page, "GET", "/items/{item_id}")
        open_and_try(page, op)
        input_box = op.wait_for_selector("input[placeholder='item_id']")
        input_box.fill("9999")
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "09_error_item_not_found_404.png"))
        print("Captured: 09_error_item_not_found_404.png")
        close_op(page, op)

        # 10. DELETE /items/{item_id} (Delete item 2)
        print("Executing 10: DELETE /items/{item_id}...")
        op = find_op(page, "DELETE", "/items/{item_id}")
        open_and_try(page, op)
        input_box = op.wait_for_selector("input[placeholder='item_id']")
        input_box.fill("2")
        page.wait_for_timeout(300)
        op.wait_for_selector(".execute").click()
        op.wait_for_selector(".responses-table .response", timeout=5000)
        page.wait_for_timeout(1000)
        op.scroll_into_view_if_needed()
        op.screenshot(path=os.path.join(SCREENSHOTS_DIR, "10_delete_item.png"))
        print("Captured: 10_delete_item.png")
        close_op(page, op)

        browser.close()
        print("All screenshots generated and saved to screenshots/ directory successfully!")


if __name__ == "__main__":
    run()
