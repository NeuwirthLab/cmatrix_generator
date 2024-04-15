import os
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from labellines import labelLine


def traverse_directory(root_dir, read_darshan_parsed_file):
    # Walk through the directory tree
    df = pd.DataFrame()
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            print(f'Processing file: {dirpath + filename}')
            if filename.endswith('.posix'):
                file_data = read_darshan_parsed_file(dirpath, filename)
                # Append the parsed data to the DataFrame
                df = df._append(file_data, ignore_index=True)
    df.sort_values(by='Filename', inplace=True)
    cal_bandwidth(df)
    cal_iops(df)
    cal_iop_counts(df)
    cal_io_intensity(df)
    return df


def read_darshan_parsed_file(dirpath, filename):
    file_path = os.path.join(dirpath, filename)
    with open(file_path, 'r') as file:
        content = file.read()

    # Define patterns to match the desired lines
    posix_pattern = re.compile(r'total_POSIX_([A-Z_]+): (\-?\d+(\.\d+)?)')
    stdio_pattern = re.compile(r'total_STDIO_([A-Z_]+): (\-?\d+(\.\d+)?)')

    # Find all matches for POSIX and STDIO patterns
    posix_matches = posix_pattern.findall(content)
    stdio_matches = stdio_pattern.findall(content)

    # Create dictionaries for POSIX and STDIO data
    posix_data = {f"POSIX_{match[0]}": [float(match[1])] for match in posix_matches}
    stdio_data = {f"STDIO_{match[0]}": [float(match[1])] for match in stdio_matches}

    # Create DataFrame for POSIX and STDIO data
    posix_df = pd.DataFrame(posix_data)
    stdio_df = pd.DataFrame(stdio_data)

    # Combine POSIX and STDIO DataFrames
    total_posix_statistics = pd.concat([posix_df, stdio_df], axis=1)
    total_posix_statistics['Filename'] = filename
    return total_posix_statistics


def cal_bandwidth(df):
    # Calculate read and write bandwidth in byte/s
    df['POSIX_BANDWIDTH_READ'] = df['POSIX_BYTES_READ'] / df['POSIX_F_READ_TIME']
    df['POSIX_BANDWIDTH_WRITE'] = df['POSIX_BYTES_WRITTEN'] / df['POSIX_F_WRITE_TIME']
    df['POSIX_BANDWIDTH'] = (df['POSIX_BYTES_READ'] + df['POSIX_BYTES_WRITTEN']) / (
            df['POSIX_F_READ_TIME'] + df['POSIX_F_WRITE_TIME'] + df['POSIX_F_META_TIME'])
    return df


def cal_iops(df):
    # Calculate IOPS
    df['POSIX_IOPS_READ'] = df['POSIX_READS'] / df['POSIX_F_READ_TIME']
    df['POSIX_IOPS_WRITE'] = df['POSIX_WRITES'] / df['POSIX_F_WRITE_TIME']
    df['POSIX_IOPS'] = (df['POSIX_READS'] + df['POSIX_WRITES'] + df['POSIX_OPENS']
                        + df['POSIX_FILENOS'] + df['POSIX_DUPS'] + df['POSIX_SEEKS'] + df['POSIX_STATS']
                        + df['POSIX_FSYNCS'] + df['POSIX_FDSYNCS']) / (
                               df['POSIX_F_READ_TIME'] + df['POSIX_F_WRITE_TIME'] + df['POSIX_F_META_TIME'])
    return df


def cal_iop_counts(df):
    df['POSIX_IO_COUNT'] = (df['POSIX_READS'] + df['POSIX_WRITES'] + df['POSIX_OPENS']
                            + df['POSIX_FILENOS'] + df['POSIX_DUPS'] + df['POSIX_SEEKS'] + df['POSIX_STATS']
                            + df['POSIX_FSYNCS'] + df['POSIX_FDSYNCS'])
    return df


