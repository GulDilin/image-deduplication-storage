import argparse
import os
import logging
import traceback
import time

import utils


from dataclasses import dataclass, field


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')


@dataclass
class HashAlgTester:
    total_size_bytes: int = 0
    total_size_by_alg: dict = field(default_factory=dict)
    hashes_dict: dict = field(default_factory=dict)
    hash_functions: dict = field(default_factory=dict)
    total_tested_files: int = 0
    args = None
    benchmark_stats_by_alg: dict = field(default_factory=dict)

    def __post_init__(self):
        self.parse_arguments()
        for alg in self.args.hash_algs:
            self.benchmark_stats_by_alg[alg] = {
                "min": -1,
                "max": 0,
                "sum": 0,
                "amount": 0,
                "errors": 0
            }
            self.total_size_by_alg[alg] = 0
            self.hashes_dict[alg] = set()

    def is_limit_over(self):
        return self.args.limit is not None and \
         self.total_tested_files >= self.args.limit

    def run(self):
        for directory in self.args.dirs:
            if self.is_limit_over():
                return
            self.test_dir(directory)

    def test_dir(self, path):
        for file in os.scandir(path):
            if self.is_limit_over():
                return
            if self.args.recursive and file.is_dir():
                self.test_dir(file.path)
            else:
                self.test_file(file.path)

    def test_file(self, path):
        if utils.get_file_type(path) \
            not in self.args.allowed_extentions:
            return
        self.total_amount += 1
        self.test_file_hash_algs(path)

    def test_file_hash_algs(self, path):
        self.total_size += os.path.getsize(path)
        for alg in self.args.hash_algs:
            hash_value = self.benchmark(alg, path)
            if hash_value not in self.hashes_dict[alg]:
                self.total_size_by_alg[alg] += os.path.getsize(path)
            self.hashes_dict[alg].add(hash_value)

    def benchmark(self, alg, path):
        return_value = None
        is_error = False
        start = time.time()
        try:
            return_value = self.hash_functions[alg](path)
        except KeyboardInterrupt as e:
            raise e
        except BaseException:
            logging.error(traceback.format_exc())
            is_error = True
        end = time.time()
        duration = (end - start) * 1000
        cur = self.benchmark_stats_by_alg[alg]
        cur["max"] = max(cur["max"], duration)
        cur["min"] = duration if cur["min"] < 0 else min(cur["min"], duration)
        cur["sum"] = sum([cur["sum"], duration])
        cur["amount"] += 1
        if is_error:
            cur["errors"] += 1
        return return_value

    def log_benchmark_stat(self):
        for alg, stat in self.benchmark_dict.items():
            avg = stat["sum"] / stat["amount"]
            logging.info("HASH {} statistic".format(alg))
            logging.info("min: {} ms".format(stat["min"]))
            logging.info("max: {} ms".format(stat["max"]))
            logging.info("avg: {} ms".format(avg))
            logging.info("sum: {} ms".format(stat["sum"]))
            logging.info("errors: {}\n".format(stat["errors"]))

    def log_size_stat(self):
        for alg, size in self.total_size_by_alg.items():
            hr_size = utils.approximate_size(size)
            logging.info(f"alg: {alg:10s} size: {hr_size}")

    def log_amount_stat(self):
        logging.info("Total images amount: {}".format(self.total_tested_files))
        for alg, hashes_set in self.hashes_dict.items():
            logging.info(f"Amount of unique images by {alg} hash: {len(hashes_set)}")

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Collect images hash algs performance stats")
        parser.add_argument('--recursive', '-r',
                            dest="is_recursive",
                            action="store_true",
                            required=False,
                            default=False,
                            help="Recursive images searching")
        parser.add_argument('--dir', "-d",
                            dest="dirs",
                            nargs="*",
                            required=False,
                            default=["."],
                            metavar="path/to/dir",
                            help="Dir with images")
        parser.add_argument('--hash-alg', "-ha",
                            dest="hash_algs", nargs="*",
                            type=utils.valid_hash_func_name,
                            required=False,
                            default=['md5', 'md5-image-png'],
                            metavar="<alg_name>",
                            help="Hash algorithms")
        parser.add_argument('--extention', '-e',
                            dest="extentions",
                            nargs="*",
                            required=False,
                            default=['jpg', 'png'],
                            metavar="ext",
                            help="Image files extentions that will be check (for example 'jpg') ")
        parser.add_argument('--limit',
                            dest="limit",
                            type=int,
                            required=False,
                            metavar="<integer>",
                            help="Maximum amount of images")
        self.args = parser.parse_args()


@utils.execution_time
def main():
    ### Add arg hash_functions below
    tester = HashAlgTester()

    try:
        tester.run()
    except BaseException:
        logging.error("Exception: {}".format(traceback.format_exc()))

    tester.log_benchmark_stat()
    tester.log_amount_stat()
    tester.log_size_stat()


if __name__ == '__main__':
    main()
