import hashlib

def generate_fingerprints(peaks, fan_value=5):
    """
    peaks: list of (freq_bin, time_bin) pairs
    fan_value: how many target points for each anchor peak
    returns: list of (hash, time_bin) tuples
    """

    fingerprints = []
    peaks = sorted(peaks, key=lambda x: x[1])  # sort by time_bin

    for i, anchor in enumerate(peaks):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):
                target = peaks[i + j]
                freq1, t1 = anchor
                freq2, t2 = target
                delta_t = t2 - t1

                # Form a hash tuple (you can tune the values/features you use)
                hash_input = f"{freq1}|{freq2}|{delta_t}"
                hash_val = hashlib.sha1(hash_input.encode()).hexdigest()

                fingerprints.append((hash_val, t1))

    return fingerprints
