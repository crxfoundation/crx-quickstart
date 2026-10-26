# CRX signature proxy

The signature proxy is a small program that signs for the seat. It runs beside the FIX engine, signs the Logon, each maker quote and each taker accept, and passes every other field as it is. The key or the custodian credential stays on the firm's host.

```text
Firm host                                                                   CRX
+------------+   FIX 4.4, TCP    +-----------------+   FIX 4.4 over TLS   +-----+
| FIX engine | <---------------> | signature proxy | <------------------> | CRX |
+------------+    127.0.0.1      +-----------------+      internet        +-----+
```

The FIX engine sends and reads standard FIX fields only. Its messages are in the [CRX FIX API](quickstart.md).

## 1. Run

1. Get the program `crx-signature-proxy` at onboarding.
2. Write `proxy.toml` (section 2).
3. Start one process for each trading session. Give each process its own `listen` port and `state_file`, and set SocketConnectPort of the session to that port:

```bash
crx-signature-proxy --config proxy.toml
```

It writes JSON lines to standard error. `"event":"listening"` shows that it waits for the FIX engine. Keep these logs for certification.

## 2. proxy.toml

Put the seat key, 64 hex characters with or without `0x`, in a file with mode 0600. Then write `proxy.toml`:

```toml
listen = "127.0.0.1:19877"
upstream = "<Provided at onboarding>"
upstream_tls = true
custody = "<seat address>"
state_file = "/var/lib/crx/proxy.state"

[domain]
name = "CRX"
version = "rulebook-1.0"
chain_id = 1
verifying_contract = "<Provided at onboarding>"

[backend]
kind = "local"
key_file = "/etc/crx/seat.key"
```

| Setting | Value |
|---|---|
| `listen` | The address for the FIX engine. A loopback address, unless `allow_remote_listen = true`. |
| `upstream` | The CRX host and port, as `host:port`. |
| `upstream_tls` | `true`: TLS 1.2 or TLS 1.3. CRX rejects a plain TCP connection. |
| `custody` | The seat address, `0x` and 40 hex characters. An EOA or an MPC address. A contract wallet cannot sign for a seat. |
| `state_file` | A new file. It keeps the signed IDs over a restart. Change to a new file only at the daily reset, with no live RFQ. |
| `[domain]` | The domain of the EIP-712 signatures. `verifying_contract` is the CRX contract address. |
| `[backend]` | The local key, or a custodian (section 3). |

## 3. Fireblocks or Fordefi

Replace the `[backend]` table with one of these tables. Give each credential file mode 0600.

```toml
[backend]
kind = "fireblocks"
api_key_file = "/etc/crx/fireblocks-api-key"
rsa_key_file = "/etc/crx/fireblocks-api-user.pem"
vault_id = "<vault account ID>"

[backend.callback]
listen = "127.0.0.1:19878"
cosigner_public_key_file = "/etc/crx/fireblocks-callback.pub.pem"
callback_private_key_file = "/etc/crx/callback.key.pem"
```

```toml
[backend]
kind = "fordefi"
token_file = "/etc/crx/fordefi-api-user-token"
signer_key_file = "/etc/crx/fordefi-api-user.pem"
vault_id = "<vault ID>"
chain = "evm_1"
```

- Set a custodian policy that signs with no approval by a person, for these messages only:
  - EIP-712 messages with domain name `CRX`, chainId 1, the CRX contract address and primaryType `Quote` or `Trade`.
  - EIP-191 messages that start with `CRX-REST-LOGIN`.
- Fireblocks: set the callback handler URL of the API user to the signature proxy, path `/v2/tx_sign_request`, with public key authentication (RSA 2048). The callback needs HTTPS: set `tls_cert_file` and `tls_key_file` in `[backend.callback]`, or put a TLS server in front of the loopback address. Use one API user for each signature proxy, and for nothing else.
- A custodian serves takers. It serves makers only when the 99th percentile time from TransactTime (60) of the R to the S sent is below 4.5 s.
- In the FIX engine, set LogonTimeout to 30 s or more and HeartBtInt (108) to 30 or more.

## 4. What it changes

| Message | Direction | Change |
|---|---|---|
| Logon (A) | To CRX | Sets Username (553) to the address that signs. Adds RawDataLength (95) = 88 and RawData (96), the Logon signature. Sets ApplicationSystemVersion (1604) to its own version. |
| Quote (S) from a maker | To CRX | Adds CrxSignature (20007), the EIP-712 `Quote` signature. |
| QuoteRequest (R) to a maker, Quote (S) to a taker | To the FIX engine | Reads RawDataLength (95) and RawData (96), the signature data, then removes both tags. |
| QuoteResponse (AJ), 694 = 1 | To CRX | Adds CrxSignature (20007), the EIP-712 `Trade` signature. |

It sets a new BodyLength (9) and CheckSum (10) on each message that it changes. All other fields stay as they are. It keeps MsgSeqNum (34) and sends no message of its own.

Domain of both EIP-712 signatures: name `CRX`, version `rulebook-1.0`, chainId `1`, verifyingContract the CRX contract address.

## 5. Messages to CRX

