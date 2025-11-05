"""
Babson Events Scraper Module

This module provides functions to scrape event information from the Babson College
events page and save the data to CSV format.

Usage:
    from babson_scraper import scrape_babson_events, save_events_to_csv
    
    # Scrape events
    events = scrape_babson_events()
    
    # Save to CSV
    save_events_to_csv(events, 'my_events.csv')
"""

import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_babson_events(verbose=True, delay=1):
    """
    Scrapes all events from the Babson College events page.
    
    Args:
        verbose (bool): If True, prints progress messages. Default is True.
        delay (float): Delay in seconds between page requests. Default is 1.
    
    Returns:
        list: A list of dictionaries containing event information with keys:
              'title', 'start_date', 'end_date', 'start_time', 'end_time', 
              'location', 'link'
    
    Raises:
        requests.RequestException: If there's an error fetching the webpage.
    """
    base_url = "https://www.babson.edu/about/events/"
    all_events = []
    page = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    if verbose:
        print("Starting to scrape Babson events...")
    
    while True:
        # Construct URL for current page
        url = f"{base_url}?search=all&categories%5B%5D=All"
        if page > 1:
            url += f"&page={page}"
        
        if verbose:
            print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            events = soup.find_all('li', class_='event-item')
            
            if not events:
                if verbose:
                    print(f"No more events found on page {page}. Stopping.")
                break
            
            # Extract information from each event
            for event in events:
                event_data = _extract_event_data(event)
                all_events.append(event_data)
            
            if verbose:
                print(f"Found {len(events)} events on page {page}")
            
            # Check if there's a next page
            pagination = soup.find('ul', class_='pagination')
            if not pagination or not pagination.find('a', title=lambda x: x and 'Page ›' in x):
                break
            
            page += 1
            time.sleep(delay)
            
        except requests.RequestException as e:
            if verbose:
                print(f"Error fetching page {page}: {e}")
            raise
    
    if verbose:
        print(f"\nTotal events scraped: {len(all_events)}")
    
    return all_events


def _extract_event_data(event):
    """
    Helper function to extract data from a single event element.
    
    Args:
        event: BeautifulSoup element containing event information
    
    Returns:
        dict: Dictionary containing extracted event data
    """
    event_data = {}
    
    # Get event title
    title_elem = event.find('p', class_='title')
    event_data['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
    
    # Get event dates
    date_stamps = event.find_all('div', class_='date-stamp')
    if len(date_stamps) == 1:
        event_data['start_date'] = _format_date(date_stamps[0])
        event_data['end_date'] = event_data['start_date']
    elif len(date_stamps) >= 2:
        event_data['start_date'] = _format_date(date_stamps[0])
        event_data['end_date'] = _format_date(date_stamps[1])
    else:
        event_data['start_date'] = 'N/A'
        event_data['end_date'] = 'N/A'
    
    # Get event time
    time_listings = event.find_all('span', class_='datelisting')
    if len(time_listings) >= 2:
        event_data['start_time'] = time_listings[0].get_text(strip=True)
        event_data['end_time'] = time_listings[1].get_text(strip=True)
    elif len(time_listings) == 1:
        event_data['start_time'] = time_listings[0].get_text(strip=True)
        event_data['end_time'] = 'N/A'
    else:
        event_data['start_time'] = 'N/A'
        event_data['end_time'] = 'N/A'
    
    # Get event location
    location_icon = event.find('span', class_='fa-map-marker')
    if location_icon and location_icon.next_sibling:
        event_data['location'] = location_icon.next_sibling.strip()
    else:
        event_data['location'] = 'N/A'
    
    # Get event link
    link_elem = event.find('a', class_='find-out-more')
    event_data['link'] = link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'N/A'
    
    return event_data


def _format_date(date_stamp):
    """
    Helper function to format a date from a date stamp element.
    
    Args:
        date_stamp: BeautifulSoup element containing date information
    
    Returns:
        str: Formatted date string (e.g., "Nov 15, 2025")
    """
    month = date_stamp.find('div', class_='month')
    day = date_stamp.find('div', class_='day')
    year = date_stamp.find('div', class_='year')
    
    month_str = month.get_text(strip=True) if month else ''
    day_str = day.get_text(strip=True) if day else ''
    year_str = year.get_text(strip=True) if year else ''
    
    return f"{month_str} {day_str}, {year_str}".strip()


def save_events_to_csv(events, filename='babson_events.csv'):
    """
    Saves a list of events to a CSV file.
    
    Args:
        events (list): List of event dictionaries from scrape_babson_events()
        filename (str): Output CSV filename. Default is 'babson_events.csv'
    
    Returns:
        bool: True if save was successful, False otherwise
    
    Raises:
        IOError: If there's an error writing to the file
    """
    if not events:
        print("Warning: No events to save.")
        return False
    
    fieldnames = ['title', 'start_date', 'end_date', 'start_time', 
                  'end_time', 'location', 'link']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)
        
        print(f"Successfully saved {len(events)} events to {filename}")
        return True
    
    except IOError as e:
        print(f"Error saving to CSV: {e}")
        raise


def scrape_and_save(filename='babson_events.csv', verbose=True):
    """
    Convenience function that scrapes events and saves them to CSV in one call.
    
    Args:
        filename (str): Output CSV filename. Default is 'babson_events.csv'
        verbose (bool): If True, prints progress messages. Default is True.
    
    Returns:
        list: The scraped events list
    """
    events = scrape_babson_events(verbose=verbose)
    save_events_to_csv(events, filename)
    return events


# Example usage when run as a script
if __name__ == "__main__":
    # Scrape and save events
    events = scrape_and_save()
    
    # Print sample
    if events:
        print("\n--- Sample events ---")
        for i, event in enumerate(events[:3], 1):
            print(f"\nEvent {i}:")
            print(f"  Title: {event['title']}")
            print(f"  Dates: {event['start_date']} to {event['end_date']}")
            print(f"  Time: {event['start_time']} - {event['end_time']}")
            print(f"  Location: {event['location']}")