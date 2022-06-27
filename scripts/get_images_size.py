import argparse
import os
import logging
import traceback
import time

import utils

import shutil


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

algs_sum_size = {"base": 0}
algs_sum_hashes = {}
g_args = None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Load used and unused images from ums")

    parser.add_argument('--recursive', '-r', dest="is_recursive", action="store_true", required=False, default=False,
                        help="Recursive images searching")
    parser.add_argument('--dir', "-d", dest="dirs", nargs="*", required=False, default=["."],
                        metavar="path/to/dir", help="Dir where find images")
    parser.add_argument('--hash-alg', "-ha", dest="hash_algs", nargs="*",
                        type=utils.valid_hash_func_name, required=False,
                        default=['md5', 'md5-image-png'], metavar="alg_name", help="Hash algorithms")
    parser.add_argument('--except-prefix', dest="except_prefixes", nargs="*", required=False, default=[],
                        metavar="prefix", help="File prefixes that will be ignored while check process")
    parser.add_argument('--extention', '-e', dest="extentions", nargs="*", required=False, default=['jpg', 'png'],
                        metavar="ext", help="Image files extentions that will be check (for example 'jpg') ")
    parser.add_argument('--stop-amount', '-sa', dest="stop_amount", type=int, required=False,
                        metavar="<integer>", help="Maximum amount of images")
    parser.add_argument('--dir-diff', '-dd', dest="dirs_diff", nargs="*", type=utils.valid_key_int_value,
                        required=False, default=[], metavar="key=dir_number",
                        help="Specified key to count amount of images that are different with another only by one part of dir (Specified by number).")
    parser.add_argument('--dir-diff-ignore', '-ddi', dest="dirs_diff_ignore", nargs="*", required=False,
                        default=[], metavar="dir_name", help="Specified dirs that will be deleted from path in check process")
    parser.add_argument('--copy-tested', dest="copy_tested", action="store_true", required=False, default=False,
                        help="Copy tested images to dir")
    parser.add_argument('--copy-tested-dir', dest="copy_tested_dir", required=False, default='tested',
                        help="Copy tested images to dir")
    return parser.parse_args()


def benchmark(func, benchmark_dict, alg):
    def wrapper(*args, **kwargs):
        return_value = None
        is_error = False
        start = time.time()

        try:
            return_value = func(*args, **kwargs)
        except KeyboardInterrupt as e:
            raise e
        except:
            logging.error(traceback.format_exc())
            is_error = True

        end = time.time()
        duration = (end - start) * 1000

        if alg not in benchmark_dict:
            benchmark_dict[alg] = {
                "min": duration,
                "max": 0,
                "sum": 0,
                "amount": 0,
                "errors": 0
            }

        cur = benchmark_dict[alg]
        cur["max"] = max(cur["max"], duration)
        cur["min"] = min(cur["min"], duration)
        cur["sum"] = sum([cur["sum"], duration])
        cur["amount"] += 1

        if is_error:
            cur["errors"] += 1

        return return_value
    return wrapper


def log_benchmark_stat(benchmark_dict):
    for alg, stat in benchmark_dict.items():
        avg = stat["sum"] / stat["amount"]
        logging.info("HASH {} statistic".format(alg))
        logging.info("min: {} ms".format(stat["min"]))
        logging.info("max: {} ms".format(stat["max"]))
        logging.info("avg: {} ms".format(avg))
        logging.info("sum: {} ms".format(stat["sum"]))
        logging.info("errors: {}\n".format(stat["errors"]))


def log_size_stat():
    for alg, size in algs_sum_size.items():
        hr_size = utils.approximate_size(size)
        logging.info(f"alg: {alg:10s} size: {hr_size}")


def do_dir_diff_alg(hash_alg_path_dict, dirs_diff, dirs_diff_ignore):
    for dir_kv in dirs_diff:
        key = dir_kv["key"]
        value = dir_kv["value"]

        repeats = 0
        for images in hash_alg_path_dict.values():
            images = [utils.rm_el_from_str_path(path, value, dirs_diff_ignore) for path in images]
            repeats += utils.find_amount_of_similar_elements(images)

        dir_kv["repeats"] = repeats
        logging.info("Same images diffs only by {}: {}".format(key, repeats))


def do_dir_diffs(hash_path_dict, dirs_diff, dirs_diff_ignore):
    if not dirs_diff:
        return

    for alg, hash_alg_path_dict in hash_path_dict.items():
        logging.info("Same images stat for {}".format(alg))
        do_dir_diff_alg(hash_alg_path_dict, dirs_diff, dirs_diff_ignore)
        logging.info("")


