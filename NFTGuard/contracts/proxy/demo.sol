pragma solidity ^0.8.4;

import "../utils/ERC721.sol";

contract token is ERC721{
    
    address public proxyRegistryAddress;
    bool public isOpenSeaProxyActive;

    constructor() ERC721("tokens", "demo") {        
    }

    function setProxyRegistryAddress(address _proxyRegistryAddress)
        external {
        proxyRegistryAddress = _proxyRegistryAddress;
    }

    function setIsOpenSeaProxyActive(bool _isOpenSeaProxyActive)
        external
    {
        isOpenSeaProxyActive = _isOpenSeaProxyActive;
    }

    function isApprovedForAll(address owner, address operator)
        public
        view
        override
        returns (bool) {
        // Whitelist OpenSea proxy contract for easy trading.
        if (address(proxyRegistryAddress) == operator) {
            return true;
        }
        return super.isApprovedForAll(owner, operator);
    }
}