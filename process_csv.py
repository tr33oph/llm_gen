import os
import pandas as pd
import glob
from collections import defaultdict

# Define the path to the csv directory
results_dir = 'csv'
output_md = 'vocabulary_comparison.md'
output_csv = 'vocabulary_comparison.csv'

# Get the current directory (where this script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(current_dir, results_dir)

# Ensure the results directory exists
if not os.path.exists(results_dir):
    raise FileNotFoundError(f"The directory {results_dir} does not exist. Please check the path.")

# Initialize data structures to store results
input_words = set()
model_outputs = defaultdict(dict)  # {model_name: {input_word: [output1, output2]}}

try:
    # Read all CSV files in the results directory
    for file_path in glob.glob(os.path.join(results_dir, '*.csv')):
        # Extract the model name from the filename
        filename = os.path.basename(file_path)
        model_name = filename.split('-')[0]
        
        # Check if the file is empty
        if os.path.getsize(file_path) == 0:
            print(f"Skipping empty file: {filename}")
            continue
            
        # Read the CSV file
        try:
            # Try reading with default headers
            df = pd.read_csv(file_path, names=['输入', '输出', '逻辑'])
        except pd.errors.ParserError:
            # If parsing fails, try again with header=0 if it was misinterpreted
            try:
                df = pd.read_csv(file_path, header=0)
                if '输出' not in df.columns:
                    print(f"File doesn't have '输出' column: {filename}")
                    continue
            except:
                print(f"Error reading file: {filename}")
                continue
        
        # Check if this is the first run or second run based on the filename
        run_number = 1 if '-1.csv' in filename else 2
        
        # Process each row in the dataframe
        for _, row in df.iterrows():
            try:
                input_word = row['输入']
                output = row['输出']
                
                # Skip if input word is NaN or empty
                if pd.isna(input_word) or not str(input_word).strip():
                    continue
                    
                # Add input word to our set
                input_words.add(input_word)
                
                # Store the output for this model and input word
                if input_word not in model_outputs[model_name]:
                    model_outputs[model_name][input_word] = [None, None]
                
                # Store the output in the appropriate position (0 for run 1, 1 for run 2)
                idx = run_number - 1
                model_outputs[model_name][input_word][idx] = output
                
            except Exception as e:
                print(f"Error processing row in {filename}: {str(e)}")
                continue

    # Create a table comparing vocabulary differences
    with open(output_md, 'w', encoding='utf-8') as f:
        # Write the header row
        header = '| 输入词 | ' + ' | '.join(model_outputs.keys()) + ' |'
        f.write(header + '\n')
        
        # Write the separator row
        separator = '|---' + '|---' * len(model_outputs) + '|'
        f.write(separator + '\n')
        
        # For each input word, write a row
        for input_word in sorted(list(input_words)):
            row = f"| {input_word}"
            
            for model_name in model_outputs:
                if input_word in model_outputs[model_name]:
                    outputs = model_outputs[model_name][input_word]
                    if outputs[0] is not None and outputs[1] is not None:
                        if outputs[0] == outputs[1]:
                            cell = f"{outputs[0]}"
                        else:
                            cell = f"{outputs[0]} / {outputs[1]}"
                    elif outputs[0] is not None:
                        cell = f"{outputs[0]} (仅第一次)"
                    elif outputs[1] is not None:
                        cell = f"{outputs[1]} (仅第二次)"
                    else:
                        cell = "无数据"
                else:
                    cell = "无数据"
                
                row += f" | {cell}"
            
            f.write(row + '\n')
    
    # Also save to CSV for completeness
    # Create a list of all unique input words
    all_input_words = sorted(list(input_words))
    
    # Create a DataFrame
    df_output = pd.DataFrame(all_input_words, columns=['输入词'])
    
    # Add columns for each model
    for model_name in model_outputs:
        df_output[f'{model_name}_第一次'] = None
        df_output[f'{model_name}_第二次'] = None
        
        for idx, input_word in enumerate(all_input_words):
            if input_word in model_outputs[model_name]:
                outputs = model_outputs[model_name][input_word]
                df_output.at[idx, f'{model_name}_第一次'] = outputs[0] if outputs[0] is not None else None
                df_output.at[idx, f'{model_name}_第二次'] = outputs[1] if outputs[1] is not None else None
    
    # Save to CSV
    df_output.to_csv(output_csv, index=False, encoding='utf-8-sig')

except Exception as e:
    print(f"Error: {str(e)}")