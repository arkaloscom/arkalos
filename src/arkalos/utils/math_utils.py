import math

def asym_gaussian(x, min_res, max_res, peak_x, rising_spread, falling_spread) -> float:
    baseline = min_res
    amplitude = max_res - min_res
    if x <= peak_x:
        # Rising: Gaussian increase.
        return baseline + amplitude * math.exp(-((peak_x - x) / rising_spread) ** 2)
    else:
        # Falling: Gaussian decay.
        return baseline + amplitude * math.exp(-((x - peak_x) / falling_spread) ** 2)
    
