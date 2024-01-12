import os
import yappi

from analysis.extractors.ConcurrentHeatSourceEliminationExtractor import ConcurrentHeatSourceEliminationExtractor
from util import repo_root

if __name__ == '__main__':
    test_dir = os.path.join(repo_root, 'tests')
    heatmap_path = os.path.join(test_dir, 'test_resources', 'heatmap.png')
    profile_path = os.path.join(test_dir, 'profile.csv')
    extractor = ConcurrentHeatSourceEliminationExtractor(overwrite=True)
    yappi.start()
    heat_sources = extractor.get_heat_sources_from_heatmap(heatmap_path)
    yappi.stop()
    stats = yappi.get_func_stats()
    with open(profile_path, 'w') as profile_file:
        profile_file.write(f"full_name,ncall,ttot,tavg\n")  # Write csv profile header
        for stat in stats:
            profile_file.write(f"{stat.full_name},{stat.ncall},{stat.ttot},{stat.tavg}\n")
