import csv
import argparse
import sys
import random
import json

def write_rows_to_tsv(writer, rows):
    """Helper function to write a list of dictionary rows to a TSV writer."""
    # Iterate over each row in the provided list.
    for row in rows:
        # Construct the first column for the TSV as specified.
        adl_type = row.get('adl_type', '[N/A]')
        input_text = row.get('input', '')
        first_column = f"Please classify for {adl_type}\n\n{input_text}"

        # The second column is the direct value from the 'classification' key.
        second_column = row.get('classification', '')

        # Write the newly formatted row to the TSV file.
        writer.writerow([first_column, second_column])

def convert_jsonl_to_tsv_split(input_path, train_path, test_path):
    """
    Reads a JSONL file, processes and splits the data into training and testing
    TSV files.

    The input JSONL must contain objects with 'input', 'classification', and 'adl_type' keys.
    The output TSVs will have two columns:
    1. A formatted prompt string.
    2. The original classification.
    """
    try:
        # --- Data Reading and Preparation ---
        all_rows = []
        with open(input_path, mode='r', encoding='utf-8') as infile:
            for line in infile:
                # Skip empty lines
                if not line.strip():
                    continue
                try:
                    # Parse each line as a JSON object and add to our list
                    row = json.loads(line)
                    all_rows.append(row)
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Skipping invalid JSON line: {line.strip()}", file=sys.stderr)
        
        if not all_rows:
            print("❌ Error: Input JSONL file is empty or contains no valid JSON objects.", file=sys.stderr)
            sys.exit(1)

        # --- Input Validation ---
        # Verify that all required keys are present in the first JSON object.
        required_keys = ['input', 'classification', 'adl_type']
        first_row_keys = all_rows[0].keys()
        if not all(key in first_row_keys for key in required_keys):
            missing = [k for k in required_keys if k not in first_row_keys]
            print(f"❌ Error: Input JSONL is missing required keys in its objects: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

        # Randomly shuffle the rows to ensure an unbiased split.
        random.shuffle(all_rows)

        # Calculate the split point for a 50/50 distribution.
        split_index = len(all_rows) // 2
        train_rows = all_rows[:split_index]
        test_rows = all_rows[split_index:]

        # --- Write Training Data ---
        with open(train_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            writer.writerow(['prompt', 'label']) # Write header
            write_rows_to_tsv(writer, train_rows)

        # --- Write Testing Data ---
        with open(test_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            writer.writerow(['prompt', 'completion']) # Write header
            write_rows_to_tsv(writer, test_rows)

        print(f"✅ Successfully converted '{input_path}' into:")
        print(f"  - Training data: '{train_path}' ({len(train_rows)} rows)")
        print(f"  - Testing data:  '{test_path}' ({len(test_rows)} rows)")

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_path}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Set up the argument parser to handle command-line arguments.
    parser = argparse.ArgumentParser(
        description="Convert a JSONL file to two TSV files (train/test split).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example usage:
  python process_data.py input_data.jsonl train_set.tsv test_set.tsv
"""
    )

    # Add arguments for the input and output file paths.
    parser.add_argument("input_path", help="The path to the source JSONL file.")
    parser.add_argument("train_output_path", help="The path for the training TSV file.")
    parser.add_argument("test_output_path", help="The path for the testing TSV file.")

    # Parse the arguments from the command line.
    args = parser.parse_args()

    # Call the main function with the provided file paths.
    convert_jsonl_to_tsv_split(args.input_path, args.train_output_path, args.test_output_path)


