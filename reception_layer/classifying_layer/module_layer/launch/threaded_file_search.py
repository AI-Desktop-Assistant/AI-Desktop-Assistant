import asyncio
import os
import difflib
import re

best_match = {"file": None, "score": -1}
lock = asyncio.Lock()

async def compare_strings(entry, queried_file):
    if entry.name.endswith(('.exe', '.url', '.lnk')):
        file_name = os.path.splitext(entry.name)[0].lower()
        
        file_name_tokens = list(re.split('\W+', file_name))
        queried_file_tokens = list(re.split('\W+', queried_file.lower()))

        matcher = difflib.SequenceMatcher(None, file_name_tokens, queried_file_tokens)
        score = matcher.ratio()
        
        async with lock:
            if score > best_match["score"]:
                best_match["score"] = score
                best_match["file"] = entry.path

async def search_directory(path, queried_file):
    if os.path.exists(path):
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        await search_directory(entry.path, queried_file)
                    elif entry.is_file():
                        await compare_strings(entry, queried_file,)
        except PermissionError:
            print(f'Permission denied: {path}')

async def find_close_match(file_name):
    home = os.path.expanduser("~")
    potential_paths = [
        "C:\\Program Files (x86)", "C:\\Program Files", 
        home + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs", 
        home + "\\Desktop", home + "\\Downloads", home + "\\Documents"
    ]
    
    await asyncio.gather(*(search_directory(path, file_name) for path in potential_paths))

    if best_match["file"]:
        return best_match
    else:
        print("No matching .exe file found")

def find_file(file_name):
    return asyncio.run(find_close_match(file_name))
