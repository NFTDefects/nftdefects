### fixed_toy_samples

Problematic code toy samples and safe contracts with proposed solutions.

- `RiskyMutableProxy`: 2 solutions to fix the problematic contract.
  - `solution1.sol`: hardcoded address with no setter function.
  - `solution2.sol`: set address in the constructor without setter function.
- `ERC721Reentrancy`: 2 solutions for fixing the ERC-721 Re-entrancy defect.
  - `solution1.sol`: put the modification of the mapping variable which determined the condition of minting before the safeMint function.
  - `solution2.sol`: use ReentrancyGuard for security.
- `UnlimitedMinting`: 1 solution for fixing the Unlimit Minting defect.
  - `solution.sol`: add comparison with state variable that denotes the max supply.
- `MissingRequirements`: 1 solution to fix the issue.
  - `solution.sol`: refer to official document and annotations to add mandated requirements.
- `PublicBurn`: 1 solution to fix Public Burn defect.
  - `solution.sol`: add judgment with msg.sender before performing burn.
