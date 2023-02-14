pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721.sol";

contract token is ERC721, Ownable {
    constructor() ERC721("tokens", "demo") {}

    function burn(uint256 tokenId) public {
        // Public Burn
        _burn(tokenId);
    }
}
