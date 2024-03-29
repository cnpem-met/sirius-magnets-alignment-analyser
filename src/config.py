# flag to enable some printing for debugging
DEBUG_MODE = False

# dict with file paths of the files containing nominals points
NOM_POINTS_FILE_NAMES = {
        "booster": "../data/input/booster-pontos-nominais.txt", 
        "SR": "../data/input/anel-pontos-nominais.txt",
        "LTB": "",
        "BTS": "",
        "FE": ""
}

# dict with file paths of the files containing measured points
MEAS_POINTS_FILE_NAMES = {
        "booster": "../data/input/booster-pontos-medidos.txt", 
        "SR": "../data/input/anel-pontos-medidos.txt",
        "LTB": "",
        "BTS": "",
        "FE": ""
}

# dict with file paths of the files containing the mapping between machine-local and magnets-specific nominal frames
FRAMES_LOOKUPTABLE_FILE_NAMES = {
        "booster": "../data/input/booster-frames.csv",
        "SR": "../data/input/anel-frames.csv",
        "LTB": "",
        "BTS": "",
        "FE": ""
}

# output default path
OUTPUT_PATH = "../data/output"

# uncertainties for magnet points inside radiation shielding calculated with Monte Carlo 
# analysis per degree of freedom. Format is: [u_tx, u_ty, u_tz, u_rz]
POINTS_UNCERTAINTIES = [0.018, 0.043, 0.023, 0.026]

# offsets of the real magnetic center of the B1 magnets (in the intersection of the in and out lines)
# in relation to its nominal position. All data were measured and imported from local documentation.
OFFSETS_B1 = {
  "S01-B03-B1-LONG": -0.21939260387942738,"S01-B11-B1-LONG": 0.5027928637375751,
  "S02-B03-B1-LONG": -0.6566497181853421,"S02-B11-B1-LONG": 0.3949965569748386,
  "S03-B03-B1-LONG": -0.20433956473073067,"S03-B11-B1-LONG": 0.43980701894961527,
  "S04-B03-B1-LONG": -0.24083142212426623,"S04-B11-B1-LONG": 0.044734592439588994,
  "S05-B03-B1-LONG": -0.5419523768496219,"S05-B11-B1-LONG": 0.18519311704547903,
  "S06-B03-B1-LONG": 0.06556785208046989,"S06-B11-B1-LONG": 0.2463624895503429,
  "S07-B03-B1-LONG": -0.11493942111696498,"S07-B11-B1-LONG": 0.1979572509557599,
  "S08-B03-B1-LONG": -0.19108205778576348,"S08-B11-B1-LONG": 0.10247298117068482,
  "S09-B03-B1-LONG": -0.12550137421514052,"S09-B11-B1-LONG": 0.06038905678307316,
  "S10-B03-B1-LONG": 0.08284427370889347,"S10-B11-B1-LONG": 0.4413268321516668,
  "S11-B03-B1-LONG": -0.08184888494565712,"S11-B11-B1-LONG": 0.08674365614044177,
  "S12-B03-B1-LONG": -0.3405172535192946,"S12-B11-B1-LONG": -0.2162778490154338,
  "S13-B03-B1-LONG": -0.20894238262729203,"S13-B11-B1-LONG": 0.007992350452042274,
  "S14-B03-B1-LONG": -0.44218076120701255,"S14-B11-B1-LONG": 0.19238108862685266,
  "S15-B03-B1-LONG": -0.14013324602614574,"S15-B11-B1-LONG": 0.16677316354694938,
  "S16-B03-B1-LONG": -0.8252640711741677,"S16-B11-B1-LONG": -0.056585429443245516,
  "S17-B03-B1-LONG": -0.542567297776479,"S17-B11-B1-LONG": 0.1909879411927733,
  "S18-B03-B1-LONG": -0.1966650964553054,"S18-B11-B1-LONG": 0.15873723593284694,
  "S19-B03-B1-LONG": -0.4565826348706068,"S19-B11-B1-LONG": 0.2918019854017899,
  "S20-B03-B1-LONG": -0.4598210056558685,"S20-B11-B1-LONG": 0.5146069215769487
}