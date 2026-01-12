
import json

def save_result(results, filepath ):
    """Saves the results to a JSON file."""
    for qa in results:
        for key in qa.keys():
            qa[key] = str(qa[key])


    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


