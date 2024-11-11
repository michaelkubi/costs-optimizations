import inspect

from kubiya_sdk.tools.models import Arg, Tool, FileSpec
from kubiya_sdk.tools.registry import tool_registry

from . import main

hello_tool = Tool(
    name="say_hello",
    type="docker",
    image="python:3.12",
    description="Prints hello {name}!",
    args=[Arg(name="name", description="name to say hello to", required=True)],
    content="""
pip install argparse > /dev/null 2>&1
pip install requests > /dev/null 2>&1
python /tmp/main.py "{{ .name }}"
""",
    with_files=[
        FileSpec(
            destination="/tmp/main.py",
            content=inspect.getsource(main),
        ),
        # Add any requirements here if needed
        # FileSpec(
        #     destination="/tmp/requirements.txt",
        #     content="",
        # ),
    ],
)

query_prometheus = Tool(
    name="query_prometheus",
    type="docker",
    image="python:3.11",
    description="Query Prometheus",
    args=[],
    on_build="""
pip install argparse > /dev/null 2>&1
pip install requests > /dev/null 2>&1
python /tmp/main.py
""",
    content="""
python /tmp/main.py
""",
    with_files=[
        FileSpec(
            destination="/tmp/main.py",
            content=inspect.getsource(main),
        ),
    ],
)

tool_registry.register(hello_tool)
tool_registry.register(query_prometheus)

