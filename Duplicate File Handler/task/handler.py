# write your code here
import argparse
import os
import hashlib


def get_hash(file_name: str) -> str:
    with open(file_name, 'rb') as f:
        return hashlib.md5(b''.join(f.readlines())).hexdigest()


class Browser:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.format = ''
        self.sorting_option = ''
        self.files_list = []
        self.files_lists_by_size = {}
        self.duplicate_check = False
        self.sorted = False
        self.duplicates = {}

    def walker(self):
        for root, dirs, files in os.walk(self.root_dir):
            for name in files:
                file = os.path.join(root, name)
                if file.endswith(self.format):
                    self.files_list.append(file)

    def get_sorting_option(self):
        self.format = input('Enter file format:\n')
        print("Size sorting options:")
        print("1. Descending")
        print("2. Ascending")

        while True:
            sorting_option = int(input("Enter a sorting option:\n"))
            if sorting_option == 1:
                self.sorting_option = 'descending'
                break
            elif sorting_option == 2:
                self.sorting_option = 'ascending'
                break
            else:
                print("Wrong option")

    def do_duplicate_check(self):
        while True:
            check = input('Check for duplicates?\n')
            if check == 'yes':
                self.duplicate_check = True
                break
            elif check == 'no':
                self.duplicate_check = False
                break
            else:
                continue

    def size_sorting(self):
        if self.sorting_option == 'ascending':
            self.files_list.sort(key=os.path.getsize)
            self.sorted = True
        else:
            self.files_list.sort(key=os.path.getsize, reverse=True)
            self.sorted = True

    def group_by_size_and_hash(self):

        if self.sorted:
            for file in self.files_list:
                file_size = os.path.getsize(file)
                file_hash = get_hash(file)
                if file_size in self.files_lists_by_size and file_hash in self.files_lists_by_size[file_size]:
                    self.files_lists_by_size[file_size][file_hash].append(file)
                elif file_size in self.files_lists_by_size and file_hash not in self.files_lists_by_size[file_size]:
                    self.files_lists_by_size[file_size][file_hash] = [file]
                else:
                    self.files_lists_by_size[file_size] = {}
                    self.files_lists_by_size[file_size][file_hash] = [file]
            # after sorting the files by size and hash collect all duplicates
            self.collect_duplicates()

    def collect_duplicates(self):
        n_duplicates = 0
        for size in self.files_lists_by_size:
            for file_hash in self.files_lists_by_size[size]:
                if len(self.files_lists_by_size[size][file_hash]) > 1:
                    for file in self.files_lists_by_size[size][file_hash]:
                        n_duplicates += 1
                        self.duplicates[n_duplicates] = (file, size, file_hash)

    def delete_menu(self):
        while True:
            check = input('Delete files?\n')
            if check == 'yes':
                while True:
                    file_to_delete = input("Enter file numbers to delete:\n").split()
                    if file_to_delete \
                            and all(i.isdigit() for i in file_to_delete) \
                            and all(int(i) in self.duplicates for i in file_to_delete):
                        self.do_delete([int(i) for i in file_to_delete])
                    else:
                        print('Wrong format')
                        continue
            elif check == 'no':
                break
            else:
                print("Wrong option")
                continue

    def do_delete(self, files_to_delete):
        freed_space = 0
        for number in files_to_delete:
            print(self.duplicates[number])
            os.remove(self.duplicates[number][0])
            freed_space += self.duplicates[number][1]
        print(f'Total freed up space: {freed_space} bytes')

    def display_files(self):
        file_size = -1
        if self.duplicate_check:
            n_duplicates = 0
            for size in self.files_lists_by_size:
                print(f'{size} bytes')
                for file_hash in self.files_lists_by_size[size]:
                    if len(self.files_lists_by_size[size][file_hash]) > 1:
                        print(f'Hash: {file_hash}')
                        for file in self.files_lists_by_size[size][file_hash]:
                            n_duplicates += 1
                            print(f"{n_duplicates}. {file}")
        else:
            for file in self.files_list:
                if file_size != os.path.getsize(file):
                    file_size = os.path.getsize(file)
                    print(f'{os.path.getsize(file)} bytes')
                    print(file)
                else:
                    print(file)


parser = argparse.ArgumentParser()
parser.add_argument('dir_name')


try:
    args = parser.parse_args()
    browser = Browser(args.dir_name)
except:
    print('Directory is not specified')
    exit(0)
browser.get_sorting_option()
browser.walker()
browser.size_sorting()
browser.group_by_size_and_hash()
browser.display_files()
browser.do_duplicate_check()
browser.display_files()
browser.delete_menu()
