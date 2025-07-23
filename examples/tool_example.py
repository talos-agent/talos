from __future__ import annotations

from talos.tools import SimpleSupervisor, get_current_time
from talos.tools.supervised_tool import SupervisedTool


def main():
    """
    An example of how to use the SupervisedTool.
    """
    # Create a supervisor
    supervisor = SimpleSupervisor()

    # Create a tool
    tool = get_current_time
    print(f"Tool: {tool.name}")

    # Create a supervised tool
    supervised_tool = SupervisedTool(
        tool=tool,
        supervisor=supervisor,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        messages=[],
    )

    # The first call should be approved
    print("First call (should be approved):")
    result = supervised_tool.invoke({})
    print(f"Result: {result}")

    # The second call should be denied
    print("\nSecond call (should be denied):")
    result = supervised_tool.invoke({})
    print(f"Result: {result}")

    # The third call should be approved
    print("\nThird call (should be approved):")
    result = supervised_tool.invoke({})
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
