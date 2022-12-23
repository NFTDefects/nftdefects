pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721Enumerable.sol";

contract token is Ownable, ERC721Enumerable{
    uint256 public constant hareReserve = 100;
    uint256 public maxSupply = 3000;

    constructor() ERC721("tokens", "demo") {        
    }

    /**
     * Set some Bored Apes aside
     */
    function reserveApes(address _to, uint256 _reserveAmount) public onlyOwner {        
        uint supply = totalSupply();
        for (uint256 i = 0; i < _reserveAmount; i++) {
            _safeMint(_to, supply+i);
        }
        
    }
}