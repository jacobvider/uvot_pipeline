# from pathlib import Path

# from uvot_pipeline.processing import process


# DATA_DIR = Path(
#     "/mnt/c/Users/jacob/research/spring_2026/"
#     "image_subtraction_pipeline_to_process_backup/"
#     "image_subtraction_pipeline_to_process"
# )

# # Only process U-band images
# observations = sorted(DATA_DIR.glob("sw*uuu_sk.img.gz"))

# print(f"Found {len(observations)} observations.")

# success = 0
# failed = 0

# for i, observation_path in enumerate(observations, start=1):

#     print("\n" + "=" * 70)
#     print(f"[{i}/{len(observations)}]")
#     print(observation_path.name)

#     try:
#         process(observation_path)
#         success += 1

#     except Exception as e:
#         failed += 1
#         print(f"FAILED: {observation_path.name}")
#         print(e)

# print("\n" + "=" * 70)
# print("Batch complete.")
# print(f"Successful : {success}")
# print(f"Failed     : {failed}")

from pathlib import Path

from uvot_pipeline.main import main


DATA_DIR = Path(
    "/mnt/c/Users/jacob/research/spring_2026/"
    "image_subtraction_pipeline_to_process_backup/"
    "image_subtraction_pipeline_to_process"
)

# Only process U-band images
# observations = sorted(DATA_DIR.glob("sw*uuu_sk.img.gz"))
observations = DATA_DIR.glob("sw*uuu_sk.img.gz")

####taking them in order they appear in the list
###processes observations in order in which they were taken
###look at most promising fields first, least promising fields later, work our way out

print(f"Found {len(observations)} observations.")

success = 0
failed = 0

for i, observation in enumerate(observations, start=1):

    print("\n" + "=" * 70)
    print(f"Processing image {i} of {len(observations)}")
    print(f"File: {observation.name}")

    try:
        main(observation.name)
        success += 1

        print(f"Completed {i}/{len(observations)} images.")

    except Exception as e:
        failed += 1

        print(f"FAILED: {observation.name}")
        print(e)

    print(f"Progress: {i}/{len(observations)}")
    print(f"Successful: {success}")
    print(f"Failed: {failed}")
    
print("\n" + "=" * 70)
print("Batch complete.")
print(f"Successful : {success}")
print(f"Failed     : {failed}")