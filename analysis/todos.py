"""
We decided to collect all TODOs in one file for better readability for the rest of the code.
We cannot outsource the remaining tasks to Git issues since the source code as part of a master's thesis
is handed in as a compressed zip directory only.

The evolving nature of new ideas for analysis, caused by e.g. insufficient
significance by the scanpath, lead to inconsistent code style.

Cleaning up the code involves restructuring major parts of the analysis.
Here are things that should be changed to make the code cleaner:

TODO It is possible to modularize working steps more than they currently are
 s.t. only the Analyzer accesses other major components.

TODO Move generation of directed masks and directed heatmaps forward to where all the other analysis images are plotted.

TODO When generating accumulated directed masks, always save the latest accumulated mask in case there is a crash.

TODO In the Accumulator, _influence_vector can be numpy vectorized.

TODO Averaging the vectors in grid in the Plotter can be numpy vectorized.
"""