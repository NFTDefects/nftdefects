pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721Enumerable.sol";

contract token is ERC721Enumerable, Ownable {
    constructor() ERC721("tokens", "demo") {}

    function burn(uint256 tokenId) public {
        // add judgment with msg.sender
        require(msg.sender == ERC721.ownerOf(tokenId), 'not the owner of the token');
        _burn(tokenId);
    }
}
