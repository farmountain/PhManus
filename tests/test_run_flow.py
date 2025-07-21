import argparse

import pytest

import run_flow


def test_validate_plan_id_valid():
    assert run_flow._validate_plan_id("Plan_1-2") == "Plan_1-2"


def test_validate_plan_id_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        run_flow._validate_plan_id("bad id!")


def test_parse_args_plan_id():
    args = run_flow.parse_args(["task", "--plan-id", "ABC123"])
    assert args.plan_id == "ABC123"


@pytest.mark.sit
def test_parse_args_verbose():
    args = run_flow.parse_args(["do", "--verbose"])
    assert args.verbose


@pytest.mark.uat
def test_parse_args_list_tools():
    args = run_flow.parse_args(["something", "--list-tools"])
    assert args.list_tools
