import os
from MERToolRunnerFactory import MERToolRunnerFactory
from MERToolRunner import MERToolRunner

if __name__ == '__main__':
    runner_factory = MERToolRunnerFactory()
    runners = [runner_factory.create_runner(runner_class) for runner_class in MERToolRunner.__subclasses__()]
    for runner in runners:
        runner.process_input()
        runner.format_output()
        runner.print_output()
    os.system('./evaluation/run_evaluation.sh')
