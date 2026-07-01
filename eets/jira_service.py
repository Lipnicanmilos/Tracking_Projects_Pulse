# # from jira import JIRA
# # from dotenv import load_dotenv
# # import os

# # load_dotenv()

# # server = os.getenv("JIRA_SERVER")
# # email = os.getenv("JIRA_EMAIL")
# # api_token = os.getenv("JIRA_API_TOKEN")

# # def get_jira_connection():
# #     os.environ['HTTPS_PROXY'] = 'http://proxy.example.local:3128'
# #     return JIRA(server=server, basic_auth=(email, api_token))



# import os
# import requests
# from dotenv import load_dotenv
# from requests.auth import HTTPBasicAuth

# load_dotenv()

# # Jira Cloud nastavenia
# JIRA_BASE_URL = os.getenv("JIRA_SERVER")  # napr. https://example.atlassian.net
# EMAIL = os.getenv("JIRA_EMAIL")
# API_TOKEN = os.getenv("JIRA_API_TOKEN")

# # Proxy nastavenie (ak je potrebné)
# os.environ['HTTP_PROXY'] = ''
# os.environ['HTTPS_PROXY'] = ''
# os.environ['NO_PROXY'] = 'login.microsoftonline.com,sharepoint.com'

# def search_jira_issues(jql, max_results=50):
#     url = f"{JIRA_BASE_URL}/rest/api/3/search"
#     payload = {
#         "jql": jql,
#         "maxResults": max_results
#     }

#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#         "X-Beta-API": "Jira-Search"
#     }

#     try:

#         response = requests.get(
#             url,
#             params=payload,
#             auth=HTTPBasicAuth(EMAIL, API_TOKEN),
#             headers=headers,
#             proxies={}
#         )


#         response.raise_for_status()
#         return response.json()

#     except requests.exceptions.RequestException as req_error:
#         print(f"Chyba pri volaní API: {req_error}")
#         return {}


# def get_projects():
#     url = f"{JIRA_BASE_URL}/rest/api/3/project/search"
    
#     response = requests.get(
#         url,
#         auth=HTTPBasicAuth(EMAIL, API_TOKEN),
#         headers={"Accept": "application/json"}
#     )
#     response.raise_for_status()
#     return response.json()
