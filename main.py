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

from uvot_pipeline.processing import process


DATA_DIR = Path(
    "/mnt/c/Users/jacob/research/spring_2026/"
    "image_subtraction_pipeline_to_process"
)

def main(filename):
    """
    Process a single Swift UVOT observation.
    """

    observation_path = DATA_DIR / filename

    if not observation_path.exists():
        raise FileNotFoundError(observation_path)

    print(f"Processing {observation_path.name}")

    result = process(observation_path)

    print("Done.")

    return result


if __name__ == "__main__":
    main("sw00083650004uuu_sk.img.gz")