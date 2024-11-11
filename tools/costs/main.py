import argparse
import requests


def hello_world(name: str):
    print(f"Hello, {name}!")


def query_prometheus(prometheus_url, query, timeout='30s'):
    """
    Queries Prometheus for a given metric.

    Parameters:
    - prometheus_url (str): Base URL of Prometheus server (e.g., 'http://localhost:9090')
    - query (str): PromQL query to send to Prometheus
    - timeout (str): Query timeout, e.g., '30s' (default is '30s')

    Returns:
    - JSON response from Prometheus with the query results
    """
    url = f"{prometheus_url}/api/v1/query"
    params = {'query': query, 'timeout': timeout}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for failed requests
        data = response.json()
        if data['status'] == 'success':
            return data['data']['result']
        else:
            raise Exception(f"Query failed with status: {data['status']}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print hello {name}!")
    parser.add_argument("name", help="Name to say hello to")

    # Parse command-line arguments
    args = parser.parse_args()

    # Get coordinates for the given city
    name = args.name

    # Get env vars
    prometheus_url = 'http://prometheus-server.prometheus-server:9090'
    query = 'up{job="prometheus"}'

    prometheus_query_results = query_prometheus(prometheus_url, query)
    print("Prometheus query results:", prometheus_query_results)
