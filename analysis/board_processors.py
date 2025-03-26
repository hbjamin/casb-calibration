import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re

from waveform_processor import WaveformProcessor





class CASB1Processor(WaveformProcessor):
    
    def __init__(self):
        super().__init__(name="CASB1")
    
    def load_singles(self, path="../data/casb1/singles/C1--Trace--*.txt"):
        files = glob.glob(path)
        if not files:
            print(f"Warning: No files found matching pattern: {path}")
            return {}
        files_per_channel = {}
        for file in files:
            try:
                filename = os.path.basename(file)
                match = re.search(r'C(\d+)--Trace--(\d+)', filename)
                if match:
                    channel = int(match.group(1))
                    trace_num = int(match.group(2))
                else:
                    match = re.search(r'Trace--(\d+)', filename)
                    if match:
                        trace_num = int(match.group(1))
                        channel = 1  # Default if no channel in filename
                    else:
                        print(f"Could not extract info from {filename}, skipping")
                        continue
                df = pd.read_csv(file, skiprows=6, names=["time", "output"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                if channel not in self.channels:
                    self.channels[channel] = {}
                if 'singles' not in self.channels[channel]:
                    self.channels[channel]['singles'] = {}
                self.channels[channel]['singles'][trace_num] = {
                    'data': df,
                    'analysis': {}
                }
                if channel in files_per_channel:
                    files_per_channel[channel] += 1
                else:
                    files_per_channel[channel] = 1
            except Exception as e:
                print(f"Error processing file {file}: {e}")
        total_files = sum(files_per_channel.values())
        print(f"Loaded {total_files} singles files across {len(files_per_channel)} channels for {self.name}")
        return files_per_channel
    
    def load_averages(self, path):
        files = glob.glob(path)
        if not files:
            print(f"Warning: No files found matching pattern: {path}")
            return {}
        files_per_channel = {}
        for file in files:
            try:
                filename = os.path.basename(file)
                match = re.search(r'ch(\d+)', filename)
                if match:
                    channel = int(match.group(1))
                else:
                    print(f"Could not extract channel from {filename}, skipping")
                    continue
                if channel in files_per_channel:
                    trace_num = files_per_channel[channel]
                else:
                    trace_num = 0
                df = pd.read_csv(file, skiprows=21, names=["time", "output", "CH3", "input"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df[["time", "output", "input"]] if "input" in df.columns else df[["time", "output"]]
                if channel not in self.channels:
                    self.channels[channel] = {}
                if 'averages' not in self.channels[channel]:
                    self.channels[channel]['averages'] = {}
                self.channels[channel]['averages'][trace_num] = {
                    'data': df,
                    'analysis': {}
                }
                if channel in files_per_channel:
                    files_per_channel[channel] += 1
                else:
                    files_per_channel[channel] = 1
            except Exception as e:
                print(f"Error processing file {file}: {e}")
        total_files = sum(files_per_channel.values())
        print(f"Loaded {total_files} averages files across {len(files_per_channel)} channels for {self.name}")
        return files_per_channel
    
    def load_data(self, singles_path="../data/casb1/singles/C1--Trace--*.txt", averages_path="../data/casb1/averages/new/ch*.csv"):
        singles_result = {}
        if singles_path:
            singles_result = self.load_singles(singles_path)
        averages_result = {}
        if averages_path:
            averages_result = self.load_averages(averages_path)
        return len(singles_result), len(averages_result)





class CASB2Processor(WaveformProcessor):
    
    def __init__(self):
        super().__init__(name="CASB2")
    
    def load_singles(self, path):
        files = glob.glob(path)
        if not files:
            print(f"Warning: No files found matching pattern: {path}")
            return {}
        files_per_channel = {}
        for file in files:
            try:
                filename = os.path.basename(file)
                ch_dir = os.path.basename(os.path.dirname(file))
                ch_match = re.search(r'ch(\d+)', ch_dir)
                if ch_match:
                    channel = int(ch_match.group(1))
                else:
                    ch_match = re.search(r'ch(\d+)', filename)
                    if ch_match:
                        channel = int(ch_match.group(1))
                    else:
                        print(f"Could not extract channel from {file}, skipping")
                        continue
                trace_match = re.search(r'tek(\d+)ALL', filename)
                if trace_match:
                    trace_num = int(trace_match.group(1))
                else:
                    if channel in files_per_channel:
                        trace_num = files_per_channel[channel]
                    else:
                        trace_num = 0
                
                df = pd.read_csv(file, skiprows=21, names=["time", "output", "input"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df[["time", "output", "input"]] if "input" in df.columns else df[["time", "output"]]
                if channel not in self.channels:
                    self.channels[channel] = {}
                if 'singles' not in self.channels[channel]:
                    self.channels[channel]['singles'] = {}
                self.channels[channel]['singles'][trace_num] = {
                    'data': df,
                    'analysis': {}
                }
                if channel in files_per_channel:
                    files_per_channel[channel] += 1
                else:
                    files_per_channel[channel] = 1
            except Exception as e:
                print(f"Error processing file {file}: {e}")
        
        # Print summary
        total_files = sum(files_per_channel.values())
        print(f"Loaded {total_files} singles files across {len(files_per_channel)} channels for {self.name}")
        
        return files_per_channel
    
    def load_averages(self, path):
        files = glob.glob(path)
        if not files:
            print(f"Warning: No files found matching pattern: {path}")
            return {}
            
        files_per_channel = {}
        
        for file in files:
            try:
                filename = os.path.basename(file)
                ch_dir = os.path.basename(os.path.dirname(file))
                ch_match = re.search(r'ch(\d+)', ch_dir)
                if ch_match:
                    channel = int(ch_match.group(1))
                else:
                    ch_match = re.search(r'ch(\d+)', filename)
                    if ch_match:
                        channel = int(ch_match.group(1))
                    else:
                        print(f"Could not extract channel from {file}, skipping")
                        continue
                trace_match = re.search(r'tek(\d+)ALL', filename)
                if trace_match:
                    trace_num = int(trace_match.group(1))
                else:
                    if channel in files_per_channel:
                        trace_num = files_per_channel[channel]
                    else:
                        trace_num = 0
                
                df = pd.read_csv(file, skiprows=21, names=["time", "output", "input"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df[["time", "output", "input"]] if "input" in df.columns else df[["time", "output"]]
                
                if channel not in self.channels:
                    self.channels[channel] = {}
                
                if 'averages' not in self.channels[channel]:
                    self.channels[channel]['averages'] = {}
                
                self.channels[channel]['averages'][trace_num] = {
                    'data': df,
                    'analysis': {}
                }
                
                if channel in files_per_channel:
                    files_per_channel[channel] += 1
                else:
                    files_per_channel[channel] = 1
                    
            except Exception as e:
                print(f"Error processing file {file}: {e}")
        
        # Print summary
        total_files = sum(files_per_channel.values())
        print(f"Loaded {total_files} averages files across {len(files_per_channel)} channels for {self.name}")
        
        return files_per_channel
    
    def load_data(self, singles_path="../data/casb2/2nhit/singles/ch*/tek*ALL.csv", averages_path="../data/casb2/2nhit/averages/ch*/tek*ALL.csv"):
        singles_result = {}
        if singles_path:
            singles_result = self.load_singles(singles_path)
        else:
            singles_result = self.load_singles()  # Use default path
        
        averages_result = {}
        if averages_path:
            averages_result = self.load_averages(averages_path)
        else:
            averages_result = self.load_averages()  # Use default path
        
        return len(singles_result), len(averages_result)





class MTCAProcessor(WaveformProcessor):
    """Processor for MTCA board data."""
    
    def __init__(self):
        super().__init__(name="MTCA1")
    
    def load_singles(self, path):
        files = glob.glob(path)
        if not files:
            print(f"Warning: No files found matching pattern: {path}")
            return {}
            
        files_per_channel = {}
        
        for file in files:
            try:
                filename = os.path.basename(file)
                
                # Extract channel and trace info
                match = re.search(r'C(\d+)--Trace--(\d+)', filename)
                if match:
                    channel = int(match.group(1))
                    trace_num = int(match.group(2))
                else:
                    match = re.search(r'Trace--(\d+)', filename)
                    if match:
                        trace_num = int(match.group(1))
                        channel = 4  # Default if not specified
                    else:
                        print(f"Could not extract info from {filename}, skipping")
                        continue
                
                # Load data - adjust skiprows based on your file format
                df = pd.read_csv(file, skiprows=6, names=["time", "output"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df['output'] = df['output'] * -1
                # Initialize channel structure if needed
                if channel not in self.channels:
                    self.channels[channel] = {}
                
                # Initialize singles dict if needed
                if 'singles' not in self.channels[channel]:
                    self.channels[channel]['singles'] = {}
                
                # Store the trace
                self.channels[channel]['singles'][trace_num] = {
                    'data': df,
                    'analysis': {}
                } 
                
                # Update counter
                if channel in files_per_channel:
                    files_per_channel[channel] += 1
                else:
                    files_per_channel[channel] = 1
                    
            except Exception as e:
                print(f"Error processing file {file}: {e}")
                
        # Print summary
        total_files = sum(files_per_channel.values())
        print(f"Loaded {total_files} singles files across {len(files_per_channel)} channels for {self.name}")
        
        return files_per_channel
    
    def load_averages(self, path):
        files = glob.glob(path)
        if not files:
            print(f"Warning: No files found matching pattern: {path}")
            return {}
            
        files_per_channel = {}
        
        for file in files:
            try:
                filename = os.path.basename(file)
                match = re.search(r'ch(\d+)', filename)
                if match:
                    channel = int(match.group(1))
                else:
                    print(f"Could not extract channel from {filename}, skipping")
                    continue
                
                # Extract trace number if available, otherwise use counter
                if channel in files_per_channel:
                    trace_num = files_per_channel[channel]
                else:
                    trace_num = 0
                
                # Load data - adjust skiprows based on your file format
                df = pd.read_csv(file, skiprows=6, names=["time", "output"])
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Initialize channel structure if needed
                if channel not in self.channels:
                    self.channels[channel] = {}
                
                # Initialize singles dict if needed
                if 'averages' not in self.channels[channel]:
                    self.channels[channel]['averages'] = {}
                
                # Store the trace
                self.channels[channel]['averages'][trace_num] = {
                    'data': df,
                    'analysis': {}
                } 
                
                # Update counter
                if channel in files_per_channel:
                    files_per_channel[channel] += 1
                else:
                    files_per_channel[channel] = 1
                    
            except Exception as e:
                print(f"Error processing file {file}: {e}")
                
        # Print summary
        total_files = sum(files_per_channel.values())
        print(f"Loaded {total_files} averages files across {len(files_per_channel)} channels for {self.name}")
        
        return files_per_channel
    
    def load_data(self, singles_path="../data/mtca1/singles/C4--Trace--*.txt", averages_path="Don't have MTCA averages yet"):
        singles_result = {}
        if singles_path:
            singles_result = self.load_singles(singles_path)
        else:
            singles_result = self.load_singles()  # Use default path
        
        averages_result = {}
        if averages_path:
            averages_result = self.load_averages(averages_path)
        else:
            try:
                averages_result = self.load_averages()  # Use default path
            except Exception as e:
                print(f"Warning: Could not load averages with default path: {e}")
        
        return len(singles_result), len(averages_result)
