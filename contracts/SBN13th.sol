// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Deploy from Remix (remix.ethereum.org) with Brave Wallet on Robinhood Chain (chain ID 4663).
// Mint phases: Closed -> WL -> FCFS -> Public. WL and FCFS wallets are checked with Merkle proofs
// (roots made by tools/merkle.js from tools/wl.txt and tools/fcfs.txt). The owner moves the phase forward with setPhase.
import "@openzeppelin/contracts@5.0.2/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts@5.0.2/token/common/ERC2981.sol";
import "@openzeppelin/contracts@5.0.2/access/Ownable.sol";
import "@openzeppelin/contracts@5.0.2/utils/cryptography/MerkleProof.sol";

contract SBN13th is ERC721, ERC2981, Ownable {
    enum Phase { Closed, WL, FCFS, Public }

    uint256 public constant MAX_SUPPLY = 1300;
    uint256 public totalSupply;
    Phase public phase;

    // Prices in wei: WL free, FCFS 0.0013 ETH, Public 0.013 ETH.
    uint256[4] public prices = [0, 0, 0.0013 ether, 0.013 ether];
    // Max mints per wallet in each phase (Public is per transaction).
    uint256[4] public limits = [0, 2, 2, 10];
    bytes32 public wlRoot;
    bytes32 public fcfsRoot;
    mapping(uint8 => mapping(address => uint256)) public mintedIn;

    string private baseURI;          // ipfs://<metadata CID>/ , set at reveal
    string private preRevealURI;     // one shared file shown for every token until reveal
    bool public revealed;
    string private contractMeta;     // ipfs://<CID>/collection.json, read by OpenSea

    constructor(string memory preRevealURI_, string memory contractMeta_, address royaltyReceiver, uint96 royaltyBps)
        ERC721("SBN13th", "SBN13") Ownable(msg.sender)
    {
        preRevealURI = preRevealURI_;
        contractMeta = contractMeta_;
        _setDefaultRoyalty(royaltyReceiver, royaltyBps);   // 500 = 5%
    }

    function price() external view returns (uint256) { return prices[uint8(phase)]; }

    // proof is empty for the Public phase.
    function mint(uint256 count, bytes32[] calldata proof) external payable {
        Phase p = phase;
        require(p != Phase.Closed, "mint closed");
        require(count > 0 && count <= limits[uint8(p)], "over limit");
        require(msg.value == prices[uint8(p)] * count, "wrong ETH amount");
        if (p != Phase.Public) {
            bytes32 root = p == Phase.WL ? wlRoot : fcfsRoot;
            require(MerkleProof.verify(proof, root, keccak256(abi.encodePacked(msg.sender))), "not on list");
            uint256 used = mintedIn[uint8(p)][msg.sender] + count;
            require(used <= limits[uint8(p)], "wallet limit reached");
            mintedIn[uint8(p)][msg.sender] = used;
        }
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

    // 0 Closed, 1 WL, 2 FCFS, 3 Public
    function setPhase(Phase p) external onlyOwner { phase = p; }
    function setRoots(bytes32 wl, bytes32 fcfs) external onlyOwner { wlRoot = wl; fcfsRoot = fcfs; }
    function setPrice(Phase p, uint256 wei_) external onlyOwner { prices[uint8(p)] = wei_; }
    function setLimit(Phase p, uint256 n) external onlyOwner { limits[uint8(p)] = n; }
    // Reveal: pass ipfs://<metadata CID>/ once the art folder is pinned.
    function reveal(string calldata u) external onlyOwner { baseURI = u; revealed = true; }
    function setPreRevealURI(string calldata u) external onlyOwner { preRevealURI = u; }
    function setContractURI(string calldata u) external onlyOwner { contractMeta = u; }
    function setRoyalty(address r, uint96 bps) external onlyOwner { _setDefaultRoyalty(r, bps); }
    function withdraw() external onlyOwner { payable(owner()).transfer(address(this).balance); }

    function contractURI() external view returns (string memory) { return contractMeta; }
    function _baseURI() internal view override returns (string memory) { return baseURI; }
    function tokenURI(uint256 id) public view override returns (string memory) {
        _requireOwned(id);
        if (!revealed) return preRevealURI;
        return string.concat(baseURI, Strings.toString(id), ".json");
    }
    function supportsInterface(bytes4 id) public view override(ERC721, ERC2981) returns (bool) {
        return super.supportsInterface(id);
    }
}
