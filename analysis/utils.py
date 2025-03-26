import numpy as np
import matplotlib.pyplot as plt





def plot_delays(boards, waveform_type):
    board_delays = {}
    channels = []
    
    # Data collection
    for board in boards:
        delays = []
        channels = []  # Reset channels for each board
        for channel in sorted(board.channels.keys()):
            if waveform_type in board.channels[channel]:
                channels.append(channel)
                analysis = board.channels[channel][waveform_type][0]['analysis']
                # print('--------------------------------')
                # for key, val in analysis.items():
                #     print(key,val)
                # print('--------------------------------')
                delays.append(analysis['output_t_low'])
        board_delays[board.name] = delays

    # Plotting
    plt.figure(figsize=(15, 8))
    
    x = np.arange(len(channels))
    width = 0.35
    colors = ['cornflowerblue', 'blue', 'navy']  # Colors for each board
    
    legend_bars = []  # Store the first bar of each board for legend
    
    # Plot bars for each board
    for idx, (board_name, delays) in enumerate(board_delays.items()):
        # Convert to picoseconds
        offset = min(delays)
        delays_adj = [1e3*(d-offset) for d in delays]

        # Create bars
        position = x + (idx - len(board_delays)/2 + 0.5) * width
        bars = plt.bar(position, delays_adj, width, color=colors[idx], alpha=0.7)
        legend_bars.append(bars[0])  # Save first bar for legend
        
        # Find indices for highlighting
        min_idx = delays_adj.index(min(delays_adj))
        temp_values = delays_adj.copy()
        temp_values[min_idx] = float('inf')
        second_min_idx = temp_values.index(min(temp_values))
        max_idx = delays_adj.index(max(delays_adj))
        
        # Highlight second lowest (green) and highest (red) values
        bars[second_min_idx].set_facecolor('lightgreen')
        bars[max_idx].set_facecolor('tomato')
        
        # Add value labels for second lowest and highest
        offset = (idx - len(board_delays)/2 + 0.5) * width
        plt.text(x[second_min_idx] + offset, delays_adj[second_min_idx] + 20,
                f"{delays_adj[second_min_idx]:.0f}", ha='center', rotation=90)
        plt.text(x[max_idx] + offset, delays_adj[max_idx] + 20,
                f"{delays_adj[max_idx]:.0f}", ha='center', rotation=90)

    # Customize plot
    plt.xlabel('Channel')
    plt.ylabel('Delay [ps]')
    plt.title(f'Average Channel Delays Relative to Minimum Delay')
    plt.xticks(x, [f'CH{ch+1}' for ch in channels], rotation=90)
    plt.ylim(0, 800)
    
    # Add legend with statistics
    legend_labels = []
    for board_name, delays in board_delays.items():
        mean = np.mean([1e3*(d-min(delays)) for d in delays])
        std = np.std([1e3*(d-min(delays)) for d in delays])
        legend_labels.append(f'{board_name} (μ={mean:.1f}, σ={std:.1f})')
    
    plt.legend(legend_bars, legend_labels)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()





def histogram_board_rise_times(boards, waveform_type,low_pct,high_pct):
    board_rise_times = {}
    for board in boards:
        rise_times = []
        for channel in board.channels:
            if waveform_type in board.channels[channel]:
                for trace_num in board.channels[channel][waveform_type]:
                    analysis = board.channels[channel][waveform_type][trace_num]['analysis']
                    rise_times.append(analysis['output_rise_time'])
        board_rise_times[board.name] = rise_times
        # if board.name == 'CASB2':
        #     rise_times = []
        #     for channel in board.channels:
        #         if waveform_type in board.channels[channel]:
        #             for trace_num in board.channels[channel][waveform_type]:
        #                 analysis = board.channels[channel][waveform_type][trace_num]['analysis']
        #                 rise_times.append(analysis['input_rise_time'])
        #     board_rise_times['HVSS2'] = rise_times
    # Determine shared bins
    all_data = []
    for board in board_rise_times:
        for rise_time in board_rise_times[board]:   
            all_data.append(rise_time)
    bins = np.arange(np.floor(min(all_data)*4)/4, np.ceil(max(all_data)*4)/4+0.25, 0.25)
    plt.figure(figsize=(6,6))
    for board in board_rise_times:
        plt.hist(board_rise_times[board], bins=bins, density=True, histtype='step',label=board)
    plt.xlabel('Rise Time [ns]')
    plt.ylabel('Frequency')
    plt.title(f'{low_pct*100:.0f}-{high_pct*100:.0f}% Rise times of 1 HVSS NHIT')
    plt.legend()
    plt.show()