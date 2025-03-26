import numpy as np
import matplotlib.pyplot as plt

class WaveformProcessor:
    """
    Base class for storing and processing waveform data from different boards
    """
    def __init__(self, name=None):
        self.name = name or "Unnamed"
        self.channels = {}  # Main data structure

    def get_available_channels(self):
        return sorted(list(self.channels.keys()))

    def get_trace_data(self, waveform_type, channel, trace_index):
        if channel not in self.channels:
            raise ValueError(f"Channel {channel} not found")  
        if waveform_type not in self.channels[channel]:
            raise ValueError(f"Channel {channel} does not have {waveform_type} data")
        if trace_index not in self.channels[channel][waveform_type]:
            raise ValueError(f"Channel {channel} does not have trace {trace_index} in {waveform_type} data. There are {len(self.channels[channel][waveform_type].keys())} traces available.")
        return self.channels[channel][waveform_type][trace_index]['data']

    def get_trace_analysis(self, waveform_type, channel, trace_index):
        if channel not in self.channels:
            raise ValueError(f"Channel {channel} not found")  
        if waveform_type not in self.channels[channel]:
            raise ValueError(f"Channel {channel} does not have {waveform_type} data")
        if trace_index not in self.channels[channel][waveform_type]:
            raise ValueError(f"Channel {channel} does not have trace {trace_index} in {waveform_type} data. There are {len(self.channels[channel][waveform_type].keys())} traces available.")
        return self.channels[channel][waveform_type][trace_index]['analysis']

    def get_pedestal(self, data, baseline_start_pct, baseline_end_pct):
        start_idx = int(len(data) * baseline_start_pct)
        end_idx = int(len(data) * baseline_end_pct)
        return np.mean(data[start_idx:end_idx+1])

    def getPeakIndex(self, data, baseline_start_pct, baseline_end_pct, threshold, use_true_peak):
        peak_value = 0
        peak_index = 0
        threshold_index = 0
        crossed_threshold = False
        counter = 0
        counter_max = 2 
        ## May want to add a counter_max for different scope resolutions    
        # if self.name=='CASB1':
        #     counter_max = 8 # traces sampled with 100 ps resolution scope -
        # elif self.name=='CASB2': 
        #     counter_max = 2 # traces sampled with 400 ps resulution scope 
    
        pedestal = self.get_pedestal(data, baseline_start_pct, baseline_end_pct)
        for i in range(len(data)):
            if not crossed_threshold and data[i]-pedestal>threshold:
                crossed_threshold = True
                threshold_index = i
            if crossed_threshold and data[i]<=peak_value:
                counter += 1
            if crossed_threshold and data[i]>peak_value:
                peak_value = data[i]
                peak_index = i
            if crossed_threshold and counter>counter_max:
                break

        if use_true_peak:
            peak_index = np.argmax(data)
            
        return peak_index, threshold_index

    
    def getLowCrossingTime(self,time,data,thresh,start_i):
        over=0
        under=0
        for i in range(start_i,-1,-1):
            if data[i]<thresh:
                under=i
                over=i+1
                break
        m=(data[over]-data[under])/(time[over]-time[under])
        cross_time=time[under]+((thresh-data[under])/m)
        return cross_time

    def getHighCrossingTime(self,time,data,thresh,start_i):
        over=0
        under=0
        for i in range(start_i,len(data)):
            if data[i]>thresh:
                over=i
                under=i-1
                break
        m=(data[over]-data[under])/(time[over]-time[under])
        cross_time=time[under]+((thresh-data[under])/m)
        return cross_time

    def calculate_rise_time(self, channel, waveform_type, trace_index, baseline_start_pct, baseline_end_pct, threshold, low_pct, high_pct,use_true_peak,output,input):
        df = self.get_trace_data(waveform_type, channel, trace_index)
        time = df["time"].values * 1e9 # Convert to ns
        if output:
            signal = df["output"].values * 1e3 # Convert to mV
        elif input:
            signal = df["input"].values * 1e3 # Convert to mV
        pedestal = self.get_pedestal(signal, baseline_start_pct, baseline_end_pct)
        peak_index,threshold_index = self.getPeakIndex(signal, baseline_start_pct, baseline_end_pct, threshold,use_true_peak)
        amplitude = signal[peak_index] - pedestal
        low_threshold = pedestal + amplitude * low_pct 
        high_threshold = pedestal + amplitude * high_pct
        t_low=self.getLowCrossingTime(time,signal,low_threshold,threshold_index)
        t_high=self.getHighCrossingTime(time,signal,high_threshold,threshold_index)
        rise_time = t_high - t_low
        if output:
            analysis_dict = self.channels[channel][waveform_type][trace_index].get('analysis', {})
            analysis_dict.update({
                "output_rise_time": rise_time,
                "output_t_low": t_low,
                "output_t_high": t_high,
                "output_peak": signal[peak_index],
                "output_peak_index": peak_index,
                "output_threshold_index": threshold_index,
                "output_pedestal": pedestal
            })
            self.channels[channel][waveform_type][trace_index]['analysis'] = analysis_dict
        elif input:
            analysis_dict = self.channels[channel][waveform_type][trace_index].get('analysis', {})
            analysis_dict.update({
                "input_rise_time": rise_time,
                "input_t_low": t_low,
                "input_t_high": t_high,
                "input_peak": signal[peak_index],
                "input_peak_index": peak_index,
                "input_threshold_index": threshold_index,
                "input_pedestal": pedestal
            })
            self.channels[channel][waveform_type][trace_index]['analysis'] = analysis_dict
        else:
            raise ValueError("Please specify if a CASB input or output trace is being analyzed")
        return rise_time, t_low, t_high
    
    def calculate_all_rise_times(self, waveform_type, baseline_start_pct, baseline_end_pct, threshold, low_pct, high_pct,use_true_peak,output,input):
        results = {}
        for channel in self.channels:
            try:
                if waveform_type in self.channels[channel]:
                    for trace_index in range(len(self.channels[channel][waveform_type])):
                        rt, t_low, t_high = self.calculate_rise_time(channel,waveform_type,trace_index,baseline_start_pct,baseline_end_pct,threshold,low_pct,high_pct,use_true_peak,output,input)
                        results[channel] = rt
                else:
                    results[channel] = np.nan
            except Exception as e:
                print(f"Error processing {self.name} {waveform_type} channel {channel}: {e}")
                results[channel] = np.nan
        return results
    
    # # Uses rise time low crossing time to calculate delay, so must be called after calculating rise times   
    # def calculate_delay(self,waveform_type,trace_index):
    #     for channel in self.channels:
    #         try:
    #             analysis = self.channels[channel][waveform_type][trace_index]['analysis']
    #             if 'output_t_low' in analysis and 'input_t_low' in analysis:
    #                 delay = analysis['output_t_low'] - analysis['input_t_low']
    #                 self.channels[channel][waveform_type][trace_index]['analysis']['delay'] = delay
    #         except Exception as e:
    #             print(f"Error calculating delay for {self.name} {waveform_type} channel {channel}: {e}")
    #     return delay

    # def calculate_all_delays(self, waveform_type, trace_index):
    #     delays = {}
    #     for channel in self.channels:
    #         try:
    #             analysis = self.channels[channel][waveform_type][trace_index]['analysis']
    #             if 'output_t_low' in analysis and 'input_t_low' in analysis:
    #                 delay = analysis['output_t_low'] - analysis['input_t_low']
    #                 self.channels[channel][waveform_type][trace_index]['analysis']['delay'] = delay 
    #                 delays[channel] = delay
    #             else:
    #                 self.channels[channel][waveform_type][trace_index]['analysis']['delay'] = np.nan
    #                 delays[channel] = np.nan
    #         except Exception as e:
    #             print(f"Error calculating delay for {self.name} {waveform_type} channel {channel}: {e}")
    #             delays[channel] = np.nan
    #     return delays
                
    
    # def calculate_gains(self, waveform_type='averages', trace_index=0):
    #     gains = {}
    #     for ch in self.channels:
    #         try:
    #             if (waveform_type in self.channels[ch] and 
    #                 trace_index in self.channels[ch][waveform_type]):
    #                 df = self.get_trace_data(waveform_type, ch, trace_index)
    #                 if "input" in df.columns and ("output" in df.columns or "amplitude" in df.columns):
    #                     input_signal = df["input"].values
    #                     output_signal = df["amplitude"].values if "amplitude" in df.columns else df["output"].values
    #                     input_pedestal = self.get_pedestal(input_signal)
    #                     output_pedestal = self.get_pedestal(output_signal)
    #                     input_adj = input_signal - input_pedestal
    #                     output_adj = output_signal - output_pedestal
    #                     input_peak = np.max(np.abs(input_adj))
    #                     output_peak = np.max(np.abs(output_adj))
    #                     if input_peak != 0:
    #                         gain = output_peak / input_peak
    #                     else:
    #                         gain = np.nan
    #                     if 'analysis' not in self.channels[ch]:
    #                         self.channels[ch]['analysis'] = {}
    #                     self.channels[ch]['analysis']['gain'] = {
    #                         'value': gain,
    #                         'input_peak': input_peak,
    #                         'output_peak': output_peak,
    #                         'source': waveform_type,
    #                         'trace_index': trace_index
    #                     }
    #                     gains[ch] = gain
    #                     print(f"Channel {ch}: Gain = {gain:.4f}")
    #                 else:
    #                     print(f"Channel {ch} missing input or output data")
    #                     gains[ch] = np.nan
    #             else:
    #                 print(f"No {waveform_type} data for channel {ch} at index {trace_index}")
    #                 gains[ch] = np.nan
    #         except Exception as e:
    #             print(f"Error calculating gain for channel {ch}: {e}")
    #             gains[ch] = np.nan
    #     return gains
    
    def plot_waveform(self, channel, waveform_type, trace_index, show_rise_time_analysis,output,input,lineup=False):
        fig, ax = plt.subplots(figsize=(10, 6))
        df = self.get_trace_data(waveform_type, channel, trace_index)
        analysis = self.get_trace_analysis(waveform_type, channel, trace_index)
        time_ns = df["time"].values*1e9  
        if lineup and output and input and not show_rise_time_analysis:
            time_diff = analysis['output_t_low']-analysis['input_t_low']
            ax.plot(time_ns-time_diff, df['output']*1e3-analysis['output_pedestal'],color='blue',label=f"CASB rt={analysis['output_rise_time']:.2f} ns")
            ax.plot(time_ns, df['input']*1e3-analysis['input_pedestal'],color='orange',label=f"HVSS rt={analysis['input_rise_time']:.2f} ns")
            ax.set_xlim(analysis['input_t_low']-10,analysis['input_t_high']+30)
        if output:
            signal_mV = df["output"].values*1e3
            ax.plot(time_ns, signal_mV - analysis['output_pedestal'],color='blue',label=f"rt={analysis['output_rise_time']:.2f} ns")
            ax.set_xlim(analysis['output_t_low']-10,analysis['output_t_high']+30)
            if (show_rise_time_analysis):
                ax.axvline(x=analysis['output_t_low'], color='blue', linestyle='--') 
                ax.axvline(x=analysis['output_t_high'], color='blue', linestyle='--') 
                ax.axhline(y=0, color='grey', linestyle='--')
                ax.axhline(y=analysis['output_peak']-analysis['output_pedestal'], color='blue', linestyle='--')
        if input:
            signal_mV = df["input"].values*1e3
            ax.plot(time_ns, signal_mV - analysis['input_pedestal'],color='orange',label=f"rt={analysis['input_rise_time']:.2f} ns")
            ax.set_xlim(analysis['input_t_low']-10,analysis['input_t_high']+30)
            if (show_rise_time_analysis):
                ax.axvline(x=analysis['input_t_low'], color='orange', linestyle='--') 
                ax.axvline(x=analysis['input_t_high'], color='orange', linestyle='--') 
                ax.axhline(y=0, color='grey', linestyle='--')
                ax.axhline(y=analysis['input_peak']-analysis['input_pedestal'], color='orange', linestyle='--')
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"{self.name} Channel {channel} {waveform_type} Trace {trace_index} ")
        ax.grid(True)
        plt.tight_layout()
        plt.legend()
        return fig

    def plot_all_waveforms(self, waveform_type, show_rise_time_analysis=False,output=True,input=False,lineup=False):
        available_traces = []
        for channel in self.channels:
            if waveform_type in self.channels[channel]:
                for trace_index in range(len(self.channels[channel][waveform_type])):
                    available_traces.append(self.channels[channel][waveform_type][trace_index])
        n_cols = 4
        n_rows = len(available_traces)//n_cols+1
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(20,5*n_rows))
        for i, trace in enumerate(available_traces):
            df=trace['data']
            analysis=trace['analysis']
            ax = axs[i//n_cols, i%n_cols]
            if lineup and output and input and not show_rise_time_analysis:
                time_diff = analysis['output_t_low']-analysis['input_t_low']
                ax.plot(df['time']*1e9-time_diff, df['output']*1e3-analysis['output_pedestal'],color='blue',label=f"rt={analysis['output_rise_time']:.2f} ns")
                ax.plot(df['time']*1e9, df['input']*1e3-analysis['input_pedestal'],color='orange',label=f"rt={analysis['input_rise_time']:.2f} ns")
                ax.set_xlim(analysis['input_t_low']-10,analysis['input_t_high']+30)
            else:
                if output:
                    ax.plot(df['time']*1e9, df['output']*1e3-analysis['output_pedestal'],color='blue',label=f"rt={analysis['output_rise_time']:.2f} ns")
                    ax.set_xlim(analysis['output_t_low']-10,analysis['output_t_high']+30)
                    if show_rise_time_analysis:
                        ax.axvline(x=analysis['output_t_low'], color='blue', linestyle='--')
                        ax.axvline(x=analysis['output_t_high'], color='blue', linestyle='--') 
                        ax.axhline(y=0, color='grey', linestyle='--')
                        ax.axhline(y=analysis['output_peak']-analysis['output_pedestal'], color='blue', linestyle='--')
                if input:
                    ax.plot(df['time']*1e9, df['input']*1e3-analysis['input_pedestal'],color='orange',label=f"rt={analysis['input_rise_time']:.2f} ns")
                    ax.set_xlim(analysis['input_t_low']-10,analysis['input_t_high']+30)
                    if show_rise_time_analysis:
                        ax.axvline(x=analysis['input_t_low'], color='orange', linestyle='--')
                        ax.axvline(x=analysis['input_t_high'], color='orange', linestyle='--') 
                        ax.axhline(y=0, color='grey', linestyle='--')
                        ax.axhline(y=analysis['input_peak']-analysis['input_pedestal'], color='orange', linestyle='--')
            ax.set_title(f"{self.name} channel {channel} {waveform_type} trace {i} ")
            ax.set_xlabel('Time (ns)')
            ax.set_ylabel('Amplitude (mV)')
            ax.legend()
        plt.tight_layout

    # def plot_delays(self, highlight_extremes=True):
    #     channels_with_delays = {}
    #     for ch in self.channels:
    #         if ('analysis' in self.channels[ch] and 
    #             'delay' in self.channels[ch]['analysis']):
    #             channels_with_delays[ch] = self.channels[ch]['analysis']['delay']['value']
    #     if not channels_with_delays:
    #         raise ValueError("No delay measurements found. Run calculate_delays first.")
    #     ch_nums = sorted(list(channels_with_delays.keys()))
    #     labels = [f"CH{ch}" for ch in ch_nums]
    #     delays = [channels_with_delays[ch] for ch in ch_nums]
    #     fig, ax = plt.subplots(figsize=(12, 6))
    #     bars = ax.bar(labels, delays)
    #     if highlight_extremes:
    #         non_zero_delays = [d for d in delays if d != 0]
    #         if non_zero_delays:
    #             min_idx = delays.index(min(non_zero_delays))
    #             max_idx = delays.index(max(delays))
    #             if min_idx == delays.index(0):  # If the minimum is the reference channel (0 delay)
    #                 temp_values = delays.copy()
    #                 temp_values[min_idx] = float('inf')
    #                 min_idx = temp_values.index(min(temp_values))
    #             bars[min_idx].set_color('lightgreen')
    #             bars[max_idx].set_color('tomato')
    #             ax.text(min_idx, delays[min_idx]+20, f"{delays[min_idx]:.0f}", 
    #                    ha='center', rotation=90)
    #             ax.text(max_idx, delays[max_idx]+20, f"{delays[max_idx]:.0f}", 
    #                    ha='center', rotation=90)
    #     std_dev = np.std([d for d in delays if not np.isnan(d) and d != 0])
    #     ax.set_xlabel("Channel")
    #     ax.set_ylabel("Delay Relative to Reference Channel [ps]")
    #     ax.set_title(f"{self.name} Unity Path Relative Channel Delays")
    #     ax.set_ylim(0, max(delays) * 1.2)  # Add 20% margin
    #     ax.legend([f'$\\sigma= {std_dev:.2f}$'])
    #     ax.grid(axis='y', linestyle='--', alpha=0.7)
    #     plt.tight_layout()
    #     return fig
    
    # def plot_multiple_traces(self, channel, waveform_type='singles', max_traces=5, ax=None):
    #     if channel not in self.channels or waveform_type not in self.channels[channel]:
    #         raise ValueError(f"No {waveform_type} data found for channel {channel}")
    #     traces = self.channels[channel][waveform_type]
    #     if not traces:
    #         raise ValueError(f"No traces found for channel {channel} in {wf_type}")
    #     if ax is None:
    #         fig, ax = plt.subplots(figsize=(10, 6))
    #     trace_nums = sorted(list(traces.keys()))[:max_traces]
    #     for i, trace_num in enumerate(trace_nums):
    #         df = traces[trace_num]
    #         if "output" in df.columns:
    #             label = f"Trace {trace_num}"
    #             ax.plot(df["time"] * 1e9, df["output"], label=label, alpha=0.7)
    #         elif "amplitude" in df.columns:
    #             label = f"Trace {trace_num}"
    #             ax.plot(df["time"] * 1e9, df["amplitude"], label=label, alpha=0.7)
    #     ax.set_xlabel("Time (ns)")
    #     ax.set_ylabel("Output")
    #     ax.set_title(f"{self.name} Channel {channel} - {waveform_type.capitalize()} Traces")
    #     ax.grid(True)
    #     ax.legend()
    #     return ax
