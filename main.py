import os
from MERToolRunnerFactory import MERToolRunnerFactory
from MERToolRunner import MERToolRunner

if __name__ == '__main__':
    runners = [MERToolRunnerFactory.create_runner(runner_class) for runner_class in MERToolRunner.__subclasses__()]
    for runner in runners:
        runner.prepare_input()
        runner.process_input()
        runner.format_output()
        runner.print_output()
    os.system('./evaluation/run_evaluation.sh')
