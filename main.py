"""
This script pulls events from online events calendars and matches them with your interests, 
giving you customized recommendations for events to go to near you. You can set this up to 
email you at a regular interval with events that are happening soon.

-----TO USE-----

1. Paste your filled out interests document into interests.txt
2. Fill in the site you want to scrape from in the config options below
3. Enter your OpenAI API key, email, and email app password in a .env file

    OPENAI_API_KEY="api_key_here"
    MY_EMAIL = "your.email@gmail.com"
    EMAIL_APP_PASSWORD = "your_app_password"

"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import scrapers
import email_me


# CONFIG
SITE_TO_SCRAPE = "babson" # Set the site you want to pull events from. See table below for options


# Available sites
sites = {
    # The Babson events calendar
    "babson": {"scraper": scrapers.scrape_babson_events, "events_data": "babson_events_test.csv"}
}


# --------------------------------------------------------------------------------------------------

# Run web scraper and save data to csv
events = sites[SITE_TO_SCRAPE]["scraper"]()
scrapers.save_events_to_csv(events, sites[SITE_TO_SCRAPE]["events_data"])


# Upload csv and interests document with prompt to openai api
client = OpenAI()

events = client.files.create(
    file=open(sites[SITE_TO_SCRAPE]["events_data"], "rb"),
    purpose="list_of_events"
)
interests = client.files.create(
    file=open("interests.txt", "rb"),
    purpose="my_interests"
)

response = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "I would like you to look through the list of events below and pick out ones I might find interesting. To help, I have filled out a document indicating what types of things I am interested in and information that might be relevant to choosing an event to go to. The events are pulled from an events calendar near me.",
                },
                {
                    "type": "input_file",
                    "file_id": interests.id,
                },
                {
                    "type": "input_file",
                    "file_id": events.id,
                },
            ]
        }
    ]
)

print(response.output_text)
with open("output.txt", "w", encoding='utf-8') as file:
    file.write(response.output_text)



# Email the result

# Load environment variables from .env file
load_dotenv()

MY_EMAIL = os.getenv('MY_EMAIL')
EMAIL_APP_PASSWORD = os.getenv('EMAIL_APP_PASSWORD')

email_me.send_txt_file("output.txt", MY_EMAIL, MY_EMAIL, EMAIL_APP_PASSWORD)
