#!/usr/bin/env python3
"""
Download script for SOP-DAG experiment datasets.
Downloads CoNLL-2003 NER dataset and FewIE dataset.
"""

import os
import sys

# Data directory
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

# Create subdirectories
conll_dir = os.path.join(data_dir, 'conll2003')
fewie_dir = os.path.join(data_dir, 'fewie')
os.makedirs(conll_dir, exist_ok=True)
os.makedirs(fewie_dir, exist_ok=True)

print("=" * 60)
print("SOP-DAG Dataset Downloader")
print("=" * 60)
print(f"Data directory: {data_dir}")
print()

# ============ CoNLL-2003 Dataset ============
print("[1/2] Downloading CoNLL-2003 NER Dataset...")
print("-" * 40)

try:
    from datasets import load_dataset
    
    # Load CoNLL-2003 dataset
    ds = load_dataset('conll2003')
    
    for split_name, split_ds in ds.items():
        print(f"  Loaded split '{split_name}': {len(split_ds)} examples")
        
        # Save as JSON lines
        output_file = os.path.join(conll_dir, f'{split_name}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, example in enumerate(split_ds):
                # Convert to dict format
                record = {
                    'id': i,
                    'tokens': example.get('tokens', []),
                    'ner_tags': example.get('ner_tags', []),
                    'chunk_tags': example.get('chunk_tags', []),
                    'pos_tags': example.get('pos_tags', [])
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"    Saved to: {output_file}")
    
    print("[SUCCESS] CoNLL-2003 downloaded successfully!")
    
except ImportError:
    print("[ERROR] 'datasets' library not installed.")
    print("        Install with: pip install datasets")
    print("        Falling back to direct download...")
    
    # Fallback: download via urllib
    import urllib.request
    import zipfile
    import io
    
    conll_urls = {
        'train': 'https://raw.githubusercontent.com/davidsBatista/NER_Datasets/master/Corpora/CoNLL2003/train.txt',
        'test': 'https://raw.githubusercontent.com/davidsBatista/NER_Datasets/master/Corpora/CoNLL2003/test.txt',
        'valid': 'https://raw.githubusercontent.com/davidsBatista/NER_Datasets/master/Corpora/CoNLL2003/valid.txt'
    }
    
    for split_name, url in conll_urls.items():
        try:
            print(f"  Downloading {split_name}...")
            output_file = os.path.join(conll_dir, f'{split_name}.txt')
            urllib.request.urlretrieve(url, output_file)
            print(f"    Saved to: {output_file}")
        except Exception as e:
            print(f"    Failed: {e}")
    
except Exception as e:
    print(f"[ERROR] Failed to load CoNLL-2003: {e}")

print()

# ============ FewIE Dataset ============
print("[2/2] Downloading FewIE Dataset...")
print("-" * 40)

fewie_urls = [
    ("https://raw.githubusercontent.com/OhioThinker/FewIE/main/data/fewie_train.json", "fewie_train.json"),
    ("https://raw.githubusercontent.com/OhioThinker/FewIE/main/data/fewie_dev.json", "fewie_dev.json"),
    ("https://raw.githubusercontent.com/OhioThinker/FewIE/main/data/fewie_test.json", "fewie_test.json"),
]

import urllib.request

for url, filename in fewie_urls:
    try:
        output_file = os.path.join(fewie_dir, filename)
        print(f"  Downloading {filename}...")
        urllib.request.urlretrieve(url, output_file)
        print(f"    Saved to: {output_file}")
    except Exception as e:
        print(f"    Failed to download {filename}: {e}")
        # Try alternative URLs
        alt_urls = [
            url.replace('OhioThinker/FewIE', 'neulab/FewIE'),
            url.replace('main/', 'master/'),
        ]
        for alt_url in alt_urls:
            try:
                print(f"    Trying alternative URL: {alt_url[:60]}...")
                urllib.request.urlretrieve(alt_url, output_file)
                print(f"    SUCCESS! Saved to: {output_file}")
                break
            except:
                pass
        else:
            print(f"    [WARNING] Could not download {filename}")

print()

# ============ Summary ============
print("=" * 60)
print("Download Summary")
print("=" * 60)

# List downloaded files
import json

def count_json_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return -1

def count_txt_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return -1

print("\nCoNLL-2003 files:")
for f in os.listdir(conll_dir):
    filepath = os.path.join(conll_dir, f)
    if os.path.isfile(filepath):
        if f.endswith('.json'):
            count = count_json_lines(filepath)
        else:
            count = count_txt_lines(filepath)
        size = os.path.getsize(filepath)
        print(f"  - {f}: {count} records, {size:,} bytes")

print("\nFewIE files:")
for f in os.listdir(fewie_dir):
    filepath = os.path.join(fewie_dir, f)
    if os.path.isfile(filepath):
        if f.endswith('.json'):
            count = count_json_lines(filepath)
        else:
            count = count_txt_lines(filepath)
        size = os.path.getsize(filepath)
        print(f"  - {f}: {count} records, {size:,} bytes")

print()
print(f"Data saved to: {data_dir}")
print("=" * 60)
