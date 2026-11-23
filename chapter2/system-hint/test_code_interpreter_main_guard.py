"""Regression: code_interpreter must run snippets as a script, so a
`if __name__ == "__main__":` block executes instead of being silently skipped."""

from agent import SystemHintAgent, SystemHintConfig


def make_agent():
    config = SystemHintConfig(
        enable_timestamps=False,
        enable_tool_counter=False,
        enable_todo_list=False,
        enable_detailed_errors=False,
        enable_system_state=False,
        save_trajectory=False,
    )
    return SystemHintAgent(api_key="test-key", provider="kimi", config=config, verbose=False)


def test_main_guard_body_runs():
    code = (
        "def main():\n"
        "    print(sum(range(5)))\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    main()\n"
    )
    result = make_agent()._tool_code_interpreter(code)
    assert result["success"] is True
    assert result["stdout"] == "10\n"


def test_snippet_sees_main_as_its_module_name():
    result = make_agent()._tool_code_interpreter("print(__name__)")
    assert result["stdout"] == "__main__\n"


def test_module_level_scoping_still_works():
    # The case fixed by the explicit namespace: functions see top-level names.
    code = "x = 5\ndef double():\n    return x * 2\nprint(double())\n"
    result = make_agent()._tool_code_interpreter(code)
    assert result["stdout"] == "10\n"


def test_snippets_do_not_share_state():
    agent = make_agent()
    agent._tool_code_interpreter("leaked = 1")
    result = agent._tool_code_interpreter("print('leaked' in globals())")
    assert result["stdout"] == "False\n"
