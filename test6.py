import re
import os

def next_available_filename(folder='media', prefix='video', extension='.mp4'):
    pattern = re.compile(rf'^{re.escape(prefix)}(\d+){re.escape(extension)}$')
    existing_numbers = set()

    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            existing_numbers.add(int(match.group(1)))

    i = 1
    while i in existing_numbers:
        i += 1

    return f"media/{prefix}{i}{extension}"
print(next_available_filename())