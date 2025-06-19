import numpy as np

# Mapping untuk jawaban ya/tidak
yesno_map = {"yes": 1, "no": 0, "true": 1, "false": 0}

def preprocess_user_input(user_input: dict, feature_names: list) -> np.ndarray:
    """
    Convert input dictionary from user (string/number) into a numpy array
    aligned with model feature names.

    Args:
        user_input (dict): input dari user dalam bentuk {key: value}
        feature_names (list): urutan kolom input model

    Returns:
        np.ndarray: bentuk array siap diprediksi
    """
    result = {}

    for col in feature_names:
        val = user_input.get(col, None)

        if val is None:
            result[col] = 0  # Default
        elif isinstance(val, str):
            result[col] = yesno_map.get(val.strip().lower(), 0)
        else:
            result[col] = val  # numerik langsung

    return np.array([result[col] for col in feature_names])