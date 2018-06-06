import errno
import os
import sys
from os import path
from runpy import run_path

DATA_DIR = os.environ["DATA_DIR"]
RESULT_DIR = os.environ["RESULT_DIR"]

# Main script

def main(model_script_name, model_result_name):
    model_script_path = path.abspath(model_script_name)
    model_result_path = path.join(RESULT_DIR, "model", model_result_name) # Model needs to be stored in $RESULTS_DIR/model (#3660)

    print("Starting DL model training...")
    print("DATA_DIR: %s" % DATA_DIR)
    print("RESULT_DIR: %s" % RESULT_DIR)
    print("MODEL_SCRIPT_PATH: %s" % model_script_path)
    print("MODEL_RESULT_PATH: %s" % model_result_path)

    # Prepare ~/.keras dir which is used to store keras config json
    keras_user_home = path.expanduser("~/.keras")
    keras_json_path = path.join(keras_user_home,"keras.json")
    print("Preparing %s..." % keras_user_home)
    os.makedirs(keras_user_home, exist_ok=True) # prepare .keras in user's home
    if not path.exists(keras_json_path):
        with open(keras_json_path, "w") as keras_json:
            keras_json.write("{}")

    os.chdir(DATA_DIR)
    os.makedirs(path.dirname(model_result_path), exist_ok=True)

    model_script = run_path(model_script_path, { "model_result_path": model_result_path })
    model = model_script["model"]

    print("Done!")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
