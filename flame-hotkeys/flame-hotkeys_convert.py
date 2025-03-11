#!/usr/bin/env python

""" Convert pre-2025 flame hotkeys to 2025 shortcuts json format.
Wrote this for a user who had a lot of hotkeys.
If the user is missing a shortcut, they should create within Flame application as that is the easiest.
Use at your own risk and not responsible if anything goes horribly wrong. """


import re
import json
import os
import glob
from collections import OrderedDict


def parse_block(block, key_mapping, ordered_keys):
    """ Parse the block using the provided key mapping and order the keys.
    Pre-2025 flame hotkeys functions have different/more KVPs. """
    block_dict = OrderedDict()

    for line in block.split('\n'):
        match_line = re.match(r'\s*(\w+)\s+(.*)', line)
        if match_line:
            key, value = match_line.groups()
            if key in key_mapping:
                block_dict[key_mapping[key]] = value

    ordered_block_dict = OrderedDict()
    for key in ordered_keys:
        if key in block_dict:
            ordered_block_dict[key] = block_dict[key]

    return ordered_block_dict


def parse_func_block(block):
    """ Parse the block using the provided key mapping and order the keys.
    Pre-2025 flame hotkeys functions have different/more KVPs. """
    key_mapping = {
        "Description": "Description",
        "Category": "Category",
        "FuncIndex": "FunctionName",
        "Key1": "Key1",
        "Key2": "Key2",
        "Key3": "Key3",
        "Key4": "Key4"
    }
    ordered_keys = ["Description", "Category", "FunctionName", "Key1", "Key2", "Key3", "Key4"]
    return parse_block(block, key_mapping, ordered_keys)


def parse_butt_block(block):
    """ Parse the block using the provided key mapping and order the keys.
    Pre-2025 flame hotkeys functions have different/more KVPs. """
    key_mapping = {
        "Description": "Description",
        "Category": "Category",
        "ItemIndex": "ButtonName",
        "ItemFuncParam": "ItemFuncParam",
        "Key1": "Key1",
        "Key2": "Key2",
        "Key3": "Key3",
        "Key4": "Key4"
    }
    ordered_keys = ["Description", "Category", "ButtonName", "ItemFuncParam",
                    "Key1", "Key2", "Key3", "Key4"]
    return parse_block(block, key_mapping, ordered_keys)


def parse_local_butt_block(block):
    """ Parse the block using the provided key mapping and order the keys.
    Pre-2025 flame hotkeys functions have different/more KVPs. """
    key_mapping = {
        "Description": "Description",
        "Category": "Category",
        "ItemIndex": "ButtonName",
        "ValueType": "ValueType",
        "ValueIncrement": "ValueIncrement",
        "ItemFuncParam": "ItemFuncParam",
        "Key1": "Key1",
        "Key2": "Key2",
        "Key3": "Key3",
        "Key4": "Key4"
    }
    ordered_keys = ["Description", "Category", "ButtonName", "ValueType", "ValueIncrement", "ItemFuncParam",
                    "Key1", "Key2", "Key3", "Key4"]
    return parse_block(block, key_mapping, ordered_keys)


def process_file(file_path, block_parser):
    """ Parse the pre-2025 flame hotkeys files from the flame user's hotkey directory """
    with open(file_path, 'r') as file:
        content = file.read()

    # Assume that blocks start with HotKeyOne StartHotKeyOne and end with EndHotKeyOne
    blocks = re.findall(r'HotKeyOne\s*StartHotKeyOne(.*?)EndHotKeyOne', content, re.DOTALL)
    return [block_parser(block) for block in blocks]


