from typing import Dict
from accelerator import Accelerator
from geom_entitites.magnet import Magnet
from geom_entitites.transformation import Transformation

class FE(Accelerator):
    def __init__(self) -> None:
        super().__init__('FE')

    def get_points_to_bestfit(self, magnet_meas: Magnet, magnet_nom: Magnet) -> Dict[str, list]:
        return super().get_points_to_bestfit(magnet_meas, magnet_nom)

    def calculate_ML_to_local_measured_transformation(self, magnet: Magnet, points: Dict[str, list]) -> Transformation:
        return super().calculate_ML_to_local_measured_transformation(magnet, points)

    def populate_magnets_with_points(self, type_of_points: str) -> None:
        super().populate_magnets_with_points(type_of_points)

    def sort_frames_by_beam_trajectory(self, type_of_points: str) -> None:
        super().sort_frames_by_beam_trajectory(type_of_points)

    def get_point_info(self, point_name: str) -> dict:
        """ Defines the expected template for the point's nomenclature and extracts meta data from it. """
        
        point_info = {}
        point_info["isCurrentAcceleratorPoint"] = True
        point_info["isValidPoint"] = True

        details = point_name.split('-')
        prefixes = ['MOG', 'EMA', 'CAR', 'CAT', 'MAN', 'IPE']
        prefix = details[0]

        if (prefix not in prefixes):
            point_info["isCurrentAcceleratorPoint"] = False
            return point_info

        if (len(details) != 3):
            point_info["isValidPoint"] = False
            return point_info

        magnet_name = details[0] + '-' + details[1]

        # dummy magnet type, because this information isn't important for FE analysis
        magnet_type = 'generic'

        point_info["location"] = prefix
        point_info["magnetType"] = magnet_type
        point_info["pointName"] = point_name
        point_info["magnetName"] = magnet_name

        return point_info