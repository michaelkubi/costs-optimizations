import argparse
import sys

import requests
import dataframe_image as dfi
import pandas as pd
import slack_sdk
import os

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
    # fields = ["cpuEfficiency", "ramEfficiency", "totalEfficiency", "cpuCost", "ramCost", "totalCost"]
    fields = ["cpuEfficiency", "ramEfficiency", "totalEfficiency", "totalCost"]

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

    df = pd.DataFrame(data).T
    df.head()


def slack_result_image_to_slack(data):
    """
    Sends a result image to a Slack channel.

    Parameters:
    - image_url (str): URL of the image to send to Slack
    - slack_token (str): Slack API token
    - slack_channel (str): Slack channel to send the image to
    """
    df = pd.DataFrame(data).T
    dfi.export(df, 'dataframe.png')

    slack_token = os.getenv("SLACK_API_TOKEN")

    client = slack_sdk.WebClient(token=slack_token)

    try:
        response = client.files_upload(
            channels="D05T1HF3MNZ",
            file='./dataframe.png',
            initial_comment="Here is the detailed stats of the namespaces."
        )
    except Exception as e:
        print(f"Failed to send image to Slack: {e}")
        sys.exit(1)

    if not response["ok"]:
        print(f"Failed to send image to Slack: {response['error']}")


def prettier_data(data):
    """

    :param data:
    :return:
    """

    result = {}
    for namespace, metrics in data:

        cpu_efficiency = metrics['cpuEfficiency'] * 100
        ram_efficiency = metrics['ramEfficiency'] * 100
        total_efficiency = metrics['totalEfficiency'] * 100

        result[namespace] = {
            "cpuEfficiency": f"{cpu_efficiency:.2f}%",
            "ramEfficiency": f"{ram_efficiency:.2f}%",
            "totalEfficiency": f"{total_efficiency:.2f}%",
            "totalCost": f"${metrics['totalCost']:.2f}"
        }
    return result


def query_prometheus(timeout='30s'):
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
            pretty_data = prettier_data(sorted_data)
            slack_result_image_to_slack(pretty_data)
            return pretty_data
        else:
            raise Exception(f"Query failed with status: {data['status']}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":

    if os.getenv("SLACK_API_TOKEN"):
        print("Slack API token found")
        sys.exit(1)

    prometheus_query_results = query_prometheus()
    print("Highest cost namespaces:", prometheus_query_results)
