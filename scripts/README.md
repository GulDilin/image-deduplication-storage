# Scripts for hash functions testing

`get_images_size` - Script for get stats for hash algs and unique images amount find by each alg

```shell
usage: get_images_size.py [-h] [--recursive] [--dir [path/to/dir ...]]
                          [--hash-alg [alg_name ...]] [--except-prefix [prefix ...]]
                          [--extention [ext ...]] [--stop-amount <integer>]
                          [--dir-diff [key=dir_number ...]]
                          [--dir-diff-ignore [dir_name ...]] [--copy-tested]
                          [--copy-tested-dir COPY_TESTED_DIR]

Load used and unused images from ums

options:
  -h, --help            show this help message and exit
  --recursive, -r       Recursive images searching
  --dir [path/to/dir ...], -d [path/to/dir ...]
                        Dir where find images
  --hash-alg [alg_name ...], -ha [alg_name ...]
                        Hash algorithms
  --except-prefix [prefix ...]
                        File prefixes that will be ignored while check process
  --extention [ext ...], -e [ext ...]
                        Image files extentions that will be check (for example 'jpg')
  --stop-amount <integer>, -sa <integer>
                        Maximum amount of images
  --dir-diff [key=dir_number ...], -dd [key=dir_number ...]
                        Specified key to count amount of images that are different with
                        another only by one part of dir (Specified by number).
  --dir-diff-ignore [dir_name ...], -ddi [dir_name ...]
                        Specified dirs that will be deleted from path in check process
  --copy-tested         Copy tested images to dir
  --copy-tested-dir COPY_TESTED_DIR
                        Copy tested images to dir
```

`hash` - script to get hash value for some image (need to edit hash.py file)

`hashlib_test` - script for generate functions for testing with hashlib

`imagehash_test` - script for generate functions for testing with imagehash

`images_size_test_new.py` - Script for get hash algs performance statistics

- Before use need to add argument to `HashAlgTester` in `images_size_test_new.py`
```shell
### here import functions dict from hashlib_test or imagehash_test
HashAlgTester(hash_functions=functions)
```

```shell
usage: images_size_test.py [-h] [--recursive] [--dir [path/to/dir ...]] [--hash-alg [<alg_name> ...]]
                               [--extention [ext ...]] [--limit <integer>]

Collect images hash algs performance stats

options:
  -h, --help            show this help message and exit
  --recursive, -r       Recursive images searching
  --dir [path/to/dir ...], -d [path/to/dir ...]
                        Dir with images
  --hash-alg [<alg_name> ...], -ha [<alg_name> ...]
                        Hash algorithms
  --extention [ext ...], -e [ext ...]
                        Image files extentions that will be check (for example 'jpg')
  --limit <integer>     Maximum amount of images
```