def save_to_json(parsed_blocks, output_file):
    """ Write out as json format and reorder to match what Flame has in shortcuts.json files. """
    # Extract the keyword from the output file name
    with open(output_file, 'w') as json_file:
        keyword = os.path.splitext(os.path.basename(output_file))[0].split('.')[2]

        # Add the version and the start of the shortcuts list
        json_file.write('{\n    "Version": "2025",\n    "' + keyword + 'Shortcuts": [\n')

        # Write each block as a JSON object
        for idx, block in enumerate(parsed_blocks):
            if idx > 0:
                json_file.write(',\n')  # Add comma between blocks

            json_file.write('        {\n')
            key_value_pairs = []
            for key, value in block.items():
                if value == "KEY_NONE":
                    continue  # Skip key-value pairs where value is "KEY_NONE"
                if value == "KEY_CTL":
                    value = "KEY_CTL_L"  # Replace "KEY_CTL" with "KEY_CTL_L"
                elif value == "KEY_ALT":
                    value = "KEY_ALT_L"  # Replace "KEY_ALT" with "KEY_ALT_L"
                value = value.replace('\\', '\\\\')  # Escape backslashes
                key_value_pairs.append(f'            "{key}": "{value}"')
            json_file.write(',\n'.join(key_value_pairs))
            json_file.write('\n        }')

        # Add the end of the shortcuts list
        json_file.write('\n    ]\n}')


# Specify the input directory
# The pre-2025 flame hotkeys files are in the flame user's hotkey directory
input_directory = './'

# Search for the pre-2025 flame hotkeys files matching the patterns
# e.g. current.Action.butt.hotkey user, current.Action.func.hotkey.user
func_files = glob.glob(os.path.join(input_directory, 'current.*.func.hotkey.user'))
butt_files = glob.glob(os.path.join(input_directory, 'current.*.butt.hotkey.user'))

for input_func_file in func_files:
    # Determine the output file name based on the input file pattern
    # Use the second and third fields for the associated output file name
    # Do not add "func" to output filename
    output_file_path = None
    match_func = re.match(r'.*\.([^.]+)\.func\.hotkey\.user', input_func_file)
    if match_func:
        keyword_func = match_func.group(1).lower()
        if keyword_func == "paintnode":
            output_file_path = 'user.shortcuts.paint_batch.json'  # PaintNode changed to paint_batch
        elif keyword_func == "paint":
            output_file_path = 'user.shortcuts.paint_tools.json'  # Paint changed to paint_tools
        else:
            output_file_path = f'user.shortcuts.{keyword_func}.json'

    # Process the file and save the output
    # Use all lowercase for json filenames
    if output_file_path:
        parsed_blocks_func = process_file(input_func_file, parse_func_block)
        save_to_json(parsed_blocks_func, output_file_path)
        print(f"Converted {len(parsed_blocks_func)} blocks to JSON and saved to {output_file_path}")

for input_butt_file in butt_files:
    # Determine the output file name based on the input file pattern
    # Use the second and third fields for the associated output file name
    # Add "buttons" to output filename
    output_file_path = None
    match_butt = re.match(r'.*\.([^.]+)\.butt\.hotkey\.user', input_butt_file)
    if match_butt:
        keyword_butt = match_butt.group(1).lower()
        if keyword_butt == "paintnode":
            output_file_path = 'user.shortcuts.paint_batch.buttons.json'  # PaintNode changed to paint_batch
        elif keyword_butt == "paint":
            output_file_path = 'user.shortcuts.paint_tools.buttons.json'  # Paint changed to paint_tools
        else:
            output_file_path = f'user.shortcuts.{keyword_butt}.buttons.json'

    # Process the file and save the output
    # Use all lowercase for json filenames
    # KVP are different/more in the older Local.func and Local.butt files
    if output_file_path == "user.shortcuts.local.buttons.json":
        parsed_blocks_butt = process_file(input_butt_file, parse_local_butt_block)
    else:
        parsed_blocks_butt = process_file(input_butt_file, parse_butt_block)
    save_to_json(parsed_blocks_butt, output_file_path)
    print(f"Converted {len(parsed_blocks_butt)} blocks to JSON and saved to {output_file_path}")