def cal_io_intensity(df):
    df['POSIX_IO_INTENSITY'] = df['POSIX_IO_COUNT'] / (df['POSIX_BYTES_READ'] + df['POSIX_BYTES_WRITTEN'])
    df['POSIX_IO_INTENSITY_READ'] = df['POSIX_READS'] / df['POSIX_BYTES_READ']
    df['POSIX_IO_INTENSITY_WRITE'] = df['POSIX_WRITES'] / df['POSIX_BYTES_WRITTEN']
    return df


def append_manuel_peak(df):
    print(df.head())
    # Total Frame Physical Size	84 bytes or 1538 bytes
    # [1,000,000,000 b/s / (84 B * 8 b/B)]
    frame_per_sec_max = 14880960
    frame_per_sec_min = 812740
    frame_per_sec_mean = (frame_per_sec_max + frame_per_sec_min) / 2
    dict = {
        'POSIX_IOPS': [frame_per_sec_mean, 1293116],
        'POSIX_BANDWIDTH': [1250 * (1000 ** 2), 500 * (1000 ** 2)],
        'POSIX_IOPS_READ': [frame_per_sec_mean, 90*1000],
        'POSIX_BANDWIDTH_READ': [1250 * (1000 ** 2), 550 * (1000 ** 2)],
        'POSIX_IOPS_WRITE': [frame_per_sec_mean, 82*1000],
        'POSIX_BANDWIDTH_WRITE': [1250 * (1000 ** 2), 450 * (1000 ** 2)],
        'Filename': ['10G-Ethernet', 'SSD']
    }
    peak_net = {'POSIX_IOPS': 1293116, 'POSIX_BANDWIDTH': 1250 * (1000 ** 2), 'Filename': '10G-Ethernet'}
    peak_ssd_w_consumer = {'POSIX_IOPS': 1293116, 'POSIX_BANDWIDTH': 450 * (1000 ** 2), 'Filename': 'SSD_W_C'}
    peaks = [peak_net, peak_ssd_w_consumer]
    df_b = pd.DataFrame(dict)

    # Assuming DataFrame A is already defined
    # Concatenate DataFrame A and DataFrame B
    result_df = pd.concat([df, df_b], ignore_index=True)
    print("hi")
    return result_df


