from typing import Union

import os
import yaml
import subprocess
import fake_reporter as reporter
import time

from models import StepResult, ChallengeResult, ChallengeError

class ChallengeExecution(object):
    def __init__(self, challenge_name: str, repository: str):
        self.repository = repository
        self.challenge_name = challenge_name

    def run_step(self, name: str, script_path: str, timeout: int = 10 * 60, get_durtion_from_stdout: bool = False) -> StepResult:
        if not get_durtion_from_stdout:
            start = time.time()
        script_envs = {**os.environ, 'CHALLENGE_NAME': self.challenge_name, 'REPOSITORY_URL': self.repository}

        p = subprocess.Popen('bash {} '.format(script_path),
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=script_envs
                             )

        try:
            p.wait(timeout)
        except subprocess.TimeoutExpired as e:
            return StepResult(name, 9999, timeout, '', 'Timeout')


        stdout_lines = p.stdout.readlines() if p.stdout else ''
        stderr_lines = p.stderr.readlines() if p.stderr else ''

        stdout = ''.join([line.decode("utf-8") for line in stdout_lines])
        stderr = ''.join([line.decode("utf-8") for line in stderr_lines])

        print(stderr)
        print(stdout)

        if not get_durtion_from_stdout:
            elapsed = time.time()
            duration = round(elapsed - start, 3)
        else:
            try:
                print('---------------------------------------------------------------')
                duration = float(stdout)
            except ValueError:
                duration = None
            
        return StepResult(name, int(p.poll()), duration, stdout, stderr)


def run_challenge(challenge_execution: ChallengeExecution) -> Union[ChallengeResult, ChallengeError]:
    print(f"Running challenge {challenge_execution.challenge_name} from repository {challenge_execution.repository}",
          flush=True)

    build_result = challenge_execution.run_step('build', 'scripts/build.sh')
    if build_result.code != 0:
        return ChallengeError('Error in building the image', build_result)

    run_result = challenge_execution.run_step('run', 'scripts/run_in_file_program.sh', get_durtion_from_stdout=True)
    # run_result = challenge_execution.run_step('run', 'scripts/runtime_exec_test.sh')
    if run_result.code != 0:
        print(run_result.__dict__)
        return ChallengeError('Error in running the code', run_result)
    else:
        print('result of runtime_exec_test.sh  =>', run_result.stdout)

    validate_result = challenge_execution.run_step('validate', 'scripts/validate.sh', timeout=10)

    challenge_execution.run_step('cleanup', 'scripts/cleanup.sh')

    if validate_result.code != 0:
        return ChallengeError('Error in validating the result', validate_result)

    return ChallengeResult(build_result, run_result, validate_result)

if __name__ == '__main__':
    with open('fake_participants.yml') as participants_stream:
        participants = yaml.load(participants_stream, Loader=yaml.FullLoader)

    with open('challenges.yml') as challenges_stream:
        challenges = yaml.load(challenges_stream, Loader=yaml.FullLoader)

    run_id = int(time.time())
    for challenge in challenges:
        challenge_name = challenge['name']
        reporter.start_round(run_id, challenge_name)
        for p in participants:
            repository = p['repository']
            nickname = p['nickname']
            ce = ChallengeExecution(challenge_name, p['repository'])
            result = run_challenge(ce)
            reporter.report(nickname, challenge_name, run_id, result)
            print(result)
        reporter.finish_round(run_id, challenge_name)
