from pathlib import Path
from uvot_pipeline.processing import process



def main():
    observation_path = Path("data/raw/sw00030375053uuu_sk.img.gz")
    process(observation_path)




if __name__ == "__main__":
    main()
