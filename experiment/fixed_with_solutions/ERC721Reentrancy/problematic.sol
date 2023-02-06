pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721Enumerable.sol";

contract token is ERC721Enumerable, Ownable {
    mapping(address => bool) public addressMinted;

    constructor() ERC721("tokens", "demo") {}

    function mintNFT(uint256 _numOfTokens, bytes memory _signature)
        public
        payable
    {
        (bool success, string memory reason) = canMint(msg.sender, _signature);
        require(success, reason);

        for (uint256 i = 0; i < _numOfTokens; i++) {
            // ERC-721 R-eentrancy
            _safeMint(msg.sender, totalSupply() + i);
        }
        addressMinted[msg.sender] = true;
    }

    function canMint(address _address, bytes memory _signature)
        public
        view
        returns (bool, string memory)
    {
        if (addressMinted[_address]) {
            return (false, "Already withdrawn");
        }
        return (true, "");
    }
}
