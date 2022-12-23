pragma solidity ^0.8.4;

import "../utils/Ownable.sol";
import "../utils/ERC721Enumerable.sol";

abstract contract ReentrancyGuard {
    // Booleans are more expensive than uint256 or any type that takes up a full
    // word because each write operation emits an extra SLOAD to first read the
    // slot's contents, replace the bits taken up by the boolean, and then write
    // back. This is the compiler's defense against contract upgrades and
    // pointer aliasing, and it cannot be disabled.

    // The values being non-zero value makes deployment a bit more expensive,
    // but in exchange the refund on every call to nonReentrant will be lower in
    // amount. Since refunds are capped to a percentage of the total
    // transaction's gas, it is best to keep them low in cases like this one, to
    // increase the likelihood of the full refund coming into effect.
    uint256 private constant _NOT_ENTERED = 1;
    uint256 private constant _ENTERED = 2;

    uint256 private _status;

    constructor() {
        _status = _NOT_ENTERED;
    }

    /**
     * @dev Prevents a contract from calling itself, directly or indirectly.
     * Calling a nonReentrant function from another nonReentrant
     * function is not supported. It is possible to prevent this from happening
     * by making the nonReentrant function external, and making it call a
     * private function that does the actual work.
     */
    modifier nonReentrant() {
        // On the first call to nonReentrant, _notEntered will be true
        require(_status != _ENTERED, "ReentrancyGuard: reentrant call");

        // Any calls to nonReentrant after this point will fail
        _status = _ENTERED;

        _;

        // By storing the original value once again, a refund is triggered (see
        // https://eips.ethereum.org/EIPS/eip-2200)
        _status = _NOT_ENTERED;
    }
}


contract token is ERC721Enumerable, Ownable{
    mapping (address => bool) public addressMinted;
    address public proxyRegistryAddress;
    uint256 mintLimit = 500;

    constructor(address marketplaceAddress) ERC721("tokens", "demo") {        
    }

    function mintNFT(uint256 _numOfTokens, bytes memory _signature) public payable {
        require(_numOfTokens <= mintLimit);   
        require(totalSupply()+(_numOfTokens) <= mintLimit);     
        (bool success, string memory reason) = canMint(msg.sender, _signature);
        require(success, reason);
        
        for(uint i = 0; i < _numOfTokens; i++) {
            _safeMint(msg.sender, totalSupply() + i);
        }
        addressMinted[msg.sender] = true;
    }

    function canMint(address _address, bytes memory _signature) public view returns (bool, string memory) {
        if (addressMinted[_address]) {
            return (false, "Already withdrawn");
        }
        return (true, "");
    }

    // function burn(uint tokenId) public {
    //     // require(_isApprovedOrOwner(_msgSender(), tokenId), "Not owner nor approved");
    //     _burn(tokenId);
    // }

    // function setProxyRegistryAddress(address _proxyRegistryAddress)
    //     external {
    //     proxyRegistryAddress = _proxyRegistryAddress;
    // }
}