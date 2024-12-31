import logging
from notion_client import Client
import config  # Import the configuration file
import time
import itertools
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Change logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
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
    logging.debug(f"Querying database {database_id}")
    response = notion.databases.query(database_id=database_id)
    for result in response["results"]:
        progress = result["properties"].get("Progress", {}).get("formula", {}).get("number")
        if progress is not None:
            progress *= 100  # Adjust the progress value
            logging.debug(f"Progress found: {progress}%")
            return progress
    logging.debug("No progress found")
    return None

def determine_image(progress):
    """Determine the GitHub Pages URL to use based on progress."""
    section = int(progress // 16.7)  # Determine which section the progress falls into
    section = min(section, 5)  # Ensure it does not exceed the maximum index (5)

    # Map progress to image file names (replace these with actual file names in your GitHub Pages)
    file_names = [
        "1 - Lots of Money.png",
        "2 - Some Spending Money.png",
        "3 - Neutral.png",
        "4 - Anxious.png",
        "5 - Over budget Sad.png",
        "6 - Max Overbudget Dead.png",
    ]
    image_url = f"{config.GITHUB_PAGES_URL}{file_names[section]}"
    logging.debug(f"Determined image URL: {image_url}")
    return image_url

def find_image_block(notion, blocks):
    """Recursively search for an image block within given blocks."""
    for block in blocks:
        if block['type'] == 'image':
            return block['id']
        if 'children' in block:
            image_block_id = find_image_block(notion, block['children'])
            if image_block_id:
                return image_block_id
        # Fetch children blocks if not already present
        if block.get('has_children'):
            response = notion.blocks.children.list(block_id=block['id'])
            children_blocks = response['results']
            image_block_id = find_image_block(notion, children_blocks)
            if image_block_id:
                return image_block_id
    return None

def update_image_block(notion, page_id, image_url):
    """Update the image block in the Notion page."""
    logging.debug(f"Updating image block for page {page_id} with URL {image_url}")
    # Fetch the children blocks of the page
    response = notion.blocks.children.list(block_id=page_id)
    blocks = response['results']

    # Find the image block
    image_block_id = find_image_block(notion, blocks)
    if image_block_id:
        try:
            # Update the image block with the new image URL
            notion.blocks.update(
                block_id=image_block_id,
                image={"external": {"url": image_url}}
            )
            logging.info(f"Image block {image_block_id} updated successfully for page {page_id}")
        except Exception as e:
            logging.error(f"Failed to update image block {image_block_id} for page {page_id}: {e}")
    else:
        logging.warning(f"No image block found for page {page_id}")

def process_page(page):
    """Process a single Notion page."""
    logging.debug(f"Processing page: {page['page_id']}")
    notion = notion_clients[page["account_key"]]
    progress = get_monthly_progress(notion, page["database_id"])
    if progress is not None:
        image_url = determine_image(progress)
        update_image_block(notion, page["page_id"], image_url)
    else:
        logging.warning(f"No progress found for page: {page['page_id']}")

def main():
    """Main function to process all pages."""
    logging.debug("Starting main function")
    threads = []
    for page in config.PAGES:
        logging.debug(f"Starting thread for page: {page['page_id']}")
        thread = threading.Thread(target=process_page, args=(page,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    logging.debug("All threads completed")

if __name__ == "__main__":
    main()
