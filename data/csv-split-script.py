import pandas as pd
import argparse
import sys

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Split a CSV file, moving one column to a new file along with the time column.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('output_file', help='Path for the output CSV file (will contain Time and CH2)')
    parser.add_argument('--remaining_file', help='Optional: Path for the file with remaining columns (Time and CH1)')
    parser.add_argument('--skiprows', type=int, default=0, help='Number of rows to skip at the beginning of the file')
    parser.add_argument('--time_col', default='Time', help='Name of the time column')
    parser.add_argument('--keep_col', default='CH2', help='Name of the column to keep with time in the new file')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Load the original CSV file
        print(f"Loading {args.input_file}...")
        df = pd.read_csv(args.input_file, skiprows=args.skiprows)
        
        # Check if the specified columns exist
        if args.time_col not in df.columns:
            print(f"Error: Time column '{args.time_col}' not found in the CSV file.")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)
            
        if args.keep_col not in df.columns:
            print(f"Error: Column to keep '{args.keep_col}' not found in the CSV file.")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)
        
        # Create a new DataFrame with only Time and the specified column
        new_df = df[[args.time_col, args.keep_col]].copy()
        
        # Save the new DataFrame to the output file
        new_df.to_csv(args.output_file, index=False)
        print(f"Successfully created {args.output_file} with {args.time_col} and {args.keep_col} columns")
        
        # Save the remaining columns if requested
        if args.remaining_file:
            # Get all columns except the keep_col (but always include time)
            remaining_cols = [col for col in df.columns if col != args.keep_col or col == args.time_col]
            df_remaining = df[remaining_cols].copy()
            df_remaining.to_csv(args.remaining_file, index=False)
            print(f"Also created {args.remaining_file} with remaining columns")
            
    except FileNotFoundError:
        print(f"Error: Could not find the input file {args.input_file}")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Error: Could not parse {args.input_file} as a CSV file")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
