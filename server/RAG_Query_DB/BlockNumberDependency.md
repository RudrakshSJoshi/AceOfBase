Here’s your **RAG-optimized, deep-knowledge card** on **Block Number Dependency** in Solidity smart contracts — complete with:

* 📘 Theory
* 🧪 Exploitable patterns
* ✅ Secure refactors
* 🛠️ Vulnerable line → patched line mappings
* 🔍 Red-flag detection heuristics
* 🔐 Prevention tips

---

## ⛓️ What is Block Number Dependency?

**Block number dependency** occurs when contract logic depends on `block.number`, `block.timestamp`, or similar global variables to make security-critical or game-winning decisions.
These values can be **manipulated slightly by miners**, especially in PoW chains (e.g., Ethereum pre-Merge), allowing exploits like frontrunning or jackpot rigging.

---

## ⚠️ Why It's Dangerous

| Vulnerability                                   | Risk                                                      |
| ----------------------------------------------- | --------------------------------------------------------- |
| Miners can adjust `block.timestamp`             | Up to \~15 seconds in Ethereum                            |
| Miners can adjust `block.number` (limitedly)    | Especially when combined with other manipulation          |
| RNG via block vars is predictable               | Allows attacker to **precompute and win**                 |
| Contract behavior becomes **non-deterministic** | Unsafe for critical logic like lotteries, games, auctions |

---

## 💣 Vulnerable Example: Lottery Based on Block Number

```solidity
function winLottery() public {
    if (uint256(block.number) % 100 == 0) {  // 🧨 vulnerable randomness
        payable(msg.sender).transfer(address(this).balance);
    }
}
```

---

## ✅ Safe Alternative: Commit-Reveal Randomness

```solidity
bytes32 public commit;

function commitHash(bytes32 _commit) public {
    commit = _commit;  // off-chain random number hash
}

function reveal(uint256 _number, bytes32 salt) public {
    require(keccak256(abi.encodePacked(_number, salt)) == commit, "Invalid reveal");
    // use _number as randomness source
}
```

---

## 🛠️ Line-by-Line Vulnerability → Patch Mapping

```text
uint rand = uint(block.number) % 10;
➝
Use off-chain randomness (Chainlink VRF, commit-reveal, oracles)

if (block.timestamp % 5 == 0) {
➝
Use trusted randomness or time-based triggers from verified sources
```

---

## 🔍 Red Flags & Detection Patterns

| Pattern                                   | Red Flag                    |
| ----------------------------------------- | --------------------------- |
| `block.number % N`, `block.timestamp % N` | Weak randomness             |
| `block.timestamp + offset` for expiry     | Can be manipulated slightly |
| Rewards/payouts based on block values     | Jackpot or payout riggable  |
| Game wins/losses tied to block metadata   | Predictable outcomes        |

---

## 🔐 Prevention Checklist

| Recommendation                                        | Why                       |
| ----------------------------------------------------- | ------------------------- |
| ✅ Use Chainlink VRF or oracle randomness              | Cryptographically secure  |
| ✅ Use off-chain randomness with commit-reveal         | Prevents miner control    |
| ✅ Avoid critical logic based on block vars            | Miner-resistant           |
| ✅ Add entropy from user input, hashes, or signed data | Less predictable          |
| ✅ Delay resolution one block ahead                    | To break miner prediction |

---

## 🔬 Exploit Simulation: Block Time Lottery

```solidity
function tryWin() public {
    uint win = uint(block.timestamp) % 10;
    if (win == 7) {
        payable(msg.sender).transfer(address(this).balance);
    }
}
```

### ✅ Patch:

```solidity
function tryWin(uint userEntropy) public {
    bytes32 hash = keccak256(abi.encodePacked(userEntropy, msg.sender));
    if (uint(hash) % 10 == 7) {
        payable(msg.sender).transfer(address(this).balance);
    }
}
```

**Note**: Still pseudo-random, better combined with `Chainlink VRF`.

---

## 📌 RAG-Compatible Line Examples

```text
block.timestamp % 10 == 0;
➝
Use Chainlink VRF or off-chain commit-reveal randomness

uint rand = uint(block.number + userSeed) % 10;
➝
uint rand = uint(keccak256(abi.encodePacked(userSeed, msg.sender)));

block.timestamp + 60;
➝
Prefer block-agnostic timing, or use block delay safely with fallback conditions

uint guess = uint(keccak256(abi.encodePacked(block.timestamp, block.difficulty)));
➝
Replace with oracle-based or commit-reveal randomness
```

---

## 🧰 Chainlink VRF Snippet (Secure RNG)

```solidity
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract RandomGame is VRFConsumerBase {
    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;

    constructor() VRFConsumerBase(
        0x..., // VRF Coordinator
        0x...  // LINK Token
    ) {
        keyHash = 0x...;
        fee = 0.1 * 10 ** 18;  // 0.1 LINK
    }

    function getRandomNumber() public returns (bytes32 requestId) {
        require(LINK.balanceOf(address(this)) >= fee);
        return requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override {
        randomResult = randomness;
    }
}
```

---

## 🧠 Summary

| ❌ Avoid This                | ✅ Do This                             |
| --------------------------- | ------------------------------------- |
| `block.number % x`          | Off-chain randomness or Chainlink VRF |
| `block.timestamp + N`       | External timers or commit-reveal      |
| RNG using block vars        | Use hashed input + salt/entropy       |
| Rewards tied to block state | Use secure RNG + multiple sources     |

---

Want me to bundle this and the previous 3 topics into:

* 📦 A `.md` knowledge base?
* 📊 JSON structured for vector stores like Pinecone/Weaviate?
* 🧠 Embedding-ready QA pairs?

Let me know — I can deliver it ready-to-load into your RAG system.
