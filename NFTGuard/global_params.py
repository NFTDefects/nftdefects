# enable reporting of the result
REPORT_MODE = 0

# print everything in the console
PRINT_MODE = 0

# enable log file to print all exception
DEBUG_MODE = 0

# Timeout for z3 in ms
TIMEOUT = 3000

# Set this flag to 2 if we want to do evm real value unit test
# Set this flag to 3 if we want to do evm symbolic unit test
UNIT_TEST = 0

# timeout to run symbolic execution (in secs)
GLOBAL_TIMEOUT = 600

# timeout to run symbolic execution (in secs) for testing
GLOBAL_TIMEOUT_TEST = 2

# print path conditions
PRINT_PATHS = 0

# Redirect results to a json file.
STORE_RESULT = 1

# depth limit for DFS
DEPTH_LIMIT = 500

GAS_LIMIT = 400000000

LOOP_LIMIT = 200

GENERATE_TEST_CASES = 0

# Run NFTGuard in parallel
PARALLEL = 0

# Iterable of targeted smart contract names
TARGET_CONTRACTS = None

SOURCE = None

OWNER_INDEX = None
APPROVAL_INDEX = None
SUPPLY_INDEX = None
PROXY_INDEX = None

# output json elements
START = None
CONTRACT_ADDRESS = ""
CONTRACT_COUNT = 0
STORAGE_VAR_COUNT = 0
SLOAD_COUNT = 0
SSTORE_COUNT = 0
KECCAK256_COUNT = 0
PUB_FUN_COUNT = 0

ONERC721RECEIVED_SELECTOR = 353073666
ONERC721RECEIVED_SELECTOR_SHL = None
# ONERC721RECEIVED_SELECTOR_SHL = 9518847231895308808422688260840288680026284048802002002228286400486822662662


SIMPLER_SLOT_MAP = {}
NAME_TO_TYPE = {}
