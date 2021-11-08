import os
import random


class id_file_manager:
    def __init__(self, file_name, show_progress=False):
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
        if sample_mode not in ['absolute', 'percent']:
            raise "Sample mode must be either absolute or percent"

        if sample_mode == 'percent':
            n = int(n * self.id_count)

        if n >= self.id_count:
            raise Exception("Sample size too big (not enough IDs in file)")

        with open(output_file, 'w') as out:
            out.write(self.header)

            checked_ids = set()
            while len(checked_ids) < n:
                i = random.randint(0, self.id_count-1)
                if i in checked_ids:
                    continue
                out.write(f'{self.get_id(i)}\n')

                if self.show_progress:
                    if (len(checked_ids) % 10000) == 0:
                        print(f'Done {len(checked_ids)}/{n}')
                checked_ids.add(i)

        if self.show_progress:
            print(f'Done {n}/{n}')

        return id_file_manager(
            output_file,
            show_progress=self.show_progress
        )

    def get_set(self):
        s = set()

        for i in range(self.id_count):
            if (self.show_progress):
                if (len(s) % 100000) == 0:
                    print(
                        f'Loaded {len(s)}/{self.id_count} IDs from file'
                    )
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

        s = smaller.get_set()

        with open(output_file, 'w') as f:
            f.write(self.header)
            for i in range(bigger.id_count):
                id = bigger.get_id(i)
                if id in s:
                    f.write(f'{id}\n')

                if self.show_progress:
                    if i % 10000 == 0:
                        print(f'Checked {i}/{bigger.id_count} IDs')

        return id_file_manager(output_file)

    def get_difference(self, file_manager, output_file):
        # The smaller file will be placed in a set
        left = self
        right = file_manager

        s = right.get_set()
        with open(output_file, 'w') as f:
            f.write(self.header)
            for i in range(left.id_count):
                id = left.get_id(i)
                if id not in s:
                    f.write(f'{id}\n')

                if self.show_progress:
                    if i % 10000 == 0:
                        print(f'Checked {i}/{left.id_count} IDs')

        return id_file_manager(output_file)

    def get_union(self, file_manager, output_file):
        if (file_manager.id_count < self.id_count):
            bigger = self
            smaller = file_manager
        else:
            bigger = file_manager
            smaller = self

        s = bigger.get_set()
        with open(output_file, 'w') as f:
            f.write(self.header)
            for id in s:
                f.write(f'{id}\n')
            for i in range(smaller.id_count):
                id = smaller.get_id(i)
                if id not in s:
                    f.write(f'{id}\n')
                    s.add(id)

                if self.show_progress:
                    if i % 10000 == 0:
                        print(f'Checked {i}/{smaller.id_count} IDs')

        return id_file_manager()

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


def hydrate(file_name):
    raise NotImplementedError


def sample_file(input_file, n, mode="absolute", output_file=None):
    raise NotImplementedError
