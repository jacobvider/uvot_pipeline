from uvot_pipeline.io.fits import load_observation


def main():
    print("Swift UVOT Pipeline")

    hdul = load_observation(
        r"C:\Users\jacobvider\research\uvot_pipeline\data\raw\sw00030375053uuu_sk.img.gz"
    )

    hdul.info()


if __name__ == "__main__":
    main()