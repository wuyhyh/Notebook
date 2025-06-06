import os
import sys
import threading
import concurrent.futures
from time import sleep

NUM_THREADS = 4
CHUNK_SIZE = 1024 * 1024  # 1MB per read


def count_bits(byte):
    return bin(byte).count('1')


def compare_chunks(data1, data2, progress, lock, bit_diff_total):
    local_diff = 0
    for b1, b2 in zip(data1, data2):
        local_diff += count_bits(b1 ^ b2)
    with lock:
        bit_diff_total[0] += local_diff
        progress[0] += len(data1)


def print_progress(progress, total_size, stop_flag):
    while not stop_flag[0]:
        percent = progress[0] / total_size * 100
        print(f"\rProgress: {percent:.1f}% ({progress[0]} / {total_size} bytes)", end='', flush=True)
        sleep(0.2)
    print(f"\rProgress: 100.0% ({total_size} / {total_size} bytes)")


def main(file1, file2):
    if not os.path.exists(file1) or not os.path.exists(file2):
        print("Error: One or both files not found")
        return

    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)
    if size1 != size2:
        print("Error: Files are not the same size")
        return

    progress = [0]
    bit_diff_total = [0]
    lock = threading.Lock()
    stop_flag = [False]

    t = threading.Thread(target=print_progress, args=(progress, size1, stop_flag))
    t.start()

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = []
            while True:
                chunk1 = f1.read(CHUNK_SIZE)
                chunk2 = f2.read(CHUNK_SIZE)
                if not chunk1:
                    break
                futures.append(executor.submit(compare_chunks, chunk1, chunk2, progress, lock, bit_diff_total))

            concurrent.futures.wait(futures)

    stop_flag[0] = True
    t.join()

    print(f"\nDiffering bits: {bit_diff_total[0]}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bitcmp.py file1 file2")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
