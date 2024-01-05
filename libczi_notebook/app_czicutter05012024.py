import tifffile
import logging
import multiprocessing
from multiprocessing import Pool
from pylibCZIrw import czi as pyczi
import numpy as np
import os, sys
from tqdm import tqdm
from tqdm.contrib import itertools as it


class FileProcessor:
    def __init__(self, folder_path, output_folder, num_processes=4, roi_width=512, roi_height=512):
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.num_processes = num_processes
        self.roi_width = roi_width
        self.roi_height = roi_height

    def libczi_cutter(self, czifile, name):
        if not os.path.exists(self.output_folder + "/" + name):
            os.makedirs(self.output_folder + "/" + name)

        from cztile.fixed_total_area_strategy import AlmostEqualBorderFixedTotalAreaStrategy2D

        tiler = AlmostEqualBorderFixedTotalAreaStrategy2D(
            total_tile_width=self.roi_width,
            total_tile_height=self.roi_height,
            min_border_width=0
        )

        
        with pyczi.open_czi(czifile) as czidoc_r:
            total_bounding_box = czidoc_r.total_bounding_box
            md_xml = czidoc_r.metadata

            tiles = tiler.tile_rectangle(czidoc_r.scenes_bounding_rectangle[0])
            tile_counter = 0
            for tile in tqdm(tiles):
                BGR_stack = np.zeros([total_bounding_box['Z'][1], 3, self.roi_height, self.roi_width])

                for z in range(0, total_bounding_box['Z'][1]):
                    tile2d = czidoc_r.read(
                        plane={"C": 0, "Z": z, "T": 0},
                        roi=(
                            tile.roi.x,
                            tile.roi.y,
                            tile.roi.w,
                            tile.roi.h
                        )
                    )

                    BGR_stack[z, :, :, :] = np.transpose(tile2d, (2, 0, 1))

                RGB_stack = np.zeros([total_bounding_box['Z'][1], 3, self.roi_height, self.roi_width])
                RGB_stack[:, 0, :, :] = BGR_stack[:, 2, :, :]
                RGB_stack[:, 1, :, :] = BGR_stack[:, 1, :, :]
                RGB_stack[:, 2, :, :] = BGR_stack[:, 0, :, :]

                img_name = name + '_X-{}_Y-{}_stack-{}.tif'.format(tile.roi.x, tile.roi.y, tile_counter)

                output_file = os.path.join(self.output_folder + "/" + name, img_name)
                tifffile.imwrite(output_file, RGB_stack.astype('uint8'), imagej=False, photometric='rgb',
                                 metadata=md_xml)
                tile_counter = tile_counter + 1

    def process_file(self, file_path):
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Processing: {file_name}")
        self.libczi_cutter(file_path, file_name)

    def process_folder(self):
        files = [os.path.join(self.folder_path, file) for file in os.listdir(self.folder_path)]

        with Pool(self.num_processes) as pool:
            pool.map(self.process_file, files)

    def setup_logging(self):
        log_format = '%(asctime)s [%(levelname)s] [%(processName)s] %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)

if __name__ == "__main__":
    # Example usage
    folder_path = "F:\\PROJECTS\\Axioscan_Analysis\\Vojtech_Abraham\\CZI_processing\\230518_ML_pyl_OB"
    output_folder = "F:\\PROJECTS\\Axioscan_Analysis\\Vojtech_Abraham\\CZI_processing\\libczi_output"
    num_processes = 4

    file_processor = FileProcessor(folder_path, output_folder, num_processes, roi_width=1920, roi_height=1600)
    file_processor.setup_logging()  # Setup logging for multiprocessing
    file_processor.process_folder()
