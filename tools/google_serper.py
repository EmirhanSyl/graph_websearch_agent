import os
import json
from langchain_community.utilities import GoogleSerperAPIWrapper
from utils.helper_functions import load_config
from states.state import AgentGraphState

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')


def format_results(organic_results):

        result_strings = []
        for result in organic_results:
            title = result.get('title', 'No Title')
            link = result.get('link', '#')
            snippet = result.get('snippet', 'No snippet available.')
            result_strings.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n---")
        
        return '\n'.join(result_strings)

def get_google_serper(state:AgentGraphState, plan):
    load_config(config_path)

    plan_data = plan().content
    plan_data = json.loads(plan_data)
    search = plan_data.get("search_term")

    serper = GoogleSerperAPIWrapper(serper_api_key="a00a73c3ac748ff73ffd073637b6dc2b01b4ded9")
    try:
        results = serper.results(search)
        if "organic" in results:
            formatted_results = format_results(results["organic"])
            state = {**state, "serper_response": formatted_results}
            return state
        else:
            return {**state, "serper_response": "No organic results found."}
    except Exception as e:
        return {**state, "serper_response": f"Error occurred: {e}"}