The samples show the trade of the [CRX FIX API](quickstart.md): a USD/MXN NDF of 1,000,000 USD, the taker buys USD. `|` stands for SOH (0x01). The keys are test keys with no funds.

Logon ([`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix)):

```text
8=FIX.4.4|9=289|35=A|34=1|49=TKR1|52=20261026-09:33:15.393|56=CRX-TRD|98=0|108=30|141=Y|1603=QuickFIX/J 2.3.3|1605=quickfixj.org|553=0xf683c26739271eeb6501552c68ed37597df8d90b|95=88|96=98Nu4OdZNuPBj2nYfJ10q1GV3s21Olvdu5UqW5hojaBJ9EHqIfxROoBp6BFsZ/UCq6XPk7JwniuvSbPZr4Mt8Bw=|1604=crx-signature-proxy/0.1.0|10=034|
```

Maker quote ([`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix)):

```text
8=FIX.4.4|9=330|35=S|34=2|49=MKR1|52=20261026-09:33:16.044|56=CRX-TRD|15=USD|38=1000000|54=1|55=USD/MXN|62=20261026-09:42:45.000|64=20261127|117=Q-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|20007=0fTVsTaYLViaVBwNzUclzYxecAfNBRjwSgwKt2Nnz88PRb/E0OjQaU0AFLu+zrHwxZY4RGLRMp5PlNs4HsPdUBw=|10=137|
```

Taker accept ([`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix)):

```text
8=FIX.4.4|9=338|35=AJ|34=4|49=TKR1|52=20261026-09:33:21.065|56=CRX-TRD|11=ORD-000201|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:33:21.065|64=20261127|117=959bbc1a-7496-82e8-af14-38c826bae7c3|167=FXNDF|541=20261127|693=QR-000201|694=1|1079=18:00:00Z|20007=qkLfhj7/MD7qVi349vO0LP4zn70FCyXxFP0sad06SNAl+zxxUrXfGVFvDw7x4/WjUS78kNoM6UtlsHdWBb/1ABw=|10=230|
```

From CRX, with the signature data in RawData (96): [`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix) and [`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix).

## 6. Logon signature

RawData (96) holds the base64 of an EIP-191 `personal_sign` signature of these 9 lines. Join the lines with `\n` (0x0A). Add no newline at the end.

```text
CRX-REST-LOGIN
Audience: crx-gateway
Chain: <chainId of the signature domain, decimal>
Method: POST
Path: /session
Custody: 0x<seat address, 40 lowercase hex>
Signer: 0x<Username (553), 40 lowercase hex>
Timestamp: <SendingTime (52) of this Logon, Unix milliseconds>
Body: 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
```

- Line 3 holds `1`. Line 6 holds the seat. Line 7 holds Username (553): the seat, or a login key address on record for the seat.
- The timestamp must be at most 120 s behind and at most 5 s ahead of CRX time.
- CRX takes each signature one time. Each Logon needs a new signature.

Test vector. Key: the public Anvil and Hardhat test account 0. It holds no funds. The seat signs.

| Item | Value |
|---|---|
| Seat address and Username (553) | `0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266` |
| SendingTime (52) | `20261020-14:30:00.000` |
| `Chain` line | `Chain: 1` |
| `Timestamp` line | `1792506600000` |
| RawDataLength (95) | `88` |
| RawData (96) | `JKdpNNytR43t65PVUy6LVUDbyqbP0OzqOSzMp2/Qv1YNDEOh/RfhNm1PWyiDWibTxDYNUFFPgyvF5MUYDzBqBRw=` |
| The same 65 bytes in hex | `0x24a76934dcad478dedeb93d5532e8b5540dbcaa6cfd0ecea392ccca76fd0bf560d0c43a1fd17e1366d4f5b28835a26d3c4360d50514f832bc5e4c5180f306a051c` |

## 7. When it does not sign

The signature proxy sends the message with no signature. For a Quote or an accept, Text (58) holds its code and one sentence, as in [`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix):

```text
TERMS_MISMATCH: The signature proxy did not sign the accept.
```

An unsigned Logon carries no Text (58). CRX then rejects the message: a Quote with AI 297 = 5, an accept with 8 150 = 8, a Logon with Logout code `LOGON_SIGNATURE_MISSING`. The log of the signature proxy gives the code and the details.

| Code | Cause |
|---|---|
| `TERMS_MISMATCH` | A field differs from the R or the S. |
| `WRONG_SIDE` | The maker Quote gives a price on the side that the R does not ask for. |
| `UNKNOWN_QUOTE_REQUEST` | No R with this QuoteReqID (131) in the last 15 minutes. |
| `UNKNOWN_QUOTE` | No S with this QuoteID (117) in the last 15 minutes. |
| `ID_REUSED` | The ID came before with other terms. |
| `SENDING_TIME_OUT_OF_RANGE` | The Logon SendingTime (52) is more than 5 s ahead of the clock or more than 120 s behind it. |
| `SIGN_TIMEOUT` | No signature before the deadline. |
| `SIGNATURE_NOT_SEAT` | The signature does not match the seat. |
| `SIGN_FAILED` | The key back end gave no signature. |

Every rule and code: [section 5 of the Rules of Engagement](rules-of-engagement.md#5-signature-proxy).
