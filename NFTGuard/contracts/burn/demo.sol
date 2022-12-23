pragma solidity ^0.8.0;
import "../utils/ERC721.sol";

contract token is ERC721{
    address contractAddress;

    constructor(address marketplaceAddress) ERC721("tokens", "demo") {
        contractAddress = marketplaceAddress;
    }

    function burn(uint tokenId) public {
        // require(_isApprovedOrOwner(_msgSender(), tokenId), "Not owner nor approved");
        _burn(tokenId);
    }
}