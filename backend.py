from serpapi import GoogleSearch
import json
from urllib.parse import urlparse

def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def fetch_serp_results(keyword, location, num_results, api_key, user_domains=[]):
    results_data = []
    start = 0
    current_rank = 1

    while len(results_data) < num_results:
        params = {
            "engine": "google",
            "q": keyword,
            "location": location,
            "start": start,
            "api_key": api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        if 'organic_results' not in results:
            break

        for result in results['organic_results']:
            if len(results_data) >= num_results:
                break

            domain = extract_domain(result.get('link', ''))
            is_user_domain = domain in user_domains

            results_data.append({
                "Rank": current_rank,
                "Title": result.get('title', 'N/A'),
                "Meta Description": result.get('snippet', 'N/A'),
                "URL": result.get('link', 'N/A'),
                "IsUserDomain": is_user_domain
            })
            current_rank += 1

        start += len(results['organic_results'])

    return results_data


def fetch_and_save_serp_results(keywords, location, num_results, api_key, user_domains, output_file):
    results_data = {"keywords": keywords, "user_domains": user_domains, "results": {}}
    for keyword in keywords:
        keyword_results = fetch_serp_results(keyword, location, num_results, api_key, user_domains)
        results_data["results"][keyword] = keyword_results

    with open(output_file, 'w') as file:
        json.dump(results_data, file, indent=4)
