import json
import os
import numpy as np

class ResultsWriter:
    """Handles writing PFE results to files."""

    def __init__(self, output_directory: str, simulation_id: str):
        self.output_directory = output_directory
        self.simulation_id = simulation_id
        
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory)
                print(f"ResultsWriter: Created output directory: {self.output_directory}")
            except OSError as e:
                raise RuntimeError(f"Could not create output directory {self.output_directory}: {e}")
        else:
            print(f"ResultsWriter: Output directory already exists: {self.output_directory}")


    def _prepare_data_for_json(self, data):
        """Converts numpy arrays to lists for JSON serialization."""
        if isinstance(data, np.ndarray):
            return data.tolist()
        if isinstance(data, dict):
            return {k: self._prepare_data_for_json(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._prepare_data_for_json(i) for i in data]
        return data

    def write_pfe_results(self, aggregated_pfe_profile: np.ndarray, individual_pfe_profiles: dict):
        """
        Writes aggregated and individual PFE profiles to a JSON file.

        Args:
            aggregated_pfe_profile (np.ndarray or None): The aggregated PFE profile.
            individual_pfe_profiles (dict): Dict where keys are trade_ids and values are PFE profiles (np.ndarray).
        """
        output_data = {
            "simulation_id": self.simulation_id,
            "aggregated_pfe_profile": self._prepare_data_for_json(aggregated_pfe_profile) if aggregated_pfe_profile is not None else None,
            "individual_trade_pfe_profiles": self._prepare_data_for_json(individual_pfe_profiles)
        }
        
        filename = f"pfe_results_{self.simulation_id}.json"
        filepath = os.path.join(self.output_directory, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(output_data, f, indent=4)
            print(f"ResultsWriter: Successfully wrote PFE results to {filepath}")
        except IOError as e:
            raise RuntimeError(f"Error writing PFE results to {filepath}: {e}")
        except TypeError as e:
            raise RuntimeError(f"Error serializing PFE results to JSON: {e}")


if __name__ == '__main__':
    print("Testing reporting.output_writer...")
    test_output_dir = "temp_test_results"
    test_sim_id = "testrun123"
    
    writer = ResultsWriter(output_directory=test_output_dir, simulation_id=test_sim_id)
    
    agg_pfe = np.array([0, 15.5, 30.1, 27.8])
    ind_pfes = {
        "TradeX": np.array([0, 10.0, 20.5, 15.3]),
        "TradeY": np.array([0, 5.5, 9.6, 12.5])
    }
    
    writer.write_pfe_results(aggregated_pfe_profile=agg_pfe, individual_pfe_profiles=ind_pfes)
    print(f"Check the '{test_output_dir}' directory for 'pfe_results_{test_sim_id}.json'")

    # Clean up test directory (optional)
    # import shutil
    # if os.path.exists(test_output_dir):
    #     shutil.rmtree(test_output_dir)
    #     print(f"Cleaned up test directory: {test_output_dir}") 