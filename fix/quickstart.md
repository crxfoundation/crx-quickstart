# FIX Quickstart

Connect a FIX 4.4 engine to CRX and make a first trade in 8 steps. Each step gives a setting or message, then the result or the CRX answer. The [Rules of Engagement](rules-of-engagement.md), version 2.0, give the full rules.

The FIX engine sends and receives standard FIX fields only. The signature proxy adds the one CRX tag, CrxSignature (20007), on the way to CRX.

The samples come from a CRX test run of version 2.0 with QuickFIX/J 2.3.3. The times in [`12-logout-daily.fix`](examples/12-logout-daily.fix) come from a test of the daily reset; the sample shows the format that CRX sends. `|` stands for SOH (0x01). The sample keys are test keys with no funds.

## 1. Requirements

Get these items before the first Logon.

| Item | Requirement |
|---|---|
| Seat | An approved seat: an EOA or an MPC address with one secp256k1 key. A contract wallet cannot sign for a seat. |
| Collateral | Circle USDC on the seat, on Ethereum (chain 1), deposited through the CRX web app or the REST API. FIX has no deposit message. |
| Trade size | Minimum 100 USD |
| SenderCompID (49) | Provided at onboarding |
| CRX host and port | Provided at onboarding |
| CRX contract address | Provided at onboarding |
| Signature proxy | The program `crx-signature-proxy` for version 2.0. Provided at onboarding. |
| FIX engine | A FIX 4.4 initiator, for example QuickFIX/J |
| Host clock | On NTP. SendingTime (52) must be within 120 seconds of CRX time. On the Logon, 52 must be at most 5 seconds ahead. |

Send CRX the seat address and, for an allowlist, the source IP addresses.

Result: CRX approves the seat and sends the SenderCompID for each role, the host and port, the CRX contract address and the status page address. See [11.1 Onboarding](rules-of-engagement.md#111-onboarding).

## 2. Dictionary

Download the CRX data dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) and load it in the FIX engine. CRX also publishes a dated copy with the same bytes, [`FIX44-CRX-2026-10-25.xml`](FIX44-CRX-2026-10-25.xml). Line 2 of the file reads `CRX dictionary version: RoE 2.0, issued 2026-10-25`, then the git commit and the body MD5.

```ini
UseDataDictionary=Y
DataDictionary=FIX44-CRX.xml
AllowUnknownMsgFields=Y
ValidateUserDefinedFields=N
```

