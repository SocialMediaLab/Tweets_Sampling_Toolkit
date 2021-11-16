import os
import random
from typing import overload
from tqdm import tqdm
import external_sort
import math


class id_file_manager:
    def __init__(self, file_name, is_sorted=False):
        # Used to avoid unnecessary sorting for set operations
        self.is_sorted=is_sorted

        # 
        self.file = open(file_name, 'rb')
        self.file_name = file_name
        file_length = os.stat(file_name).st_size
        first_line = self.file.readline()

        # If the first line is non-numeric, it's skipped whenever IDs
        # are selected.
        try:
            # If this doesn't fail, there is no header and no offset is needed
            int(first_line)
            self.offset = 0
            self.header = ''
            second_line = first_line
        except ValueError:
            # If there is a header, it will be skipped whenever searching for IDs
            self.header = str(first_line, 'utf-8')
            self.offset = len(first_line)
            second_line = self.file.readline()
        # If the second line cannot be read as a number, then the file is corrupted
        try:
            int(second_line)
        except ValueError:
            print("Warning: empty or malformed file")
        self.line_length = len(second_line)

        if self.line_length == 0:
            self.id_count = 0
        else:
            self.id_count = int((file_length - self.offset) / self.line_length)

        # Alert user when a new (non-temp) file has been created
        if 'temp' not in self.file_name:
            print(f'New file: {self.id_count} IDs ({self.file_name})')

    def get_id(self, index):
        if not isinstance(index, int) or index < 0:
            raise Exception("Index must be a positive integer.")
        if index >= self.id_count:
            raise Exception("Index out of bounds (not enough IDs in file)")

        # Rather than reading the file line-by-line, we skip to the specific byte we need
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

            # We keep track of the indexes that have been used to avoid duplicates
            checked_ids = set()
            while len(checked_ids) < n:
                # Pick a new random ID
                i = random.randint(0, self.id_count-1)
                # Only use it if it hasn't already been used
                if i in checked_ids:
                    continue
                out.write(f'{self.get_id(i)}\n')
                checked_ids.add(i)

                bar.update(1)

        return id_file_manager(output_file)

    def get_intersection(self, file_manager, output_file):
        # The bigger file will be sorted to allow quick checking
        if (file_manager.id_count < self.id_count):
            bigger = self
            smaller = file_manager
        else:
            bigger = file_manager
            smaller = self

        # The bigger file must be sorted to allow binary search 
        sorted = bigger.sort('temp.csv')

        # Check each ID in the smaller file, and add it to output if it's found
        print('Checking files for overlap (Final Step)')
        with open(output_file, 'w') as f:
            f.write(self.header)
            for i in tqdm(range(smaller.id_count)):
                id = smaller.get_id(i)
                if sorted.contains(id):
                    f.write(f'{id}\n')

        # Remove temporary sorted file
        sorted.file.close()
        os.remove(sorted.file_name)

        result = id_file_manager(output_file)
        overlap = result.id_count
        print(f'{overlap} IDs were found in both {bigger.file_name} and {smaller.file_name}.')

        return result

    def sort(self, output_file):
        # Use the external sort algorithm; return sorted document
        external_sort.external_sort(self.file_name, output_file, self.id_count)
        return id_file_manager(output_file, is_sorted=True)

    def get_difference(self, file_manager, output_file):
        print('Generating difference file')
        # The right file will be sorted
        left = self
        right = file_manager

        sorted = right.sort('temp.csv')
        # For each ID in the left file, copy it only if it is not in the right file
        print(f'Writing results from {left.file_name}')
        with open(output_file, 'w') as f:
            for i in tqdm(range(left.id_count)):
                id = left.get_id(i)
                if not sorted.contains(id):
                    f.write(f'{id}\n')

        # Remove temporary sorted file
        sorted.file.close()
        os.remove('temp.csv')

        result = id_file_manager(output_file)
        overlap = left.id_count - result.id_count
        print(f'{overlap} IDs were found in both {left.file_name} and {right.file_name}.')

        return result

    def contains(self, n, min_index=0, max_index=None):
        # This is a recursive binary search that has O(log n) complexity
        # Each iteration reduces the search range by half
        # Self must be sorted
        if not self.is_sorted:
            print('Warning: .contains() only works on sorted documents.')

        # Set default maximum search range
        if max_index is None:
            max_index = self.id_count
        # If the search range is empty, the file does not contain the id
        if max_index == min_index:
            return False

        # Pick the ID in the middle of the range: if it's higher than what you're looking for,
        # search the first half of the range, if it's lower search the second half of the range
        check_id = min_index + math.floor((max_index - min_index)/2)
        check = self.get_id(check_id)
        if n < check:
            return self.contains(n, min_index=min_index, max_index=check_id)
        if n > check:
            return self.contains(n, min_index=check_id + 1, max_index=max_index)
        if n == check:
            return True

    def get_union(self, file_manager, output_file):
        print(f'Creating union file')

        # The larger file will be sorted
        if self.id_count < file_manager.id_count:
            smaller = self
            bigger = file_manager
        else:
            smaller = file_manager
            bigger = self

        # Sort the larger file to allow binary search
        sorted = bigger.sort('temp.csv')

        with open(output_file, 'w') as f:
            # Copy entire contents of larger file
            print(f'Writing results from {bigger.file_name}')
            for i in tqdm(range(sorted.id_count)):
                f.write(f'{sorted.get_id(i)}\n')

            # Copy IDs from smaller file that are not already in larger file
            print(f'Writing results from {smaller.file_name}')
            for i in tqdm(range(smaller.id_count)):
                n = smaller.get_id(i)
                if not sorted.contains(n):
                    f.write(f'{smaller.get_id(i)}\n')

        # Delete temporary sorted file
        sorted.file.close()
        os.remove(sorted.file_name)

        result = id_file_manager(output_file)
        overlap = bigger.id_count + smaller.id_count - result.id_count
        print(f'{overlap} IDs were found in both {bigger.file_name} and {smaller.file_name}.')

        return result

    def get_page_sample(self, page_number, page_count, output_file):
        if not isinstance(page_number, int) or not isinstance(page_count, int):
            raise Exception('Page count and page number must be integers')
        if page_number < 0 or page_count <= page_number:
            raise Exception('Page number out of bounds')

        # Calculate where to start copying
        start = int(self.id_count / page_count) * page_number
        # Calculate where to finish copying
        # If the number of IDs is not divisble by the number of pages, the last page will be longer than the others
        if page_number == page_count - 1:
            end = self.id_count
        else:
            end = int(self.id_count / page_count) * (page_number + 1)

        # Copy the files in the calculated range
        with open(output_file, 'w') as f:
            f.write(self.header)
            for i in tqdm(range(start, end)):
                f.write(f'{self.get_id(i)}\n')

        return id_file_manager(output_file)

    def get_page_samples(self, page_count, output_file):
        if not isinstance(page_count, int) or page_count < 0:
            raise Exception('Page count must be a positive integer')

        # Determine the size of zero-padding need for all pages names to have consistent length
        zeroes = 1
        n = 10
        while page_count > n:
            zeroes += 1
            n *= 10
        format = f'{{0:0{zeroes}d}}'

        # For each page, a file is created and added to the list of results
        results = []
        for p in range(page_count):
            print(f'Generating page {p+1} of {page_count}')
            tokens = output_file.split('.')
            tokens[0] += '_' + format.format(p)
            name = '.'.join(tokens)
            results.append(self.get_page_sample(p, page_count, name))

        return results
