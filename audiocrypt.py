import getpass
import os
import random
import sys
from datetime import datetime
from itertools import cycle
try:
    import numpy as np
    from scipy.io import wavfile
except ModuleNotFoundError:
    print('Enter the command: pip install numpy scipy')
    sys.exit()


class AudioCrypt():
    def __init__(self, password):
        self.password = password

    def encrypt(self, filename):
        new_filename = self.new_filename('e', filename)
        if new_filename is None:
            print(f'Error: file {new_filename} already exists')
        else:
            try:
                start = datetime.now()
                samplerate, data = wavfile.read(filename)
                encrypted = self.get_datalist(data)
                numbers = self.password_to_numbers(self.password)
                for i in progress_bar(numbers, 'Encryption: '):
                    encrypted = self.rail_fence_encrypt(encrypted, i)
                print('Creation...')
                e_data = np.array(encrypted)
                wavfile.write(new_filename, samplerate, e_data)
                print(f'Encrypted audio saved as {new_filename}')
                print('Time:', datetime.now() - start)
            except FileNotFoundError as error:
                print(error)

    def decrypt(self, filename):
        new_filename = self.new_filename('d', filename)
        if new_filename is None:
            print(f'Error: file {new_filename} already exists')
        else:
            try:
                start = datetime.now()
                samplerate, data = wavfile.read(filename)
                decrypted = self.get_datalist(data)
                numbers = self.password_to_numbers(self.password[::-1])
                for i in progress_bar(numbers, 'Decryption: '):
                    decrypted = self.rail_fence_decrypt(decrypted, i)
                print('Creation...')
                d_data = np.array(decrypted)
                wavfile.write(new_filename, samplerate, d_data)
                print(f'Decrypted audio saved as {new_filename}')
                print('Time:', datetime.now() - start)
            except FileNotFoundError as error:
                print(error)

    @staticmethod
    def get_datalist(data):
        print('Scanning...')
        datalist = []
        for i in data:
            datalist.append(tuple(i))
        return datalist

    @staticmethod
    def password_to_numbers(password):
        numbers = [ord(i) for i in password]
        return numbers

    def rail_fence_encrypt(self, plaintext, rails):
        p = self.rail_pattern(rails)
        return sorted(plaintext, key=lambda i: next(p))

    def rail_fence_decrypt(self, ciphertext, rails):
        p = self.rail_pattern(rails)
        indexes = sorted(range(len(ciphertext)), key=lambda i: next(p))
        result = [''] * len(ciphertext)
        for i, c in zip(indexes, ciphertext):
            result[i] = c
        return result

    @staticmethod
    def rail_pattern(n):
        r = list(range(n))
        return cycle(r + r[-2:0:-1])

    @staticmethod
    def new_filename(mode, filename):
        new_filename = f'{filename[:len(filename) - 4]}-{mode}.wav'
        if os.path.exists(new_filename):
            return None
        else:
            return new_filename


def progress_bar(it, prefix='', size=60, out=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'='*x}{('·'*(size-x))}]", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print('', flush=True, file=out)


def main():
    filename = input('Enter audio filename: ')
    if filename[len(filename) - 3:] == 'wav':
        password = getpass.getpass(prompt='Enter password: ', stream=None)
        if len(password) >= 8:
            mode = input('Do you want to encrypt or decrypt the audio [E/d]? ')
            if mode == 'd' or mode == 'D':
                AudioCrypt(password).decrypt(filename)
            else:
                AudioCrypt(password).encrypt(filename)
        else:
            print('Error: minimum password length: 8')
            return
    else:
        print('Error: only .wav format')
        return


if __name__ == '__main__':
    main()
