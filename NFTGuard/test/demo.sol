pragma solidity ^0.8.4;

import "./utils/Ownable.sol";
import "./utils/ERC721Enumerable.sol";

contract token is ERC721Enumerable, Ownable {
    mapping(address => bool) public addressMinted;
    address public proxyRegistryAddress;
    uint256 mintLimit = 500;

    constructor() ERC721("tokens", "demo") {}

    function mintNFT(uint256 _numOfTokens, bytes memory _signature)
        public
        payable
    {
        require(_numOfTokens <= mintLimit);
        require(totalSupply() + (_numOfTokens) <= mintLimit);
        (bool success, string memory reason) = canMint(msg.sender, _signature);
        require(success, reason);

        for (uint256 i = 0; i < _numOfTokens; i++) {
            // ERC-721 Reentrancy
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

    function reserveApes(address _to, uint256 _reserveAmount) public onlyOwner {
        uint256 supply = totalSupply();
        for (uint256 i = 0; i < _reserveAmount; i++) {
            // Unlimited Minting
            _safeMint(_to, supply + i);
        }
    }

    function burn(uint256 tokenId) public {
        // Public Burn
        _burn(tokenId);
    }

    function setProxyRegistryAddress(address _proxyRegistryAddress) external {
        // Risky Mutable Proxy
        proxyRegistryAddress = _proxyRegistryAddress;
    }
}
