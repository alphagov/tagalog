from ..helpers import assert_equal
from subprocess import Popen, PIPE
import json

def test_json():
    p = Popen("echo '{\"@fields\": {\"handbags\": \"great\", \"why\": \"because\"}}' | logship --no-stamp --json -s stdout",
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal({'@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))
