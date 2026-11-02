# KROMT ABI Toolkit

**Offline ABI encode / decode / selector utility for the KROMT ecosystem.**

Part of the public tooling suite for [KROMT](https://kromt.xyz).

- Website: https://kromt.xyz  
- GitHub: https://github.com/kromtxyz  

---

## What it does

Helps you prepare and inspect calldata **without any network connection**:

- Compute 4-byte function selectors
- ABI-encode function arguments into calldata
- ABI-decode raw data given type list

Ideal for reviewing what an AI agent (or any dApp) is about to submit before you confirm the transaction in your wallet.

## Requirements

- Python 3.9+
- `eth-abi`, `eth-utils`, `click`, `rich`

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Function selector
python kromt_abi.py selector "transfer(address,uint256)"

# Encode calldata
python kromt_abi.py encode "transfer(address,uint256)" \
  address:0x0000000000000000000000000000000000000001 \
  uint256:1000000000000000000

# Decode data
python kromt_abi.py decode "address,uint256" 0x000000000000000000000000...

# Help
python kromt_abi.py --help
```

## Security Notes

- Fully offline for core operations.
- Never handles private keys.
- Useful as a verification step before signing any transaction.

## License

MIT — see [LICENSE](LICENSE)

---

**KROMT** · Non-custodial AI trading agent  
https://kromt.xyz · https://github.com/kromtxyz
