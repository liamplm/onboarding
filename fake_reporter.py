from typing import Union
import json
import os

from models import ChallengeResult, ChallengeError

results = {}

def write_report():
    with open('result.json', 'w+') as result_stream:
        result_stream.write(json.dumps(results, default=lambda o: o.__dict__, indent=4))
        result_stream.close()


def report(nickname: str, challenge_name: str, run_id: str, result: Union[ChallengeResult, ChallengeError]):

    print('====>', result.__dict__, result)
    # request = ReportRequest(nickname, challenge_name, run_id, result)
    # request_json = json.dumps(request.__dict__, default=lambda o: o.__dict__, indent=4)

    results[nickname] = {
        challenge_name: result.__dict__
    }



def start_round(round_id: int, challenge_name: str):
    pass

def finish_round(round_id: int, challenge_name: str):
    write_report()
    pass

