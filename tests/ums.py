import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


from ums_client import create_ums_client
from executeTests import send_machine_info
import core.system_info
import argparse



def test_create_client():
    test_ums_client = create_ums_client("TEST")

    for group in ['Smoke', 'Sanity']:
        r = test_ums_client.get_suite_id_by_name(group)
        assert r.status_code == 200

        env = {
            "hostname": "rpr_cistest_2020",
            "cpu": "Intel Core i5 2 GHz Quad-Core",
            "cpu_count": 4,
            "ram": 16,
            "gpu": "Intel Iris Plus Graphics"
        }

        r = test_ums_client.define_environment(env)
        assert r.status_code == 200

    assert 1 == 1
