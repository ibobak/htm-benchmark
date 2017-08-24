import csv
import json
from datetime import datetime
from nupic.engine import Network
from nupic.encoders import DateEncoder
import csv


_VERBOSITY = 0

# Default config fields for SPRegion
_SP_PARAMS = {
    "spatialImp": "cpp",
    "columnCount": 2048,

    "inputWidth": 0,   # will be fixed automatically
    "globalInhibition": 1,
    "numActiveColumnsPerInhArea": 40,
    "potentialPct": 0.8,
    "synPermConnected": 0.1,
    "synPermActiveInc": 0.0001,
    "synPermInactiveDec": 0.0005,

    "spVerbosity": _VERBOSITY,
    "seed": 1956,
    "boostStrength": 0.0
}

# Default config fields for TPRegion
_TM_PARAMS = {
    "temporalImp": "cpp",
    "columnCount": 2048,
    "inputWidth": 2048,
    "cellsPerColumn": 4,
    "newSynapseCount": 20,
    "initialPerm": 0.21,
    "permanenceInc": 0.1,
    "permanenceDec": 0.1,
    "minThreshold": 9,
    "activationThreshold": 12,

    "outputType": "normal",
    "pamLength": 3,

    "verbosity": _VERBOSITY,
    "seed": 1960
}

_INPUT_FILE_PATH = "../data/one_device_2015-2017.csv "

_SCALAR_ENCODER = {
    "n": 0,
    "w": 0,
    "minValue": 0,
    "maxValue": 1,
    "resolution": 0.001
}

_DATE_ENCODER = {
    "season": (31, 91.5)
}


def create_network():
    network = Network()

    m_sensor = network.addRegion("Measurement", 'ScalarSensor', json.dumps(_SCALAR_ENCODER))
    dt_sensor = network.addRegion("DT", 'py.PluggableEncoderSensor', "")
    dt_sensor.getSelf().encoder = DateEncoder(**_DATE_ENCODER)

    # Add a SPRegion, a region containing a spatial pooler
    scalar_n = m_sensor.getParameter('n')
    dt_n = dt_sensor.getSelf().encoder.getWidth()
    _SP_PARAMS["inputWidth"] = scalar_n + dt_n
    network.addRegion("sp", "py.SPRegion", json.dumps(_SP_PARAMS))

    # Input to the Spatial Pooler
    network.link("Measurement", "sp", "UniformLink", "")
    network.link("DT", "sp", "UniformLink", "")

    # Add a TPRegion, a region containing a Temporal Memory
    network.addRegion("tm", "py.TMRegion", json.dumps(_TM_PARAMS))

    # Set up links
    network.link("sp", "tm", "UniformLink", "")
    network.link("tm", "sp", "UniformLink", "", srcOutput="topDownOut", destInput="topDownIn")

    network.regions['sp'].setParameter("learningMode", True)
    network.regions['sp'].setParameter("anomalyMode", False)


    # network.regions['tm'].setParameter("topDownMode", True)  # check this

    # Make sure learning is enabled (this is the default)
    network.regions['tm'].setParameter("learningMode", True)
    # Enable anomalyMode so the tm calculates anomaly scores
    network.regions['tm'].setParameter("anomalyMode", True)
    # Enable inference mode to be able to get predictions
    network.regions['tm'].setParameter("inferenceMode", True)


    # TODO: enable all inferences
    return network


def run_network(network):
    m_sensor = network.regions['Measurement']
    dt_sensor = network.regions['DT']

    tm_region = network.regions['tm']

    csv_reader = csv.reader(open(_INPUT_FILE_PATH, 'r'))
    i = 0
    t0 = datetime.now()
    for row in csv_reader:
        i = i + 1
        m_str = row[13]
        m_sensor.setParameter('sensedValue', float(m_str))

        dt_str = row[11] + " " + row[12]
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        dt_sensor.getSelf().setSensedValue(dt)

        network.run(1)

        anomaly = tm_region.getOutputData('anomalyScore')[0]
        if (anomaly > 0.9):
            print "Date: %s, Measurement: %s, Anomaly score: %f" % (dt_str, m_str, anomaly)
        if i % 100 == 0:
            delta = datetime.now() - t0
            print "Processed %d records. The rate is %s records/second" % (i, i / delta.total_seconds())


if __name__ == "__main__":
    net = create_network()
    run_network(net)
