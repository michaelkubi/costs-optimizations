import argparse
import requests


def hello_world(name: str):
    print(f"Hello, {name}!")


def filter_namespace_data(data):
    """
    Filters the input data for all namespaces found in the structure and retains specified fields.

    Parameters:
    - data: The input data containing metrics for various namespaces.
    - fields: List of fields to keep in the output.

    Returns:
    - JSON structure with the filtered data.
    """
    fields = ["cpuEfficiency", "ramEfficiency", "totalEfficiency", "cpuCost", "ramCost", "totalCost"]

    result = {
        namespace: {field: metrics.get(field) for field in fields}
        for namespace, metrics in data[0].items() if metrics.get("properties", {}).get("namespace")
    }
    return result


def print_pandas_table(data):
    """
    Prints the input data as a pandas DataFrame.

    Parameters:
    - data: The input data to print as a pandas DataFrame.
    """
    import pandas as pd

    df = pd.DataFrame(data).T
    print(df)


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

    cost_metrics_url = "http://opencost.opencost:9090/model/allocation/compute"
    params = {'window': '7d', 'aggregate': 'namespace', 'includeIdle': 'true', 'step': '1d', 'accumulate': 'true'}

    try:
        response = requests.get(cost_metrics_url, params=params)
        response.raise_for_status()  # Raise an error for failed requests
        data = response.json()
        if data['status'] == 'success':
            structured_data = filter_namespace_data(data['data'])
            sorted_data = sorted(structured_data.items(), key=lambda item: item[1]['totalCost'], reverse=True)
            print_pandas_table(sorted_data)
            return
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

