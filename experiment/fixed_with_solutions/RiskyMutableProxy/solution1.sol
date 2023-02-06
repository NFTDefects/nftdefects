pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721.sol";

contract OwnableDelegateProxy {}

contract ProxyRegistry {
    mapping(address => OwnableDelegateProxy) public proxies;
}

contract token is ERC721, Ownable {
    address public proxyRegistryAddress = 0xa5409ec958C83C3f309868babACA7c86DCB077c1;

    constructor() ERC721("tokens", "demo") {}

    function isApprovedForAll(address _owner, address _operator)
        public
        view
        override
        returns (bool isOperator)
    {
        ProxyRegistry proxyRegistry = ProxyRegistry(proxyRegistryAddress);
        if (
            address(proxyRegistry) != address(0) &&
            address(proxyRegistry.proxies(_owner)) == _operator
        ) {
            return true;
        }

        return super.isApprovedForAll(_owner, _operator);
    }
}
