// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Deploy from Remix (remix.ethereum.org) with Brave Wallet on Robinhood Chain (chain ID 4663).
// Works for both launch styles: the owner can batch-mint to any wallet, and a public mint can be switched on with a price.
import "@openzeppelin/contracts@5.0.2/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts@5.0.2/token/common/ERC2981.sol";
import "@openzeppelin/contracts@5.0.2/access/Ownable.sol";

contract SBN13th is ERC721, ERC2981, Ownable {
    uint256 public constant MAX_SUPPLY = 1300;
    uint256 public totalSupply;
    uint256 public price;            // public mint price in wei (0 = free)
    bool public publicMintOpen;
    string private baseURI;          // ipfs://<metadata CID>/
    string private contractMeta;     // ipfs://<CID>/collection.json, read by OpenSea

    constructor(string memory baseURI_, string memory contractMeta_, address royaltyReceiver, uint96 royaltyBps)
        ERC721("SBN13th", "SBN13") Ownable(msg.sender)
    {
        baseURI = baseURI_;
        contractMeta = contractMeta_;
        _setDefaultRoyalty(royaltyReceiver, royaltyBps);   // 500 = 5%
    }

    // Owner mints the next `count` tokens (ids go up from 1) to `to`. Mint in batches of about 100 to stay under the gas limit.
    function ownerMint(address to, uint256 count) external onlyOwner {
        _mintMany(to, count);
    }

    function mint(uint256 count) external payable {
        require(publicMintOpen, "mint closed");
        require(count > 0 && count <= 10, "1-10 per tx");
        require(msg.value == price * count, "wrong ETH amount");
        _mintMany(msg.sender, count);
    }

    function _mintMany(address to, uint256 count) internal {
        require(totalSupply + count <= MAX_SUPPLY, "sold out");
        for (uint256 i = 0; i < count; i++) {
            _safeMint(to, ++totalSupply);
        }
    }

    function setPublicMint(bool open, uint256 priceWei) external onlyOwner { publicMintOpen = open; price = priceWei; }
    function setBaseURI(string calldata u) external onlyOwner { baseURI = u; }
    function setContractURI(string calldata u) external onlyOwner { contractMeta = u; }
    function setRoyalty(address r, uint96 bps) external onlyOwner { _setDefaultRoyalty(r, bps); }
    function withdraw() external onlyOwner { payable(owner()).transfer(address(this).balance); }

    function contractURI() external view returns (string memory) { return contractMeta; }
    function _baseURI() internal view override returns (string memory) { return baseURI; }
    function tokenURI(uint256 id) public view override returns (string memory) {
        _requireOwned(id);
        return string.concat(baseURI, Strings.toString(id), ".json");
    }
    function supportsInterface(bytes4 id) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(id);
    }
}
