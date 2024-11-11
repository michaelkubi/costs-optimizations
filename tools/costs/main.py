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

    cost_metrics_url = "http://localhost:9090/model/allocation/compute"
    params = {'window': '7d', 'aggregate': 'namespace', 'includeIdle': 'true', 'step': '1d', 'accumulate': 'true'}

    try:
        response = requests.get(cost_metrics_url, params=params)
        response.raise_for_status()  # Raise an error for failed requests
        data = response.json()
        if data['status'] == 'success':
            return data
        else:
            raise Exception(f"Query failed with status: {data['status']}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    # Get env vars
    prometheus_url = 'http://prometheus-server.prometheus-system'
    query = 'up{job="prometheus"}'

    prometheus_query_results = query_prometheus(prometheus_url, query)
    print("Prometheus query results:", prometheus_query_results)