def draw_roofline(df=None, start=10**-8, end=10**0, df_peaks=None, is_read=False, is_aggregated=False):
    cmap = plt.get_cmap('tab20')
    plt.set_cmap(cmap)
    if df_peaks is None:
        peak_net = {'peak_ops': 1293116, 'peak_bw': 1250 * (1000 ** 2), 'peak_name': '10G-Ethernet'}
        peak_ssd_w_consumer = {'peak_ops': 90*1000, 'peak_bw': 450 * (1000 ** 2), 'peak_name': 'SSD_W_C'}
        peak_measured = {'peak_ops': 1293116, 'peak_bw': 260 * (1000 ** 2), 'peak_name': 'Measured_W_C'}
        peaks = [peak_net, peak_ssd_w_consumer, peak_measured]
        for p_index, peak in enumerate(peaks):
            x = np.linspace(start, end, 10000000)
            y = np.minimum(x * peak['peak_bw'], peak['peak_ops'])
            plt.plot(x, y, label=f"{peak['peak_name']}", color=cmap(p_index))
            la = f"%s MB/s" % format(peak['peak_bw'] / 1024 / 1024, '.0f')
            labelLine(plt.gca().get_lines()[-1], x=np.logspace(np.log10(start), np.log10(end), num=8)[p_index + 1],
                      label=la)
    else:
        # iterate over the rows of the DataFrame
        for index, row in df_peaks.iterrows():
            # Plot the peak performance
            x = np.linspace(start, end, 10000000)
            la = ""
            if is_aggregated:
                y = np.minimum(x * row['POSIX_BANDWIDTH'], row['POSIX_IOPS'])
                plt.plot(x, y, label=f"{row['Filename']}")
                la = f"%s MB/s" % format(row['POSIX_BANDWIDTH'] / 1000 / 1000, '.0f')
            else:
                if is_read:
                    y = np.minimum(x * row['POSIX_BANDWIDTH_READ'], row['POSIX_IOPS_READ'])
                    plt.plot(x, y, label=f"{row['Filename']}")
                    la = f"%s MB/s" % format(row['POSIX_BANDWIDTH_READ'] / 1000 / 1000, '.0f')
                if not is_read:
                    y = np.minimum(x * row['POSIX_BANDWIDTH_WRITE'], row['POSIX_IOPS_WRITE'])
                    plt.plot(x, y, label=f"{row['Filename']}")
                    la = f"%s MB/s" % format(row['POSIX_BANDWIDTH_WRITE'] / 1000 / 1000, '.0f')
            labelLine(plt.gca().get_lines()[-1], x=np.logspace(np.log10(start), np.log10(end), num=16)[index+1],
                      label=la, fontsize=8, ha='right', va='center', outline_color='white', outline_width=2)
    leg = plt.legend(loc='lower right', fontsize='small')
    plt.gca().add_artist(leg)

    # Check if the DataFrame is provided
    if df is not None:
        x_mean_values = []
        x_err_min = []
        x_err_max = []
        y_mean_values = []
        y_err_min = []
        y_err_max = []
        x_names = df['Filename']
        if is_aggregated:
            x_values = df['POSIX_IO_INTENSITY']
            y_values = df['POSIX_IOPS']
        else:
            if is_read:
                x_values = df['POSIX_IO_INTENSITY_READ']
                y_values = df['POSIX_IOPS_READ']
            if not is_read:
                x_values = df['POSIX_IO_INTENSITY_WRITE']
                y_values = df['POSIX_IOPS_WRITE']
        colors = plt.cm.viridis(np.linspace(0, 1, len(x_values)))
        app_list = []
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            min_x = x
            max_x = x
            mean_x = x

            x_err_min.append(mean_x - min_x)
            x_err_max.append(max_x - mean_x)
            x_mean_values.append(mean_x)

            min_y = y
            max_y = y
            mean_y = y

            y_err_min.append(mean_y - min_y)
            y_err_max.append(max_y - mean_y)
            y_mean_values.append(mean_y)

            # Plot each point with a unique color
            app_list.append(
                plt.errorbar(mean_x, mean_y, xerr=[[x_err_min[i]], [x_err_max[i]]],
                             yerr=[[y_err_min[i]], [y_err_max[i]]], fmt='o', color=colors[i],
                             label=x_names[i]))
        plt.legend(handles=app_list, title="Applications", bbox_to_anchor=(0, -0.4, 1, 0.2), loc="upper center",
                   mode="expand", borderaxespad=0, ncol=2, )
    if is_aggregated:
        plt.title("Empirical Roofline for Converged Computing (Aggregated)")
    else:
        if is_read:
            plt.title("Empirical Roofline for Converged Computing (Read)")
        else:
            plt.title("Empirical Roofline for Converged Computing (Write)")
    plt.ylabel("Operational Performance [IOPS]")
    plt.xlabel("Operational Intensity [IOP/Byte]")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="major", ls="-.")
    plt.tight_layout(rect=[0, 0, 0.95, 1])
    plt.show()


if __name__ == '__main__':
    root_dir = '../results/consumer01/'
    df = traverse_directory(root_dir=root_dir, read_darshan_parsed_file=read_darshan_parsed_file)
    root_dir_peak = '../results/consumer_peaks/'
    df_peaks = traverse_directory(root_dir=root_dir_peak, read_darshan_parsed_file=read_darshan_parsed_file)
    df_peaks = append_manuel_peak(df_peaks)
    # draw_roofline_consumer_write(df)
    draw_roofline(df, df_peaks=df_peaks, is_read=False)
    draw_roofline(df, df_peaks=df_peaks, is_read=True)
    draw_roofline(df, df_peaks=df_peaks, is_aggregated=True)