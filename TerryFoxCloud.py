import os
import logging
from notion_client import Client
import config  # Import the configuration file
import time
import itertools
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("notion_script.log"), logging.StreamHandler()]
)

# Configuration
NOTION_API_KEY = config.NOTION_API_KEY
GITHUB_PAGES_URL = config.GITHUB_PAGES_URL
PAGES = config.PAGES

# Initialize Notion client
notion = Client(auth=NOTION_API_KEY)

def loading_animation(message):
    """Display a loading animation with a message."""
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if loading_animation.done:
            break
        print(f'\r{message} {c}', end='', flush=True)
        time.sleep(0.1)
    print('\r', end='', flush=True)

loading_animation.done = False

def get_monthly_progress(database_id):
    """Retrieve the progress percentage from the Notion database."""
    try:
        logging.info("Checking balances...")
        response = notion.databases.query(database_id=database_id)
        for result in response["results"]:
            progress = result["properties"].get("Progress", {}).get("formula", {}).get("number")
            if progress is not None:
                progress *= 100  # Adjust the progress value
                logging.info(f"Found progress percentage: {progress}%.")
                return progress
            else:
                logging.error("Progress value is None.")
                return None
    except Exception as e:
        logging.error(f"An error occurred while fetching progress: {e}")
        return None

def determine_image(progress):
    """Determine the GitHub Pages URL to use based on progress."""
    section = int(progress // 16.7)  # Determine which section the progress falls into
    section = min(section, 5)  # Ensure it does not exceed the maximum index (5)
    logging.info(f"Progress {progress}% falls into section {section}.")

    # Map progress to image file names (replace these with actual file names in your GitHub Pages)
    file_names = [
        "1 - Lots of Money.png",
        "2 - Some Spending Money.png",
        "3 - Neutral.png",
        "4 - Anxious.png",
        "5 - Over budget Sad.png",
        "6 - Max Overbudget Dead.png",
    ]
    return f"{GITHUB_PAGES_URL}{file_names[section]}"

def find_image_block(blocks):
    """Recursively search for an image block within given blocks."""
    for block in blocks:
        logging.info(f"Checking Block ID: {block['id']}, Type: {block['type']}")
        if block["type"] == "image":
            return block["id"]
        elif "has_children" in block and block["has_children"]:
            child_blocks = notion.blocks.children.list(block["id"])["results"]
            image_block_id = find_image_block(child_blocks)
            if image_block_id:
                return image_block_id
    return None

def update_image_block(page_id, image_url):
    """Update the image block in the page with the new image."""
    try:
        logging.info("Updating image...")
        blocks = notion.blocks.children.list(page_id)["results"]
        image_block_id = find_image_block(blocks)

        if image_block_id:
            notion.blocks.update(
                block_id=image_block_id,
                image={"external": {"url": image_url}}  # Correct payload format
            )
            logging.info(f"Successfully updated image block with URL: {image_url}")
        else:
            logging.warning("No image block found on the page.")
    except Exception as e:
        logging.error(f"Error while updating image block: {e}")

def process_page(page):
    page_id = page["page_id"]
    database_id = page["database_id"]

    logging.info(f"Processing page {page_id}")

    # Step 1: Get progress percentage
    progress = get_monthly_progress(database_id)
    if progress is None:
        logging.error("Progress could not be retrieved. Skipping page.")
        return

    # Step 2: Determine the image URL based on progress
    image_url = determine_image(progress)

    if not image_url:
        logging.error("Image URL could not be determined. Skipping page.")
        return

    # Step 3: Update the image block
    update_image_block(page_id, image_url)

def main():
    logging.info("Script started.")
    loading_thread = threading.Thread(target=loading_animation, args=("Processing",))
    loading_thread.start()

    for page in PAGES:
        process_page(page)

    loading_animation.done = True
    loading_thread.join()
    logging.info("Script finished successfully.")

if __name__ == "__main__":
    main()
