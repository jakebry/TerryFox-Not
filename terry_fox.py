import os
import logging
from notion_client import Client
import config  # Import the configuration file

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("notion_script.log"), logging.StreamHandler()]
)

# Configuration
NOTION_API_KEY = config.NOTION_API_KEY
DATABASE_ID = config.DATABASE_ID
PAGE_ID = config.PAGE_ID
GITHUB_PAGES_URL = config.GITHUB_PAGES_URL

# Initialize Notion client
notion = Client(auth=NOTION_API_KEY)

def get_monthly_progress():
    """Retrieve the progress percentage from the Notion database."""
    try:
        logging.debug("Fetching database items from Notion API.")
        response = notion.databases.query(database_id=DATABASE_ID)
        logging.info("Successfully fetched database items.")

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

# Example usage of the function
progress = get_monthly_progress()
if progress is not None:
    logging.info(f"Progress {progress}% falls into section {int(progress // 10)}.")
else:
    logging.error("Progress could not be retrieved. Exiting script.")

def determine_image(progress):
    """Determine the GitHub Pages URL to use based on progress."""
    section = int(progress // 16.7)  # Determine which section the progress falls into
    section = min(section, 5)  # Ensure it does not exceed the maximum index (5)
    logging.info(f"Progress {progress}% falls into section {section}.")

    # Map progress to image file names (replace these with actual file names in your GitHub Pages)
    file_names = [
        "image1.jpg",  # Replace with actual file names
        "image2.jpg",
        "image3.jpg",
        "image4.jpg",
        "image5.jpg",
        "image6.jpg",
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

def update_image_block(image_url):
    """Update the image block in the page with the new image."""
    try:
        logging.debug("Fetching page content to find the image block.")
        blocks = notion.blocks.children.list(PAGE_ID)["results"]
        logging.info(f"Fetched {len(blocks)} blocks from the page.")

        image_block_id = find_image_block(blocks)

        if image_block_id:
            logging.info("Found image block. Updating the image.")
            notion.blocks.update(
                block_id=image_block_id,
                image={"external": {"url": image_url}}  # Correct payload format
            )
            logging.info(f"Successfully updated image block with URL: {image_url}")
        else:
            logging.warning("No image block found on the page.")
    except Exception as e:
        logging.error(f"Error while updating image block: {e}")

def main():
    logging.info("Script started.")

    # Step 1: Get progress percentage
    progress = get_monthly_progress()
    if progress is None:
        logging.error("Progress could not be retrieved. Exiting script.")
        return

    # Step 2: Determine the image URL based on progress
    image_url = determine_image(progress)

    if not image_url:
        logging.error("Image URL could not be determined. Exiting script.")
        return

    # Step 3: Update the image block
    update_image_block(image_url)

    logging.info("Script finished successfully.")

if __name__ == "__main__":
    main()