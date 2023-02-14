pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721Enumerable.sol";

contract token is ERC721Enumerable, Ownable {
    mapping(address => bool) public addressMinted;
    uint256 maxSupply = 500;

    constructor() ERC721("tokens", "demo") {}

    function reserveApes(address _to, uint256 _reserveAmount) public onlyOwner {
        uint256 supply = totalSupply();
        for (uint256 i = 0; i < _reserveAmount; i++) {
            // Unlimited Minting
            _safeMint(_to, supply + i);
        }
    }
}
