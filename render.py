import os
import sys

import jinja2
import requests
import yaml
from dotenv import load_dotenv
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

load_dotenv()


REBRICKABLE_API_KEY = os.getenv("REBRICKABLE_API_KEY")
REBRICKABLE_API_BASE = "https://rebrickable.com/api/v3/lego"


def get_set_data(set_num: str, session: requests.Session) -> dict:
    """Fetch set data from Rebrickable API."""
    headers = {"Authorization": f"key {REBRICKABLE_API_KEY}"}

    set_num = set_num + "-1" if "-" not in set_num else set_num

    url = f"{REBRICKABLE_API_BASE}/sets/{set_num}/"

    response = session.get(url, headers=headers)

    if response.status_code == 404:
        raise Exception(f"Set {set_num} not found in Rebrickable")

    response.raise_for_status()
    return response.json()


def enrich_set_data(sets_data: list[dict]) -> list[dict]:
    """Enrich sets data with information from Rebrickable."""
    enriched_data = []

    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429])
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)

    for set_data in sets_data:
        set_num = set_data["code"].strip()  # Remove any whitespace

        logger.info(f"Enriching set {set_num}")

        rebrickable_data = get_set_data(set_num, session)

        set_data["thumbnail_url"] = rebrickable_data["set_img_url"]
        # Note: Rebrickable API doesn't provide direct instruction links
        # We'll keep the existing instructions_url if available
        set_data["instructions_url"] = rebrickable_data["set_url"] + "#bi"
        set_data["name"] = rebrickable_data["name"]

        enriched_data.append(set_data)

    return sorted(enriched_data, key=lambda x: x["name"])


def load_yaml(file_path):
    """Load YAML file and return its contents as a list of dictionaries with codes."""
    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        # Remove duplicates and convert to list of dicts with codes
        unique_codes = {code.strip() for code in data}
        return [{"code": code} for code in sorted(unique_codes)]


def render_template(template_path, output_path, data):
    """Render the template with the provided data and save to output file."""
    # Create a Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(template_path)), autoescape=True
    )

    # Load the template
    template = env.get_template(os.path.basename(template_path))

    # Render the template with the data
    rendered = template.render(site={"pdfs": data})

    # Write the rendered content to the output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)


def main():
    if not REBRICKABLE_API_KEY:
        logger.error("Please set the REBRICKABLE_API_KEY environment variable")
        logger.error("You can get an API key from https://rebrickable.com/api/")
        sys.exit(1)

    # Define paths
    template_path = "index.template.html"
    yaml_path = "pdfs.yml"
    output_path = "index.html"

    # Load the PDF data
    pdfs_data = load_yaml(yaml_path)

    # Enrich data with Rebrickable information
    enriched_data = enrich_set_data(pdfs_data)

    # Render the template
    render_template(template_path, output_path, enriched_data)

    logger.info(f"Successfully rendered {template_path} to {output_path}")


if __name__ == "__main__":
    main()
