// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Deploy from Remix (remix.ethereum.org) with Brave Wallet on Robinhood Chain (chain ID 4663).
// One public mint: free by default, 5 per wallet, opened and closed by the owner with setMintOpen.
import "@openzeppelin/contracts@5.0.2/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts@5.0.2/token/common/ERC2981.sol";
import "@openzeppelin/contracts@5.0.2/access/Ownable.sol";

contract SBN13th is ERC721, ERC2981, Ownable {
    uint256 public constant MAX_SUPPLY = 1300;
    uint256 public totalSupply;
    bool public mintOpen;
    uint256 public price;                 // wei per token, 0 = free
    uint256 public maxPerWallet = 5;
    mapping(address => uint256) public mintedBy;

    string private baseURI;               // ipfs://<metadata CID>/ , set at reveal
    string private preRevealURI;          // one shared file shown for every token until reveal
    bool public revealed;
    string private contractMeta;          // ipfs://<CID>/collection.json, read by OpenSea

    constructor(string memory preRevealURI_, string memory contractMeta_, address royaltyReceiver, uint96 royaltyBps)
        ERC721("SBN13th", "SBN13") Ownable(msg.sender)
    {
        preRevealURI = preRevealURI_;
        contractMeta = contractMeta_;
        _setDefaultRoyalty(royaltyReceiver, royaltyBps);   // 500 = 5%
    }

    function mint(uint256 count) external payable {
        require(mintOpen, "mint closed");
        require(count > 0, "count is 0");
        uint256 used = mintedBy[msg.sender] + count;
        require(used <= maxPerWallet, "wallet limit reached");
        require(msg.value == price * count, "wrong ETH amount");
        mintedBy[msg.sender] = used;
        _mintMany(msg.sender, count);
    }

    // Owner mints the next `count` tokens to `to` (team reserve or giveaways). Use batches of about 100.
    function ownerMint(address to, uint256 count) external onlyOwner { _mintMany(to, count); }

    function _mintMany(address to, uint256 count) internal {
        require(totalSupply + count <= MAX_SUPPLY, "sold out");
        for (uint256 i = 0; i < count; i++) {
            _safeMint(to, ++totalSupply);
        }
    }

    function setMintOpen(bool open) external onlyOwner { mintOpen = open; }
    function setPrice(uint256 wei_) external onlyOwner { price = wei_; }
    function setMaxPerWallet(uint256 n) external onlyOwner { maxPerWallet = n; }
    // Reveal: pass ipfs://<metadata CID>/ once the art folder is pinned.
    function reveal(string calldata u) external onlyOwner { baseURI = u; revealed = true; }
    function setPreRevealURI(string calldata u) external onlyOwner { preRevealURI = u; }
    function setContractURI(string calldata u) external onlyOwner { contractMeta = u; }
    function setRoyalty(address r, uint96 bps) external onlyOwner { _setDefaultRoyalty(r, bps); }
    function withdraw() external onlyOwner { payable(owner()).transfer(address(this).balance); }

    function contractURI() external view returns (string memory) { return contractMeta; }
    function tokenURI(uint256 id) public view override returns (string memory) {
        _requireOwned(id);
        if (!revealed) return preRevealURI;
        return string.concat(baseURI, Strings.toString(id), ".json");
    }
    function supportsInterface(bytes4 id) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(id);
    }
}
