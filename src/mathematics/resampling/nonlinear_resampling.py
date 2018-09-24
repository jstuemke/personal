import numpy as np
from matplotlib import pyplot as plt


def _nonlinear_resample(data, threshold=0.15):

    data_len = len(data)
    if data_len <= 4:
        return data
    normed_threshold = threshold / data_len

    result = [data[0]]
    key_point = data[0]
    for idx in range(2, data_len - 2):

        x0, y0 = data[idx - 1]['x'], data[idx - 1]['y']
        x1, y1 = key_point['x'], key_point['y']
        x2, y2 = data[idx]['x'], data[idx]['y']

        dx = x2 - x1
        dy = y2 - y1

        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / ((dx ** 2 + dy ** 2) ** 0.5)

        if d > normed_threshold:
            # if nonlinear, log point at idx-1, keypoint = point at idx-1
            key_point = data[idx - 1]
            result.append(key_point)

    result.append(data[-1])
    return result


def _closed_loop_resample(data, start_threshold=0.15, max_iterations=100, min_percentage=0.1, max_percentage=0.2):
    if min_percentage <= 0.0:
        min_percentage = 0.01
    if max_percentage > 100.0:
        max_percentage = 100.0

    continue_condition = True
    iteration = 0
    original_data_length = len(data)
    min_end_val = min_percentage * original_data_length / 100
    max_end_val = max_percentage * original_data_length / 100
    while continue_condition:
        iteration += 1
        print("Iteration: %d" % iteration)
        result = _nonlinear_resample(data, threshold=start_threshold * iteration)
        if min_end_val < len(result) < max_end_val:
            continue_condition = False
        elif iteration > max_iterations:
            continue_condition = False

    return result


def _nonlinear_resample2(data):

    d = [0.0]
    for idx in range(1, len(data) - 1):

        x0, y0 = data[idx]['x'], data[idx]['y']
        x1, y1 = data[idx - 1]['x'], data[idx - 1]['y']
        x2, y2 = data[idx + 1]['x'], data[idx + 1]['y']

        dx = x2 - x1
        dy = y2 - y1

        d.append(
            abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / ((dx ** 2 + dy ** 2) ** 0.5)
        )

    d.append(0.0)

    return d


def _closed_loop_resample2(data, start_factor=0.05, min_percentage=0.3, max_percentage=0.5):

    distances = _nonlinear_resample2(data)
    indices = range(len(distances))
    thresholds = start_factor * np.linspace(1, 100, 100) / len(data)
    min_end_val = min_percentage * len(data)
    max_end_val = max_percentage * len(data)

    for threshold in thresholds:
        result = [data[i] for i in indices if distances[i] > threshold]
        if min_end_val < len(result) < max_end_val:
            break

    return result


if __name__ == "__main__":

    x = np.linspace(0, 1, 11000)
    y = 2 * np.sin(10 * x) - 10 * np.log(2 * x + 1)
    y_range = max(y) - min(y)
    y_noisy = y + np.random.uniform(0, 0.01 * y_range, len(x))

    data = [{'x': x_val, 'y': y_val} for (x_val, y_val) in zip(x, y_noisy)]
    resampled = _closed_loop_resample(data, start_threshold=1, max_percentage=7)
    print(len(resampled))


    xr, yr = zip(*[(v['x'], v['y']) for v in resampled])

    plt.plot(x, y_noisy)
    plt.plot(xr, yr, 'r')
    plt.scatter(xr, yr, c='r')
    plt.show()