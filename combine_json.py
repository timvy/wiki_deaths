import os
import json
from datetime import datetime
from override_list import override_list

def extract_language(url):
    return url.split('//')[1].split('.')[0]

def combine_json_files(directory):
    combined_data = {}

    # Get a sorted list of all JSON files in the directory
    filenames = sorted([f for f in os.listdir(directory) if f.endswith("2025.json")])

    for filename in filenames:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for entry in data:
                date = entry['date']
                if date not in combined_data:
                    combined_data[date] = {
                        'date': date,
                        'data': {
                            'deaths': [
                                {
                                    'text': death['text'],
                                    'title': death['pages'][0]['title'],
                                    'description': death['pages'][0].get('description', ''),
                                    'content_url': death['pages'][0]['content_urls']['desktop']['page'],
                                    'language': extract_language(death['pages'][0]['content_urls']['desktop']['page']),
                                    'extract': death['pages'][0].get('extract', '')
                                }
                                for death in entry['data']['deaths']
                                if all(page['title'] not in override_list for page in death['pages'])
                            ]
                        }
                    }
                else:
                    existing_titles = {death['title'] for death in combined_data[date]['data']['deaths']}
                    new_deaths = [
                        {
                            'text': death['text'],
                            'title': death['pages'][0]['title'],
                            'description': death['pages'][0].get('description', ''),
                            'content_url': death['pages'][0]['content_urls']['desktop']['page'],
                            'language': extract_language(death['pages'][0]['content_urls']['desktop']['page']),
                            'extract': death['pages'][0].get('extract', '')
                        }
                        for death in entry['data']['deaths']
                        if all(page['title'] not in existing_titles and page['title'] not in override_list for page in death['pages'])
                    ]
                    for new_death in new_deaths:
                        # Check if the title already exists and if the new entry is in English
                        existing_death = next((d for d in combined_data[date]['data']['deaths'] if d['title'] == new_death['title']), None)
                        if existing_death:
                            if new_death['language'] == 'en':
                                combined_data[date]['data']['deaths'].remove(existing_death)
                                combined_data[date]['data']['deaths'].append(new_death)
                        else:
                            combined_data[date]['data']['deaths'].append(new_death)

    # Convert combined_data to a list and sort by date
    combined_data_list = list(combined_data.values())
    combined_data_list.sort(key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y"))

    output_filepath = os.path.join(directory, 'combined_wikimedia_deaths.json')
    with open(output_filepath, 'w', encoding='utf-8') as output_file:
        json.dump(combined_data_list, output_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    directory = "/Users/tim/wiki_deaths"
    combine_json_files(directory)
