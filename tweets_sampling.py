import os
import random
from tqdm import tqdm
import external_sort
import math


class id_file_manager:
    def __init__(self, file_name, show_progress=False, is_sorted=False):
        self.is_sorted=is_sorted

        self.file = open(file_name, 'rb')
        self.file_name = file_name
        file_length = os.stat(file_name).st_size
        first_line = self.file.readline()

        # If the first line is non-numeric, it's skipped whenever IDs
        # are selected.
        try:
            int(first_line)
            self.offset = 0
            self.header = ''
            second_line = first_line
        except ValueError:
            self.header = str(first_line, 'utf-8')
            # self.header = first_line
            # If the first line is num
            self.offset = len(first_line)
            second_line = self.file.readline()
        try:
            int(second_line)
        except ValueError:
            print("Warning: empty or malformed file")
        self.line_length = len(second_line)

        if self.line_length == 0:
            self.id_count = 0
        else:
            self.id_count = int((file_length - self.offset) / self.line_length)

        self.show_progress = show_progress

    def get_id(self, index):
        if not isinstance(index, int) or index < 0:
            raise Exception("Index must be a positive integer.")
        if index >= self.id_count:
            raise Exception("Index out of bounds (not enough IDs in file)")

        position = self.offset + self.line_length * index
        self.file.seek(position)
        return int(self.file.readline())

    def get_random_id(self):
        index = random.randint(0, self.id_count-1)
        return self.get_id(index)

    def get_random_sample(self, n, output_file, sample_mode="absolute"):
        print('Generating random sample')
        if sample_mode not in ['absolute', 'percent']:
            raise "Sample mode must be either absolute or percent"

        if sample_mode == 'percent':
            n = int(n * self.id_count)

        if n >= self.id_count:
            raise Exception("Sample size too big (not enough IDs in file)")

        with open(output_file, 'w') as out, tqdm(total=n) as bar:
            out.write(self.header)

            checked_ids = set()
            while len(checked_ids) < n:
                i = random.randint(0, self.id_count-1)
                if i in checked_ids:
                    continue
                out.write(f'{self.get_id(i)}\n')
                checked_ids.add(i)

                bar.update(1)

        if self.show_progress:
            print(f'Done {n}/{n}')

        return id_file_manager(
            output_file,
            show_progress=self.show_progress
        )

    def get_set(self):
        print('Loading file')

        s = set()

        for i in tqdm(range(self.id_count)):
            s.add(self.get_id(i))

        if len(s) != self.id_count:
            print(
                f'Warning: {self.file_name} contains duplicate IDs'
            )

        return s

    def get_intersection(self, file_manager, output_file):
        # The smaller file will be placed in a set
        if (file_manager.id_count < self.id_count):
            bigger = self
            smaller = file_manager
        else:
            bigger = file_manager
            smaller = self

        sorted = bigger.sort('temp.csv')

        with open(output_file, 'w') as f:
            f.write(self.header)
            for i in tqdm(range(smaller.id_count)):
                id = smaller.get_id(i)
                if sorted.contains(id):
                    f.write(f'{id}\n')

        sorted.file.close()
        os.remove(sorted.file_name)

        return id_file_manager(output_file)

    def sort(self, output_file):
        external_sort.external_sort(self.file_name, output_file, self.id_count)
        return id_file_manager(output_file, is_sorted=True)

    def get_difference(self, file_manager, output_file):
        # The smaller file will be placed in a set
        left = self
        right = file_manager

        sorted = right.sort('temp.csv')
        with open(output_file, 'w') as f:
            for i in tqdm(range(left.id_count)):
                id = left.get_id(i)
                if not sorted.contains(id):
                    f.write(f'{id}\n')

        sorted.file.close()
        os.remove('temp.csv')

        return id_file_manager(output_file)

    def contains(self, n, min_index=0, max_index=None):
        if not self.is_sorted:
            print('Warning: .contains() only works on sorted documents.')

        if max_index is None:
            max_index = self.id_count
        if max_index == min_index:
            return False

        check_id = min_index + math.floor((max_index - min_index)/2)
        check = self.get_id(check_id)
        if n < check:
            return self.contains(n, min_index=min_index, max_index=check_id)
        if n > check:
            return self.contains(n, min_index=check_id + 1, max_index=max_index)
        if n == check:
            return True

    def get_union(self, file_manager, output_file):
        print(f'Creating union of the two files in {output_file}')

        if self.id_count < file_manager.id_count:
            smaller = self
            bigger = file_manager
        else:
            smaller = file_manager
            bigger = self

        sorted = bigger.sort('temp.csv')

        with open(output_file, 'w') as f:
            print(f'Writing results from {bigger.file_name}')
            for i in tqdm(range(sorted.id_count)):
                f.write(f'{self.get_id(i)}\n')

            print(f'Writing results from {smaller.file_name}')
            for i in tqdm(range(smaller.id_count)):
                n = smaller.get_id(i)
                if not sorted.contains(n):
                    f.write(f'{self.get_id(i)}\n')

        sorted.file.close()
        os.remove(sorted.file_name)

        return id_file_manager(output_file)

    def get_page_sample(self, page_number, page_count, output_file):
        if not isinstance(page_number, int) or not isinstance(page_count, int):
            raise Exception('Page count and page number must be integers')
        if page_number < 0 or page_count <= page_number:
            raise Exception('Page number out of bounds')

        start = int(self.id_count / page_count) * page_number
        if page_number == page_count - 1:
            end = self.id_count
        else:
            end = int(self.id_count / page_count) * (page_number + 1)

        with open(output_file, 'w') as f:
            f.write(self.header)
            for i in range(start, end):
                f.write(f'{self.get_id(i)}\n')

                if self.show_progress:
                    if (i - start) % 10000 == 0:
                        print(f'Wrote {i - start}/{end - start} IDs')

        return id_file_manager(output_file)

    def get_page_samples(self, page_count, output_file):
        if not isinstance(page_count, int) or page_count < 0:
            raise Exception('Page count must be a positive integer')

        zeroes = 1
        n = 10
        while page_count > n:
            zeroes += 1
            n *= 10
        format = f'{{0:0{zeroes}d}}'

        results = []
        for p in range(page_count):
            tokens = output_file.split('.')
            tokens[0] += '_' + format.format(p)
            name = '.'.join(tokens)
            results.append(self.get_page_sample(p, page_count, name))

        return results
