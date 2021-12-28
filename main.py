import sys
import SchedIO

if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        scheduler = SchedIO.import_file(input_path, output_path)
        scheduler.execute()
    else:
        raise Exception(
            'Insufficient arguments. The name of the input and output files are required')
