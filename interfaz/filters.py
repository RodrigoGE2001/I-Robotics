"""Aqui empieza."""

from scipy.signal import filtfilt, firwin, iirfilter, kaiserord, lfilter


def iir_filter(signal, f_cutoff, f_sampling, filter_type, order, fbf=False):
    """Funcion de un filtro."""
    if filter_type == "Low pass":
        b, a = iirfilter(
            order, Wn=f_cutoff[0], fs=f_sampling, btype="low", ftype="butter"
        )
    elif filter_type == "High pass":
        b, a = iirfilter(
            order, Wn=f_cutoff[0], fs=f_sampling, btype="high", ftype="butter"
        )
    elif filter_type == "Band pass":
        b, a = iirfilter(
            order,
            Wn=[f_cutoff[0], f_cutoff[1]],
            fs=f_sampling,
            btype="band",
            ftype="butter",
        )

    if not fbf:
        filtered = lfilter(b, a, signal)
    else:
        filtered = filtfilt(b, a, signal)
    return filtered


def fir_filter(signal, nyq_rate, f_cutoff, filter_type):
    """Funcion de otro filtro."""
    width = 5.0 / nyq_rate
    ripple_db = 20.0
    N, beta = kaiserord(ripple_db, width)

    if filter_type == "Low pass":
        taps = firwin(N + 1, f_cutoff[0] / nyq_rate, window=("kaiser", beta))
    elif filter_type == "High pass":
        taps = firwin(
            N + 1, f_cutoff[0] / nyq_rate, pass_zero=False, window=("kaiser", beta)
        )
    elif filter_type == "Band pass":
        taps = firwin(
            N + 1,
            [f_cutoff[0] / nyq_rate, f_cutoff[1] / nyq_rate],
            pass_zero=False,
            window=("kaiser", beta),
        )

    filtered = lfilter(taps, 1.0, signal)
    return filtered, taps, N