Result: the FIX engine reads MaturityTime (1079), UpfrontPriceType (1741) and UpfrontPrice (1742) inside the NoRelatedSym (146) group of QuoteRequest (R), and the field order of each message and group. A stock `FIX44.xml` lacks these fields in the group. QuickFIX C++, QuickFIX/n and QuickFIX/Go then end the group at 1079 and read Side (54) and OrderQty (38) outside it. `AllowUnknownMsgFields=Y` and `ValidateUserDefinedFields=N` keep the session up when CRX adds an optional tag. Use them only with [`FIX44-CRX.xml`](FIX44-CRX.xml) loaded. See [3.4 Engine settings](rules-of-engagement.md#34-engine-settings) and [13. Dictionary](rules-of-engagement.md#13-dictionary).

## 3. Signature proxy

Run the signature proxy on the FIX engine host, one process for each trading session. It signs the Logon, the maker Quote and the taker accept. It removes the signature data from the messages that CRX sends. The key or custodian credential stays on the firm's host.

### 3.1 Path A: local key

Put the seat key, 64 hex characters with or without `0x`, in a file with mode 0600. Then write `proxy.toml`:

```toml
listen = "127.0.0.1:19877"
upstream = "<host>:<port>"  # Provided at onboarding
upstream_tls = true
custody = "0x<seat address>"
state_file = "/var/lib/crx/proxy.state"

[domain]
name = "CRX"
version = "rulebook-1.0"
chain_id = 1
verifying_contract = "0x<CRX contract address>"  # Provided at onboarding

[backend]
kind = "local"
key_file = "/etc/crx/seat.key"
```

- `listen`: the address for the FIX engine; a loopback address unless `allow_remote_listen = true`.
- `upstream_tls = true`: TLS 1.2 or TLS 1.3. CRX rejects a plain TCP connection.
- `custody`: the seat address.
- `state_file`: a new file. It keeps the signed IDs over a restart. The signature proxy refuses a state file from version 1.x. Change to a new state file only at the daily reset, with no live RFQ.
- `[domain]`: the domain of the EIP-712 signatures. `chain_id = 1` also goes in the `Chain` line of the Logon signature. See [5.2 Tags the signature proxy adds and removes](rules-of-engagement.md#52-tags-the-signature-proxy-adds-and-removes).

### 3.2 Path B: Fireblocks or Fordefi

Replace the `[backend]` table of path A with one of these tables. Give each credential file mode 0600.

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

- Set a custodian policy that signs with no approval by a person, only for EIP-712 messages with domain name `CRX`, chainId 1, the CRX contract address and primaryType `Quote` or `Trade`, and EIP-191 messages that start with `CRX-REST-LOGIN`.
- Fireblocks: set the callback handler URL of the API user to the signature proxy, path `/v2/tx_sign_request`, with public key authentication (RSA 2048). The callback needs HTTPS: set `tls_cert_file` and `tls_key_file` in `[backend.callback]`, or put a TLS server in front of the loopback address. Use one API user for each signature proxy, and for nothing else.
- A custodian back end serves takers, and makers only when the 99th percentile time from TransactTime (60) of the R to the S sent is below 4.5 seconds.
- See [5.5 Key back ends](rules-of-engagement.md#55-key-back-ends).

### 3.3 Start

```bash
crx-signature-proxy --config proxy.toml
```

Result: the signature proxy writes JSON lines to standard error; `"event":"listening"` shows that it waits for the FIX engine. Keep these logs for certification.

## 4. FIX session

Set the session in the FIX engine. It connects to the signature proxy on 127.0.0.1, at the `listen` port of step 3.

```ini
[SESSION]
ConnectionType=initiator
BeginString=FIX.4.4
SenderCompID=<Provided at onboarding>
TargetCompID=CRX-TRD
SocketConnectHost=127.0.0.1
SocketConnectPort=19877
StartTime=17:00:30
EndTime=17:00:00
TimeZone=America/New_York
HeartBtInt=30
ReconnectInterval=5;10;20;40;60
ResetOnLogon=N
ResendRequestChunkSize=1000
UseDataDictionary=Y
DataDictionary=FIX44-CRX.xml
AllowUnknownMsgFields=Y
ValidateUserDefinedFields=N
```

- TargetCompID (56): `CRX-TRD` for trading, `CRX-DC` for drop copy.
- ReconnectInterval: `5;10;20;40;60` is the QuickFIX/J form. QuickFIX C++, QuickFIX/n and QuickFIX/Go take one value, `5`.
- With a custodian back end, set `LogonTimeout` to 30 seconds or more, and HeartBtInt (108) to 30 or more.

Answer: at 17:00:00 New York time each day, CRX ends the session with Logout code `DAILY_RESET` ([`12-logout-daily.fix`](examples/12-logout-daily.fix)). From 17:00:30, log on with MsgSeqNum (34) = 1 and ResetSeqNumFlag (141) = Y. The settings of step 4 send no 141: in QuickFIX/J, set 141 = Y in `toAdmin` on a Logon with MsgSeqNum (34) = 1. Without it, the signature proxy refuses the QuoteRequest (R) and Quote (S) messages of the new day until it restarts. See [4.8 Schedule](rules-of-engagement.md#48-schedule) and [3.4 Engine settings](rules-of-engagement.md#34-engine-settings).

```text
8=FIX.4.4|9=158|35=5|49=CRX-TRD|56=MKR1|34=2|52=20261025-17:45:11.013|58=DAILY_RESET: The session ends for the daily reset. Log on from 17:45:41 UTC. (trace 1a1742a98620000)|10=014|
```

## 5. Logon

Start the FIX engine. It sends Logon (A) to the signature proxy ([`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix)). Set ApplicationSystemName (1603) to the name and version of the FIX engine, and ApplicationSystemVendor (1605) to its vendor. CRX reads the FIX engine version for certification from 1603. The sample has no 1603 and no 1605; CRX accepts the Logon without them.

```text
8=FIX.4.4|9=72|35=A|34=1|49=TKR1|52=20261025-17:30:46.985|56=CRX-TRD|98=0|108=30|141=Y|10=095|
```

Samples 01 to 03 carry ResetSeqNumFlag (141) = Y, as on the first Logon after the daily reset. At other times, send 141 = N or no 141. The CRX answer then has no 141.

The signature proxy sets Username (553) to the seat address. It adds RawDataLength (95) = 88 and RawData (96) = the Logon signature in base64, and sets ApplicationSystemVersion (1604) to its own version. Then it sends the Logon to CRX ([`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix)). The Logon signature covers the `chain_id` of step 3, `1`. See [4.1.1 Logon signature](rules-of-engagement.md#411-logon-signature).

```text
8=FIX.4.4|9=248|35=A|34=1|49=TKR1|52=20261025-17:30:46.985|56=CRX-TRD|98=0|108=30|141=Y|553=0xedf21751cb0cd9525bafcbc269b49dab7323acdd|95=88|96=v0GnLWmFUf63doVj6dPnsKgxJsiOmA6E+RKR85DGO7Y8FuDl1PRWdNHUyIhP4REdQLlFz308L7woDNJA5HbHYhs=|1604=crx-signature-proxy/0.1.0|10=246|
```

Answer: CRX sends Logon (A) with MaxMessageSize (383) = 8192 ([`03-logon-answer.fix`](examples/03-logon-answer.fix)). Send application messages only after this answer. Keep each message at most 8,192 bytes.

```text
8=FIX.4.4|9=81|35=A|49=CRX-TRD|56=TKR1|34=1|52=20261025-17:30:47.026|98=0|108=30|141=Y|383=8192|10=002|
```

A rejected Logon gets Logout (5). Text (58) starts with the code ([`04-logon-rejected.fix`](examples/04-logon-rejected.fix)). See [9.6 Logout codes](rules-of-engagement.md#96-logout-codes).

```text
8=FIX.4.4|9=130|35=5|49=CRX-TRD|56=TKR1|34=1|52=20261025-17:44:03.363|58=LOGON_BEGIN_STRING: BeginString must be FIX.4.4. (trace 1a17429901b0023)|10=201|
```

## 6. Taker: first trade

### 6.1 Request

Send QuoteRequest (R) ([`20-quote-request.fix`](examples/20-quote-request.fix)). Set a new QuoteReqID (131), unique for the seat. In the NoRelatedSym (146) group:

- Set SecurityType (167) = `FXNDF`.
- Set the settlement time in MaturityDate (541) and MaturityTime (1079), UTC, 1 hour to 90 days ahead. 1079 has the form `HH:MM:SSZ`, with no decimals in the seconds. 1079 directly follows 541.
- Set SettlDate (64) to the date of 541. Any other date gets QuoteRequestReject (AG), code `MATURITY_MISMATCH`.
- For an upfront premium, add UpfrontPriceType (1741) = 1 and UpfrontPrice (1742), in percent of the notional, as the last fields of the group.

See [7.6 QuoteRequest (R), taker to CRX](rules-of-engagement.md#76-quoterequest-r-taker-to-crx).

```text
8=FIX.4.4|9=199|35=R|34=3|49=TKR1|52=20261025-17:30:47.036|56=CRX-TRD|131=TKR1-R-1792949447036-2|146=1|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|537=1|54=1|38=1000|64=20261025|15=USD|60=20261025-17:30:47.036|10=127|
```

Answer: QuoteStatusReport (AI) 297 = 10 (Pending), immediately ([`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix)).

```text
8=FIX.4.4|9=152|35=AI|49=CRX-TRD|56=TKR1|34=2|52=20261025-17:30:47.041|131=TKR1-R-1792949447036-2|117=TKR1-R-1792949447036-2|55=USD/MXN|60=20261025-17:30:47.037|297=10|10=180|
```

Then CRX sends the best Quote (S), 5 to 20 seconds after the R ([`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix)). The signature proxy reads and removes RawDataLength (95) and RawData (96). The FIX engine receives the S without them ([`22a-quote-to-engine.fix`](examples/22a-quote-to-engine.fix)). QuoteID (117) is a UUID. The rate is in OfferPx (133) when the taker buys and in BidPx (132) when the taker sells. With no quote, CRX sends QuoteRequestReject (AG) 658 = 8, code `NO_QUOTE`.

```text
8=FIX.4.4|9=268|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261025-17:30:52.311|131=TKR1-R-1792949447036-2|117=561527dd-df4b-8967-b6ac-6e9160d6b7bb|537=1|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|54=1|38=1000|64=20261025|15=USD|133=18.5|62=20261025-17:32:47.042|60=20261025-17:30:52.308|10=105|
```

### 6.2 Accept

Before ValidUntilTime (62) of the S, send QuoteResponse (AJ) with 694 = 1 ([`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix)). Copy QuoteID (117), Symbol (55), Side (54) and OrderQty (38) from the S. Set SecurityType (167) = `FXNDF` and Price (44) = the quoted rate. Set a new QuoteRespID (693) and a new ClOrdID (11). MaturityDate (541), MaturityTime (1079) and SettlDate (64) are optional; when sent, they must equal the S.

```text
8=FIX.4.4|9=248|35=AJ|34=4|49=TKR1|52=20261025-17:30:52.320|56=CRX-TRD|11=TKR1-O-1792949452320-4|38=1000|44=18.5|54=1|55=USD/MXN|60=20261025-17:30:52.320|64=20261025|117=561527dd-df4b-8967-b6ac-6e9160d6b7bb|167=FXNDF|541=20261025|693=TKR1-QR-1792949452320-3|694=1|10=203|
```

The signature proxy adds CrxSignature (20007), the `Trade` signature in base64 ([`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix)). See [5.4 Taker accept signature](rules-of-engagement.md#54-taker-accept-signature).

Answer: ExecutionReport (8) 150 = A (Pending New) within 100 milliseconds ([`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix)), then 150 = 0 (New) when CRX takes the accept ([`27-exec-new.fix`](examples/27-exec-new.fix)). OrderID (37) and ExecID (17) are UUIDs.

```text
8=FIX.4.4|9=372|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261025-17:30:52.326|37=fe0f0ab6-7a24-8f5d-b560-67de12f00deb|11=TKR1-O-1792949452320-4|693=TKR1-QR-1792949452320-3|17=7b863094-9926-8c9a-bea1-a70bb70a25fd|150=A|39=A|64=20261025|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|54=1|38=1000|15=USD|151=1000|14=0|6=0|60=20261025-17:30:52.323|120=USD|117=561527dd-df4b-8967-b6ac-6e9160d6b7bb|10=032|
8=FIX.4.4|9=372|35=8|49=CRX-TRD|56=TKR1|34=6|52=20261025-17:30:52.363|37=fe0f0ab6-7a24-8f5d-b560-67de12f00deb|11=TKR1-O-1792949452320-4|693=TKR1-QR-1792949452320-3|17=0ab5b529-2079-85f4-a768-3df2ceffe381|150=0|39=0|64=20261025|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|54=1|38=1000|15=USD|151=1000|14=0|6=0|60=20261025-17:30:52.360|120=USD|117=561527dd-df4b-8967-b6ac-6e9160d6b7bb|10=010|
```

### 6.3 Fill

Wait for ExecutionReport (8) 150 = F. Book the trade on 150 = F, once for each TrdMatchID (880).

Answer: 8 150 = F, 39 = 2 when the trade is final on Ethereum ([`28-exec-fill.fix`](examples/28-exec-fill.fix)), or 8 150 = 8 when the trade does not open. The fill carries SecondaryExecID (527), the on-chain trade hash, and CalculatedCcyLastQty (1056), the amount in the second currency of the Symbol.

```text
8=FIX.4.4|9=535|35=8|49=CRX-TRD|56=TKR1|34=7|52=20261025-17:30:54.605|37=fe0f0ab6-7a24-8f5d-b560-67de12f00deb|527=0xc4686427c2ba9a854310756514b1d62d35e9655f3d18bbe14652f36cb818b268|11=TKR1-O-1792949452320-4|693=TKR1-QR-1792949452320-3|17=4833b118-8f0f-8307-9079-b04c93aa9002|150=F|39=2|64=20261025|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|54=1|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261025|60=20261025-17:30:54.598|120=USD|851=2|117=561527dd-df4b-8967-b6ac-6e9160d6b7bb|880=67398b15-f79f-882b-ab81-892df5a37d04|1056=18500.00|10=128|
```

Until the settlement time, CRX can send 8 150 = H (Trade Cancel). The trade then does not stand. Remove it from the books.

If no ExecutionReport arrives 5 seconds after the AJ, send OrderStatusRequest (H). Do not send a new AJ for the same quote.

## 7. Maker: first quote

For the maker cases, CRX sends a test RFQ at 100 USD. See [11.6 Maker cases](rules-of-engagement.md#116-maker-cases).

### 7.1 Request

Wait for QuoteRequest (R) ([`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix)). The signature proxy reads and removes RawDataLength (95) and RawData (96). The FIX engine receives the R without them ([`50a-quote-request-to-engine.fix`](examples/50a-quote-request-to-engine.fix)).

- QuoteReqID (131) is a UUID. Side (54) is the taker's side.
- ExpireTime (126) is the quote deadline: TransactTime (60) + 5 seconds, or + half the RFQ life when that is shorter. CRX can close collection before 126.
- ValidUntilTime (62) is the signature end: the latest time that the trade can open on Ethereum.
- A maker test request carries Text (58) with code `TEST_REQUEST` and sets 126 to the RFQ end.

See [5.8 Timing](rules-of-engagement.md#58-timing).

```text
8=FIX.4.4|9=258|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261025-17:30:47.546|131=f4c08ede-85b7-89cc-be7c-8c4a3a9a5198|146=1|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|54=1|38=1000|64=20261025|15=USD|62=20261025-17:40:17.000|126=20261025-17:30:52.042|60=20261025-17:30:47.042|10=111|
```

### 7.2 Quote

Before ExpireTime (126), send Quote (S) ([`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix)). Copy QuoteReqID (131), Symbol (55), Side (54), OrderQty (38), Currency (15), MaturityDate (541) and MaturityTime (1079) from the R. Copy UpfrontPriceType (1741) and UpfrontPrice (1742) when the R has them. Set ValidUntilTime (62) to 62 of the R. Set a new QuoteID (117), unique for the seat. Send OfferPx (133) when 54 = 1 and BidPx (132) when 54 = 2.

```text
8=FIX.4.4|9=243|35=S|34=2|49=MKR1|52=20261025-17:30:47.558|56=CRX-TRD|15=USD|38=1000|54=1|55=USD/MXN|62=20261025-17:40:17.000|64=20261025|117=MKR1-Q-1792949447555-1|131=f4c08ede-85b7-89cc-be7c-8c4a3a9a5198|133=18.5|167=FXNDF|537=1|541=20261025|1079=19:30:00Z|10=243|
```

The signature proxy adds CrxSignature (20007), the `Quote` signature in base64 ([`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix)). See [5.3 Maker quote signature](rules-of-engagement.md#53-maker-quote-signature).

```text
8=FIX.4.4|9=338|35=S|34=2|49=MKR1|52=20261025-17:30:47.558|56=CRX-TRD|15=USD|38=1000|54=1|55=USD/MXN|62=20261025-17:40:17.000|64=20261025|117=MKR1-Q-1792949447555-1|131=f4c08ede-85b7-89cc-be7c-8c4a3a9a5198|133=18.5|167=FXNDF|537=1|541=20261025|1079=19:30:00Z|20007=Rp8mtKimxj2gcqZCu7NAJRKCan4KhGMndRcyLZ7Clw4oQTUrDlDd0hXGrmBCtDvS5ymsN1ioAvUSr5zE5LDcshs=|10=169|
```

Answer: QuoteStatusReport (AI) 297 = 0 ([`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix)). The quote is live and binding until the quote end, with no last look.

```text
8=FIX.4.4|9=165|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261025-17:30:47.577|131=f4c08ede-85b7-89cc-be7c-8c4a3a9a5198|117=MKR1-Q-1792949447555-1|55=USD/MXN|60=20261025-17:30:47.573|297=0|10=205|
```

### 7.3 Fill

Wait for ExecutionReport (8). To cancel the quote before a taker accepts it, send QuoteCancel (Z). A second Quote (S) on the same R replaces the first; CRX sends AI 297 = 6 for the first QuoteID.

Answer: 8 150 = 0 (New) when a taker accepts the quote, then 8 150 = F when the trade is final ([`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix)). Taker and maker get the same TrdMatchID (880) and SecondaryExecID (527). A quote that does not win gets AI 297 = 7 at the quote end.

```text
8=FIX.4.4|9=493|35=8|49=CRX-TRD|56=MKR1|34=6|52=20261025-17:30:54.624|37=b802ddb6-431a-823d-9a15-c18935abf4ce|527=0xc4686427c2ba9a854310756514b1d62d35e9655f3d18bbe14652f36cb818b268|11=MKR1-Q-1792949447555-1|17=bbcc19be-cfa1-8227-b973-eb5b24ee5257|150=F|39=2|64=20261025|55=USD/MXN|167=FXNDF|541=20261025|1079=19:30:00Z|54=2|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261025|60=20261025-17:30:54.616|120=USD|851=1|117=MKR1-Q-1792949447555-1|880=67398b15-f79f-882b-ab81-892df5a37d04|1056=18500.00|10=188|
```

To decline an RFQ, send QuoteRequestReject (AG) 658 = 10 before ExpireTime (126) ([`59-maker-decline.fix`](examples/59-maker-decline.fix)).

## 8. Common rejects and fixes

Each CRX reject carries Text (58) in the form `<CODE>: <sentence> (trace <id>)`. The code is the first token of 58. Base reject handling in the FIX engine on the code. When the code is unknown, act on the FIX reason field: 373, 380, 658, 300 or 103. Give the trace ID to CRX support.

| Code | Message | Cause | Fix |
|---|---|---|---|
| `LOGON_COMP_ID_UNKNOWN` | Logout (5) | CRX has no record of the SenderCompID, or TargetCompID (56) is wrong for the role. | Use the SenderCompID from onboarding. Use `CRX-TRD`, or `CRX-DC` for drop copy. |
| `LOGON_SIGNATURE_INVALID` | Logout (5) | RawData (96) is not 88 characters of canonical base64, or the signature does not match Username (553). | Check `custody` and the key of the signature proxy. |
| `LOGON_SIGNATURE_MISSING` | Logout (5) | The signature proxy did not sign the Logon. | Read the signature proxy log. |
| `UNAUTHORIZED` | Logout (5) | The address that signs is not on record for the seat, the Logon time is out of range, or CRX took the signature before. | Check `custody` and the host clock. Log on again with a new signature. |
| `SENDING_TIME_ACCURACY` | Logout (5) | SendingTime (52) is more than 120 seconds from CRX time. | Keep the host clock on NTP. |
| `LOGON_SESSION_ACTIVE` | Logout (5) | The SenderCompID has a live session. | Log on after the other session ends. |
| `SEAT_CANNOT_SIGN` | Logout (5) | The seat is a contract wallet. | Use an EOA or MPC seat. |
| `NOT_WHITELISTED` | Logout (5), AG, AI or 8 | CRX did not approve the seat for this action. | Contact CRX support. |
| `GROUP_ORDER` | Reject (3) 373 = 15 | A field of the NoRelatedSym (146) group is out of order. | Send the group fields in the order of [`FIX44-CRX.xml`](FIX44-CRX.xml). |
| `MISSING_FIELD` | AG 658 = 99, or 8 150 = 8 | A required field is absent, for example SecurityType (167) on an R or an AJ. | Add the field. Send 167 = `FXNDF`. |
| `INVALID_FIELD` | AG 658 = 99, AI 297 = 5 or 8 150 = 8 | A field has a value that CRX does not take, for example a MaturityTime (1079) with decimals in the seconds. | Correct the field. Send 1079 as `HH:MM:SSZ`. |
| `NO_QUOTE` | AG 658 = 8 | No maker quoted within the quote window. | Send a new R later, or with other terms. |
| `UNKNOWN_SYMBOL` | AG 658 = 1 | CRX does not list the Symbol. | Use a Symbol from SecurityList (y). |
| `NOTIONAL_BELOW_MINIMUM` | AG 658 = 3 | OrderQty (38) is below 100 USD. | Increase OrderQty. |
| `BAD_REQUEST` | AG 658 = 3 | The settlement time is not 1 hour to 90 days ahead. | Use a time in the range that Text gives. |
| `EXPIRY_OUTSIDE_HOURS` | AG 658 = 3 | The settlement time falls in a market closure, or in the first 15 minutes after a reopen. | Use the earliest time in Text or later. |
| `MATURITY_MISMATCH` | AG 658 = 99, or 8 150 = 8 | SettlDate (64) is not MaturityDate (541). On an AJ, 541, 64 or 1079 differs from the S. | Send 64 equal to 541. On an AJ, copy 541 and 1079 from the S. |
| `INSUFFICIENT_COLLATERAL` | AG, AI or 8 | The seat has not enough free collateral. | Deposit USDC or reduce OrderQty. |
| `QUOTE_EXPIRED` | 8 150 = 8, 103 = 4 | The accept reached CRX after ValidUntilTime (62). | Send a new R. |
| `QUOTE_MISMATCH` | 8 150 = 8 | An accept field differs from the S. | Copy the fields from the S. |
| `TRADE_STALE` | 8 150 = 8, 103 = 99 | The signature data of the quote changed before the accept. | Accept the new S that CRX sends next, with a new QuoteRespID and ClOrdID. |
| `QUOTE_WINDOW_CLOSED` | AI 297 = 5, 300 = 4 | The maker Quote reached CRX after ExpireTime (126). | Quote the next RFQ sooner. |
| `QUOTE_TERMS_MISMATCH` | AI 297 = 5, 300 = 99 | A maker Quote field differs from the R, or 62 is earlier than 62 of the R. | Copy the fields and 62 from the R. |
| A signature proxy code, for example `TERMS_MISMATCH` | AI 297 = 5, 300 = 99, or 8 150 = 8, 103 = 99 | The signature proxy did not sign. | Read the signature proxy log. |
| `SIGNATURE_INVALID` or `INVALID_SIGNATURE` | AI 297 = 5 or 8 150 = 8 | The signature does not match the seat. | Check the `[domain]` and the key of the signature proxy. |
| `SIGNATURE_MISSING` | AI 297 = 5 or 8 150 = 8 | The message has no CrxSignature (20007) and no signature proxy code. | Send the message through the signature proxy. |
| `UNSUPPORTED_MESSAGE` | j 380 = 3 | CRX does not take this MsgType, for example NewOrderSingle (D). | Accept a quote with QuoteResponse (AJ). |
| `RATE_LIMITED` | j 380 = 0. On an AJ: 8 150 = 8, 103 = 99 | The request exceeds a rate limit of the seat. | Wait for the time in Text. |

Unknown Symbol ([`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix)):

```text
8=FIX.4.4|9=216|35=AG|49=CRX-TRD|56=TKR1|34=4|52=20261025-17:37:01.883|131=TKR1-R-1792949821765-2|658=1|146=1|55=USD/XXX|58=UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace 1a17423215903c1)|10=120|
```

Late accept ([`29-exec-rejected.fix`](examples/29-exec-rejected.fix)):

```text
8=FIX.4.4|9=431|35=8|49=CRX-TRD|56=TKR1|34=9|52=20261025-17:33:58.944|37=NONE|11=TKR1-O-1792949638934-4|693=TKR1-QR-1792949638934-3|17=2f41c08f-7e42-8996-913f-1a0bf43352b6|150=8|39=8|103=4|64=20261025|55=USD/MXN|167=FXNDF|541=20261025|1079=19:31:00Z|54=1|38=1000|15=USD|151=0|14=0|6=0|60=20261025-17:33:58.936|120=USD|58=QUOTE_EXPIRED: The quote ended before an accept reached CRX. (trace 1a1742057180219)|117=a1b63e3b-9376-880c-bc58-0b584c618fca|10=210|
```

Late maker Quote ([`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix)):

```text
8=FIX.4.4|9=280|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261025-17:31:52.030|131=176e5e17-7b38-8243-8bed-4aa99977c5a6|117=MKR1-Q-1792949512010-1|55=USD/MXN|60=20261025-17:31:52.024|297=5|58=QUOTE_WINDOW_CLOSED: The quote reached CRX after ExpireTime (126) of the request. (trace 1a1741e67500115)|300=4|10=003|
```

Accept that the signature proxy did not sign, and the CRX answer ([`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix), [`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix)):

```text
8=FIX.4.4|9=311|35=AJ|34=4|49=TKR1|52=20261025-17:34:09.062|56=CRX-TRD|11=TKR1-O-1792949649062-4|38=1000|44=1.0|54=1|55=USD/MXN|60=20261025-17:34:09.062|64=20261025|117=2cd65202-72b5-8425-b5f5-930177c00a79|167=FXNDF|541=20261025|693=TKR1-QR-1792949649062-3|694=1|58=TERMS_MISMATCH: The signature proxy did not sign the accept.|10=231|
8=FIX.4.4|9=433|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261025-17:34:09.067|37=NONE|11=TKR1-O-1792949649062-4|693=TKR1-QR-1792949649062-3|17=d8f956f8-67c4-895b-b809-d270c85c76c6|150=8|39=8|103=99|64=20261025|55=USD/MXN|167=FXNDF|541=20261025|1079=19:34:00Z|54=1|38=1000|15=USD|151=0|14=0|6=0|60=20261025-17:34:09.062|120=USD|58=TERMS_MISMATCH: The signature proxy did not sign the message. (trace 1a174207ea60231)|117=2cd65202-72b5-8425-b5f5-930177c00a79|10=186|
```

NewOrderSingle (D) ([`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix)):

```text
8=FIX.4.4|9=151|35=j|49=CRX-TRD|56=TKR1|34=2|52=20261025-17:38:11.847|45=2|372=D|380=3|58=UNSUPPORTED_MESSAGE: CRX does not take this MsgType. (trace 1a174243303045a)|10=023|
```

See [9. Rejects and codes](rules-of-engagement.md#9-rejects-and-codes) for every code.

**Next:** run the certification cases on production at 100 USD. See [11. Onboarding and certification](rules-of-engagement.md#11-onboarding-and-certification).
