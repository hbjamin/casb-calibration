import sys
import pandas as pd
import matplotlib.pyplot as plt

def plot_waveform(file_path):
    try:
        # Read the file, skipping the header lines
        df = pd.read_csv(file_path, skiprows=5, names=["Time", "Amplitude"])
        
        # Plot the data
        plt.figure(figsize=(15, 6))
        plt.plot(df["Time"], df["Amplitude"], linestyle='-', color='b')
        plt.title("Waveform Data")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.show()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python plot_waveform.py <file_path>")
    else:
        plot_waveform(sys.argv[1])