def add_hash_path_info(hash_path_dict, dirs_diff, hash_alg, hash_value, path):
    if not dirs_diff:
        return

    if hash_alg not in hash_path_dict:
        hash_path_dict[hash_alg] = {}

    if hash_value not in hash_path_dict[hash_alg]:
        hash_path_dict[hash_alg][hash_value] = []

    hash_path_dict[hash_alg][hash_value].append(path)


def add_file_stat(path, hash_alg, hash_value):
    if hash_alg not in algs_sum_hashes:
        algs_sum_hashes[hash_alg] = set()
    if hash_alg not in algs_sum_size:
        algs_sum_size[hash_alg] = 0
    if hash_value not in algs_sum_hashes[hash_alg]:
        algs_sum_size[hash_alg] += os.path.getsize(path)
    algs_sum_hashes[hash_alg].add(hash_value)


def do_hash_algs(path, hash_dict, hash_algs, benchmark_dict, hash_path_dict, dirs_diff):
    logging.debug("Start check hashes for file: {}, hashes: {}".format(path, hash_algs))
    algs_sum_size["base"] += os.path.getsize(path)
    for hash_alg in hash_algs:
        hash_value = benchmark(utils.hash_funcs[hash_alg], benchmark_dict, hash_alg)(path)
        add_file_stat(path, hash_alg, hash_value)
        hash_dict[hash_alg].update([hash_value])
        add_hash_path_info(hash_path_dict, dirs_diff, hash_alg, hash_value, path)


def do_file(path, hash_dict, hash_algs, benchmark_dict, hash_path_dict, dirs_diff, except_prefixes, extentions, copy_tested, copy_tested_dir):
    logging.debug("Start do file: {}, type: {}".format(path, utils.get_file_type(path)))

    for exc_prefix in except_prefixes:
        if path.startswith(exc_prefix):
            logging.debug("Ignore file because of prefix: {}".format(path))
            return
    if utils.get_file_type(path) in extentions:
        do_hash_algs(path, hash_dict, hash_algs, benchmark_dict, hash_path_dict, dirs_diff)
        hash_dict["total_amount"] += 1
        if copy_tested:
            if not os.path.exists(copy_tested_dir):
                os.makedirs(copy_tested_dir)
            shutil.copyfile(path, f'{copy_tested_dir}/{hash_dict["total_amount"]}.{utils.get_file_type(path)}')


def do_dir(path, hash_dict, hash_algs, benchmark_dict, hash_path_dict, dirs_diff, recursive, except_prefixes, extentions, stop_amount, copy_tested, copy_tested_dir):
    logging.debug("Start do dir: {}".format(path))

    for file in os.scandir(path):
        if stop_amount is not None and hash_dict["total_amount"] >= stop_amount:
            break
        logging.debug("Found file: {}".format(file))
        if recursive and file.is_dir():
            do_dir(file.path, hash_dict, hash_algs, benchmark_dict, hash_path_dict, dirs_diff, recursive, except_prefixes, extentions, stop_amount, copy_tested, copy_tested_dir)
        else:
            do_file(file.path, hash_dict, hash_algs, benchmark_dict, hash_path_dict, dirs_diff, except_prefixes, extentions, copy_tested, copy_tested_dir)


@utils.execution_time
def main():
    args = parse_arguments()

    benchmark_dict = {}
    hash_path_dict = {}
    hash_dict = {hash_alg: set() for hash_alg in args.hash_algs}
    hash_dict["total_amount"] = 0
    logging.info("Start check images")

    try:
        for directory in args.dirs:
            if args.stop_amount is not None and hash_dict["total_amount"] >= args.stop_amount:
                break
            do_dir(
                directory,
                hash_dict,
                args.hash_algs,
                benchmark_dict,
                hash_path_dict,
                args.dirs_diff,
                args.is_recursive,
                args.except_prefixes,
                args.extentions,
                args.stop_amount,
                args.copy_tested,
                args.copy_tested_dir
            )
    except BaseException:
        logging.error("Exception: {}".format(traceback.format_exc()))

    logging.info("Total images amount: {}".format(hash_dict["total_amount"]))

    for hash_alg in args.hash_algs:
        logging.info("Amount of unique images by {} hash: {}".format(hash_alg, len(hash_dict[hash_alg])))

    logging.info("")
    log_benchmark_stat(benchmark_dict)
    log_size_stat()
    do_dir_diffs(hash_path_dict, args.dirs_diff, args.dirs_diff_ignore)


if __name__ == '__main__':
    main()
