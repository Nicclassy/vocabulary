from src.text import PointProcessor

# TODO: remove ()
# TODO: remove stuff with citations e.g. (Tis author, pg 9)
# TODO: remove bad newlines (maybe not if :), what if Title then dont?

def main():
    folder_name = "analects"
    point_processor = PointProcessor(folder_name)
    point_processor.points_from_files()

    
if __name__ == "__main__":
    main()
