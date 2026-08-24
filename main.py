# from pathlib import Path
# from uvot_pipeline.processing import process


# def main(filename):

#     #goes through 
#     observation_path = Path(
#         "/mnt/c/Users/jacob/research/spring_2026/"
#         "image_subtraction_pipeline_to_process/"
#         f"{filename}"
#     )

#     if not observation_path.exists():
#         raise FileNotFoundError(observation_path)

#     print(f"Processing {observation_path.name}")
#     process(observation_path)
#     print("Done.")

# if __name__ == "__main__":
#     main("sw00083650004uuu_sk.img.gz")

from pathlib import Path

print("In main.py: import process")
from processing import process

print("In main.py: define path")
DATA_DIR = Path(
    "/mnt/c/Users/jacob/research/spring_2026/"
    "image_subtraction_pipeline_to_process"
)

def main(filename):
    """
    Process a single Swift UVOT observation.
    """
    print("In main.py: set observation_path")

    observation_path = DATA_DIR / filename
    print(observation_path)

    print("In main.py: check if observation_path exists")

    if not observation_path.exists():
        print("In main.py: path does not exist")

        raise FileNotFoundError(observation_path)
    


    print(f"Processing {observation_path.name}")
    print("In main.py: run process from processing.py")

    result = process(observation_path)

    print("Done.")

    return result


if __name__ == "__main__":
    main("sw00030009002uw1_sk.img.gz")
