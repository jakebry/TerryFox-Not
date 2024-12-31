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

# Initialize Notion clients for multiple accounts
notion_clients = {key: Client(auth=api_key) for key, api_key in config.NOTION_API_KEYS.items()}

def loading_animation(message):
    """Display a loading animation with a message."""
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if loading_animation.done:
            break
        print(f'\r{message} {c}', end='', flush=True)
        time.sleep(0.1)
    print('\r', end='', flush=True)

loading_animation.done = False

def get_monthly_progress(notion, database_id):
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
    return f"{config.GITHUB_PAGES_URL}{file_names[section]}"

def find_image_block(blocks):
    """Recursively search for an image block within given blocks."""
    for block in blocks:
        if block['type'] == 'image':
            return block['id']
        if 'children' in block:
            image_block_id = find_image_block(block['children'])
            if image_block_id:
                return image_block_id
    return None

def update_image_block(notion, page_id, image_url):
    """Update the image block in the Notion page."""
    try:
        # Fetch the children blocks of the page
        response = notion.blocks.children.list(block_id=page_id)
        blocks = response['results']

        # Find the image block
        image_block_id = find_image_block(blocks)
        if not image_block_id:
            logging.error("No image block found.")
            return

        # Update the image block with the new image URL
        notion.blocks.update(
            block_id=image_block_id,
            image={"type": "external", "external": {"url": image_url}}
        )
        logging.info(f"Updated image block with URL: {image_url}")
    except Exception as e:
        logging.error(f"An error occurred while updating image block: {e}")

def process_page(page):
    """Process a single page to update its image based on progress."""
    notion = notion_clients[page["account_key"]]
    progress = get_monthly_progress(notion, page["database_id"])
    if progress is not None:
        image_url = determine_image(progress)
        update_image_block(notion, page["page_id"], image_url)

def main():
    """Main function to process all pages."""
    loading_thread = threading.Thread(target=loading_animation, args=("Processing pages",))
    loading_thread.start()

    try:
        for page in config.PAGES:
            process_page(page)
    finally:
        loading_animation.done = True
        loading_thread.join()

if __name__ == "__main__":
    main()
