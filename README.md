# Terry Fox Progress Tracker

This project tracks the progress of a Notion database and updates an image block in a Notion page based on the progress percentage. The images are hosted on GitHub Pages.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. **Create and activate a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. **Set up GitHub Pages:**

    - Create a GitHub repository named `yourusername.github.io`.
    - Enable GitHub Pages in the repository settings.
    - Upload your images to a directory named `images` in the repository.

2. **Configure the project:**

    - Open `config.py` and set the following variables:

    ```python
    NOTION_API_KEY = "your_notion_api_key"
    GITHUB_PAGES_URL = "https://yourusername.github.io/yourrepository/images/"
    PAGES = [
        {"page_id": "your_page_id", "database_id": "your_database_id"},
        # Add more pages as needed
    ]
    ```

## Usage

1. **Run the script:**

    ```sh
    python TerryFoxCloud.py
    ```

    The script will fetch the progress percentage from the Notion database, determine the appropriate image based on the progress, and update the image block in the Notion page.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
