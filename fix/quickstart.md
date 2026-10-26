# FIX Quickstart

Connect a FIX 4.4 engine to CRX, make a first trade as a taker and send a first quote as a maker. Steps 1 to 6 lead to the first trade. Step 7 gives the first maker quote. Step 8 lists common rejects. Each step gives a setting or message, then the result or the CRX answer. The [Rules of Engagement](rules-of-engagement.md) give the full rules.

The FIX engine sends and receives standard FIX fields only. Each step shows the messages as the FIX engine sends and receives them. The fields that the signature proxy adds and removes are in [Messages between the signature proxy and CRX](#messages-between-the-signature-proxy-and-crx).

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
| Signature proxy | The program `crx-signature-proxy`. Provided at onboarding. |
| FIX engine | A FIX 4.4 initiator, for example QuickFIX/J |
| Host clock | On NTP. SendingTime (52) must be within 120 s of CRX time. On the Logon, 52 must be at most 5 s ahead. |

Send CRX the seat address and, for an allowlist, the source IP addresses.

Result: CRX approves the seat and sends the SenderCompID for each role, the host and port, the CRX contract address and the status page address. See [11.1 Onboarding](rules-of-engagement.md#111-onboarding).

## 2. Dictionary

Download the CRX data dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) and load it in the FIX engine. Line 2 of the file gives the version and the issue date of the Rules of Engagement, then the git commit and the body MD5. CRX also publishes a dated copy with the same bytes, `FIX44-CRX-<issue date>.xml`.

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

- `listen`: the address for the FIX engine; a loopback address unless `allow_remote_listen = true`.
- `upstream`: the CRX host and port, as `host:port`.
- `upstream_tls = true`: TLS 1.2 or TLS 1.3. CRX rejects a plain TCP connection.
- `custody`: the seat address, `0x` and 40 hex characters.
- `state_file`: a new file. It keeps the signed IDs over a restart. The signature proxy refuses a state file of an earlier major version. Change to a new state file only at the daily reset, with no live RFQ.
- `[domain]`: the domain of the EIP-712 signatures. `verifying_contract` is the CRX contract address. `chain_id = 1` also goes in the `Chain` line of the Logon signature. See [5.2 Tags the signature proxy adds and removes](rules-of-engagement.md#52-tags-the-signature-proxy-adds-and-removes).

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
- A custodian back end serves takers, and makers only when the 99th percentile time from TransactTime (60) of the R to the S sent is below 4.5 s.
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
- With a custodian back end, set `LogonTimeout` to 30 s or more, and HeartBtInt (108) to 30 or more.

Answer: at 17:00:00 New York time each day, CRX ends the session with Logout code `DAILY_RESET`. From 17:00:30, log on with MsgSeqNum (34) = 1 and ResetSeqNumFlag (141) = Y. The settings of step 4 send no 141: in QuickFIX/J, set 141 = Y in `toAdmin` on a Logon with MsgSeqNum (34) = 1. Without it, the signature proxy refuses each QuoteRequest (R) and Quote (S) from CRX whose MsgSeqNum (34) is at or below the highest number it passed before the reset. See [4.8 Schedule](rules-of-engagement.md#48-schedule) and [3.4 Engine settings](rules-of-engagement.md#34-engine-settings).

The samples on this page come from a CRX test run with QuickFIX/J 2.3.3. `|` stands for SOH (0x01).

Logout at the daily reset ([`12-logout-daily.fix`](examples/12-logout-daily.fix)):

```text
8=FIX.4.4|9=158|35=5|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:48:14.116|58=DAILY_RESET: The session ends for the daily reset. Log on from 09:48:44 UTC. (trace 1a1779c4b930000)|10=086|
```

The test kit moved the daily reset into the run: the sample shows run times, not 17:00:00 New York time.

## 5. Logon

Start the FIX engine. It sends Logon (A) to the signature proxy. Set ApplicationSystemName (1603) to the name and version of the FIX engine, and ApplicationSystemVendor (1605) to its vendor. CRX reads the FIX engine version for certification from 1603.

First Logon of the day, from the FIX engine ([`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix)):

```text
8=FIX.4.4|9=113|35=A|34=1|49=TKR1|52=20261026-09:33:15.393|56=CRX-TRD|98=0|108=30|141=Y|1603=QuickFIX/J 2.3.3|1605=quickfixj.org|10=076|
```

The first Logon of the day carries ResetSeqNumFlag (141) = Y, as step 4 gives. At other times, send 141 = N or no 141. The CRX answer then has no 141.

The signature proxy adds the seat address and the Logon signature on the way to CRX. See [Messages between the signature proxy and CRX](#messages-between-the-signature-proxy-and-crx).

Answer: CRX sends Logon (A) with MaxMessageSize (383) = 8192. Send application messages only after this answer. Keep each message at most 8,192 bytes.

Answer to the first Logon of the day ([`03-logon-answer.fix`](examples/03-logon-answer.fix)):

```text
8=FIX.4.4|9=81|35=A|49=CRX-TRD|56=TKR1|34=1|52=20261026-09:33:15.503|98=0|108=30|141=Y|383=8192|10=002|
```

A rejected Logon gets Logout (5). Text (58) starts with the code. See [9.6 Logout codes](rules-of-engagement.md#96-logout-codes).

Logon reject ([`04-logon-rejected.fix`](examples/04-logon-rejected.fix)):

```text
8=FIX.4.4|9=130|35=5|49=CRX-TRD|56=TKR1|34=1|52=20261026-09:47:00.015|58=LOGON_BEGIN_STRING: BeginString must be FIX.4.4. (trace 1a1779b2a2c0023)|10=036|
```

## 6. Taker: first trade

The samples of steps 6 and 7 show one trade: a USD/MXN NDF of 1,000,000 USD, the taker buys USD. Settlement is on the fixing date, one month after the trade date and moved to the next business day, at 18:00:00 UTC: SettlDate (64) = MaturityDate (541). See [10.3 Settlement time](rules-of-engagement.md#103-settlement-time). The FIX engine sets the IDs `ORD-…` in ClOrdID (11), `RFQ-…` in QuoteReqID (131), `QR-…` in QuoteRespID (693) and `Q-…` in the maker QuoteID (117). The IDs that CRX sets are UUIDs.

The signature proxy removes the signature data from the Quote (S) and signs the QuoteResponse (AJ). See [Messages between the signature proxy and CRX](#messages-between-the-signature-proxy-and-crx).

### 6.1 Request

Send QuoteRequest (R). Set a new QuoteReqID (131), unique for the seat. In the NoRelatedSym (146) group:

- Set SecurityType (167) = `FXNDF`.
- Set the settlement time in MaturityDate (541) and MaturityTime (1079), UTC, 1 hour to 90 days ahead. 1079 has the form `HH:MM:SSZ`, with no decimals in the seconds. 1079 directly follows 541.
- Set SettlDate (64) to the date of 541. Any other date gets QuoteRequestReject (AG), code `MATURITY_MISMATCH`.
- For an upfront premium, add UpfrontPriceType (1741) = 1 and UpfrontPrice (1742), in percent of the notional, as the last fields of the group.

See [7.6 QuoteRequest (R), taker to CRX](rules-of-engagement.md#76-quoterequest-r-taker-to-crx).

QuoteRequest from the FIX engine ([`20-quote-request.fix`](examples/20-quote-request.fix)):

```text
8=FIX.4.4|9=190|35=R|34=3|49=TKR1|52=20261026-09:33:15.511|56=CRX-TRD|131=RFQ-000201|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|537=1|54=1|38=1000000|64=20261127|15=USD|60=20261026-09:33:15.510|10=094|
```

Answer: QuoteStatusReport (AI) 297 = 10 (Pending), immediately. At Pending, QuoteID (117) repeats QuoteReqID (131).

Pending ([`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix)):

```text
8=FIX.4.4|9=128|35=AI|49=CRX-TRD|56=TKR1|34=2|52=20261026-09:33:15.634|131=RFQ-000201|117=RFQ-000201|55=USD/MXN|60=20261026-09:33:15.520|297=10|10=114|
```

Then CRX sends the best Quote (S), 5 to 20 s after the R. The rate is in OfferPx (133) when the taker buys and in BidPx (132) when the taker sells. With no quote, CRX sends QuoteRequestReject (AG) 658 = 8, code `NO_QUOTE`.

Quote to the FIX engine ([`22a-quote-to-engine.fix`](examples/22a-quote-to-engine.fix)):

```text
8=FIX.4.4|9=262|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:33:21.054|131=RFQ-000201|117=959bbc1a-7496-82e8-af14-38c826bae7c3|537=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|133=18.4753|62=20261026-09:35:15.781|60=20261026-09:33:21.048|10=209|
```

### 6.2 Accept

Before ValidUntilTime (62) of the S, send QuoteResponse (AJ) with 694 = 1. Copy QuoteID (117), Symbol (55), Side (54) and OrderQty (38) from the S. Set SecurityType (167) = `FXNDF` and Price (44) = the quoted rate. Set a new QuoteRespID (693) and a new ClOrdID (11). MaturityDate (541), MaturityTime (1079) and SettlDate (64) are optional; when sent, they must equal the S.

QuoteResponse from the FIX engine ([`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix)):

```text
8=FIX.4.4|9=243|35=AJ|34=4|49=TKR1|52=20261026-09:33:21.065|56=CRX-TRD|11=ORD-000201|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:33:21.065|64=20261127|117=959bbc1a-7496-82e8-af14-38c826bae7c3|167=FXNDF|541=20261127|693=QR-000201|694=1|1079=18:00:00Z|10=011|
```

Answer: ExecutionReport (8) 150 = A (Pending New) within 100 ms, then 150 = 0 (New) when CRX takes the accept.

Pending New and New ([`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix), [`27-exec-new.fix`](examples/27-exec-new.fix)):

```text
8=FIX.4.4|9=352|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261026-09:33:21.078|37=63a7bccb-65ac-82d6-9262-ab701a9894be|11=ORD-000201|693=QR-000201|17=84ba6d7a-c139-8227-a8de-55fc822163ad|150=A|39=A|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=1000000|14=0|6=0|60=20261026-09:33:21.074|120=USD|117=959bbc1a-7496-82e8-af14-38c826bae7c3|10=242|
8=FIX.4.4|9=352|35=8|49=CRX-TRD|56=TKR1|34=6|52=20261026-09:33:21.163|37=63a7bccb-65ac-82d6-9262-ab701a9894be|11=ORD-000201|693=QR-000201|17=2fa513dc-2397-82f3-aa48-05e80c9ceb23|150=0|39=0|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=1000000|14=0|6=0|60=20261026-09:33:21.159|120=USD|117=959bbc1a-7496-82e8-af14-38c826bae7c3|10=200|
```

### 6.3 Fill

Wait for ExecutionReport (8) 150 = F. Book the trade on 150 = F, once for each TrdMatchID (880).

Answer: 8 150 = F, 39 = 2 when the trade is final on Ethereum, or 8 150 = 8 when the trade does not open. The fill carries SecondaryExecID (527), the on-chain trade hash, and CalculatedCcyLastQty (1056), the amount in the second currency of the Symbol.

Fill ([`28-exec-fill.fix`](examples/28-exec-fill.fix)):

```text
8=FIX.4.4|9=527|35=8|49=CRX-TRD|56=TKR1|34=7|52=20261026-09:33:23.466|37=63a7bccb-65ac-82d6-9262-ab701a9894be|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=ORD-000201|693=QR-000201|17=70fda49c-379a-8ff5-b9fc-92f96e6c3ff8|150=F|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.452|120=USD|851=2|117=959bbc1a-7496-82e8-af14-38c826bae7c3|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=187|
```

Until the settlement time, CRX can send 8 150 = H (Trade Cancel). The trade then does not stand. Remove it from the books.

If no ExecutionReport arrives 5 s after the AJ, send OrderStatusRequest (H). Do not send a new AJ for the same quote.

## 7. Maker: first quote

For the maker cases, CRX sends a test RFQ at 100 USD. See [11.6 Maker cases](rules-of-engagement.md#116-maker-cases).

The signature proxy removes the signature data from the QuoteRequest (R) and signs the Quote (S). See [Messages between the signature proxy and CRX](#messages-between-the-signature-proxy-and-crx).

### 7.1 Request

Wait for QuoteRequest (R).

- Side (54) is the taker's side.
- ExpireTime (126) is the quote deadline: TransactTime (60) + 5 s, or + half the RFQ life when that is shorter. CRX can close collection before 126.
- ValidUntilTime (62) is the signature end: the latest time that the trade can open on Ethereum.
- A maker test request carries Text (58) with code `TEST_REQUEST` and sets 126 to the RFQ end.

See [5.8 Timing](rules-of-engagement.md#58-timing).

QuoteRequest to the FIX engine ([`50a-quote-request-to-engine.fix`](examples/50a-quote-request-to-engine.fix)):

```text
8=FIX.4.4|9=261|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:33:16.016|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|62=20261026-09:42:45.000|126=20261026-09:33:20.781|60=20261026-09:33:15.781|10=104|
```

### 7.2 Quote

Before ExpireTime (126), send Quote (S). Copy QuoteReqID (131), Symbol (55), Side (54), OrderQty (38), Currency (15), MaturityDate (541) and MaturityTime (1079) from the R. Copy UpfrontPriceType (1741) and UpfrontPrice (1742) when the R has them. Set ValidUntilTime (62) to 62 of the R. Set a new QuoteID (117), unique for the seat. Send OfferPx (133) when 54 = 1 and BidPx (132) when 54 = 2.

Quote from the FIX engine ([`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix)):

```text
8=FIX.4.4|9=235|35=S|34=2|49=MKR1|52=20261026-09:33:16.044|56=CRX-TRD|15=USD|38=1000000|54=1|55=USD/MXN|62=20261026-09:42:45.000|64=20261127|117=Q-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|10=064|
```

Answer: QuoteStatusReport (AI) 297 = 0. The quote is live and binding until the quote end, with no last look.

Quote accepted ([`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix)):

```text
8=FIX.4.4|9=151|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261026-09:33:16.088|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|117=Q-000101|55=USD/MXN|60=20261026-09:33:16.079|297=0|10=232|
```

### 7.3 Fill

Wait for ExecutionReport (8). To cancel the quote before a taker accepts it, send QuoteCancel (Z). A second Quote (S) on the same R replaces the first; CRX sends AI 297 = 6 for the first QuoteID.

Answer: 8 150 = 0 (New) when a taker accepts the quote, then 8 150 = F when the trade is final. Taker and maker get the same TrdMatchID (880) and SecondaryExecID (527). A quote that does not win gets AI 297 = 7 at the quote end.

Maker fill ([`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix)):

```text
8=FIX.4.4|9=483|35=8|49=CRX-TRD|56=MKR1|34=6|52=20261026-09:33:23.509|37=c44357af-4326-8aed-8b7a-17b97a682a2a|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=Q-000101|17=dfd3631e-f4f4-8776-8258-f5b0c38de807|150=F|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=2|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.489|120=USD|851=1|117=Q-000101|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=115|
```

To decline an RFQ, send QuoteRequestReject (AG) 658 = 10 before ExpireTime (126) ([`59-maker-decline.fix`](examples/59-maker-decline.fix)).

## 8. Common rejects and fixes

Each CRX reject carries Text (58) in the form `<CODE>: <sentence> (trace <id>)`. The code is the first token of 58. Base reject handling in the FIX engine on the code. When the code is unknown, act on the FIX reason field: 373, 380, 658, 300 or 103. Give the trace ID to CRX support.

| Code | Message | Cause | Fix |
|---|---|---|---|
| `LOGON_COMP_ID_UNKNOWN` | Logout (5) | CRX has no record of the SenderCompID, or TargetCompID (56) is wrong for the role. | Use the SenderCompID from onboarding. Use `CRX-TRD`, or `CRX-DC` for drop copy. |
| `LOGON_SIGNATURE_INVALID` | Logout (5) | The Logon signature from the signature proxy is not valid, or it does not match the address that signs. | Check `custody` and the key of the signature proxy. |
| `LOGON_SIGNATURE_MISSING` | Logout (5) | The signature proxy did not sign the Logon. | Read the signature proxy log. |
| `UNAUTHORIZED` | Logout (5) | The address that signs is not on record for the seat, the Logon time is out of range, or CRX took the signature before. | Check `custody` and the host clock. Log on again with a new signature. |
| `SENDING_TIME_ACCURACY` | Logout (5) | SendingTime (52) is more than 120 s from CRX time. | Keep the host clock on NTP. |
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
| `SIGNATURE_MISSING` | AI 297 = 5 or 8 150 = 8 | The S or the AJ reached CRX with no signature and no signature proxy code. | Send the message through the signature proxy. |
| `UNSUPPORTED_MESSAGE` | j 380 = 3 | CRX does not take this MsgType, for example NewOrderSingle (D). | Accept a quote with QuoteResponse (AJ). |
| `RATE_LIMITED` | j 380 = 0. On an AJ: 8 150 = 8, 103 = 99 | The request exceeds a rate limit of the seat. | Wait for the time in Text. |

Unknown Symbol ([`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix)):

```text
8=FIX.4.4|9=204|35=AG|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:39:41.676|131=RFQ-001901|658=1|146=1|55=USD/XXX|58=UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace 1a1779479cb03d3)|10=077|
```

Late accept ([`29-exec-rejected.fix`](examples/29-exec-rejected.fix)):

```text
8=FIX.4.4|9=408|35=8|49=CRX-TRD|56=TKR1|34=9|52=20261026-09:36:32.982|37=NONE|11=ORD-000801|693=QR-000801|17=8a44db94-d3b9-83df-84f0-fdf1e54fec1b|150=8|39=8|103=4|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=0|14=0|6=0|60=20261026-09:36:32.915|120=USD|58=QUOTE_EXPIRED: The quote ended before an accept reached CRX. (trace 1a177919884021d)|117=11116d0c-113b-804e-aafd-07cd8906ab57|10=239|
```

Late maker Quote ([`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix)):

```text
8=FIX.4.4|9=266|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261026-09:34:23.485|131=9acfe992-a282-87aa-842a-bdd79da947c4|117=Q-000501|55=USD/MXN|60=20261026-09:34:23.479|297=5|58=QUOTE_WINDOW_CLOSED: The quote reached CRX after ExpireTime (126) of the request. (trace 1a1778f9edc0119)|300=4|10=097|
```

Accept that the signature proxy did not sign ([`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix)):

```text
8=FIX.4.4|9=410|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261026-09:36:48.454|37=NONE|11=ORD-001001|693=QR-001001|17=388c1ad9-e594-84c9-a94b-f3ccb89da994|150=8|39=8|103=99|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=0|14=0|6=0|60=20261026-09:36:48.411|120=USD|58=TERMS_MISMATCH: The signature proxy did not sign the message. (trace 1a17791d50f023a)|117=11003a68-99ab-84fc-bbc4-fafb643da005|10=100|
```

NewOrderSingle (D) ([`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix)):

```text
8=FIX.4.4|9=151|35=j|49=CRX-TRD|56=TKR1|34=2|52=20261026-09:40:59.581|45=2|372=D|380=3|58=UNSUPPORTED_MESSAGE: CRX does not take this MsgType. (trace 1a17795aa39047a)|10=139|
```

See [9. Rejects and codes](rules-of-engagement.md#9-rejects-and-codes) for every code.

**Next:** run the certification cases on production at 100 USD. See [11. Onboarding and certification](rules-of-engagement.md#11-onboarding-and-certification).

## Messages between the signature proxy and CRX

The FIX engine does not send or read Username (553), RawDataLength (95), RawData (96) or CrxSignature (20007). The signature proxy adds them on the way to CRX, sets ApplicationSystemVersion (1604) on the Logon, and removes 95 and 96 on the way to the FIX engine. It sets a new BodyLength (9) and CheckSum (10) on each message that it changes. All other fields stay as they are. The samples use test keys with no funds. See [5.10 Messages between the signature proxy and CRX](rules-of-engagement.md#510-messages-between-the-signature-proxy-and-crx).

First Logon of the day, signature proxy to CRX ([`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix)):

```text
8=FIX.4.4|9=289|35=A|34=1|49=TKR1|52=20261026-09:33:15.393|56=CRX-TRD|98=0|108=30|141=Y|1603=QuickFIX/J 2.3.3|1605=quickfixj.org|553=0xf683c26739271eeb6501552c68ed37597df8d90b|95=88|96=98Nu4OdZNuPBj2nYfJ10q1GV3s21Olvdu5UqW5hojaBJ9EHqIfxROoBp6BFsZ/UCq6XPk7JwniuvSbPZr4Mt8Bw=|1604=crx-signature-proxy/0.1.0|10=034|
```

- Username (553): the address that signs, the seat or a login key. `0x` and 40 lowercase hex, 42 characters.
- RawDataLength (95) = 88 and RawData (96): the Logon signature, 65 bytes, base64 of 88 characters. It covers the `chain_id` of step 3. See [4.1.1 Logon signature](rules-of-engagement.md#411-logon-signature).
- ApplicationSystemVersion (1604): the name and version of the signature proxy.

Quote (S) to a taker, CRX to the signature proxy ([`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix)):

```text
8=FIX.4.4|9=413|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:33:21.054|131=RFQ-000201|117=959bbc1a-7496-82e8-af14-38c826bae7c3|537=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|133=18.4753|62=20261026-09:35:15.781|60=20261026-09:33:21.048|95=140|96=opnqaSDcEq+6Fgi01vYVUS4RqH8D3qco+BAKbpBcuYmVZHBnJlHZ6xy1DOpTB8Ufx/cFRnziATEAAAAAat8glQAAAaF3jqsJjQuNri/MHi4UFVM+IA0Cy1ccPxvpq4tM6Rfe9CkmJmA=|10=233|
```

- RawDataLength (95) = 140 and RawData (96): the signature data of the S, 104 bytes, base64 of 140 characters. The signature proxy keeps it for the accept. See [5.4 Taker accept signature](rules-of-engagement.md#54-taker-accept-signature).

QuoteResponse (AJ), signature proxy to CRX ([`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix)):

```text
8=FIX.4.4|9=338|35=AJ|34=4|49=TKR1|52=20261026-09:33:21.065|56=CRX-TRD|11=ORD-000201|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:33:21.065|64=20261127|117=959bbc1a-7496-82e8-af14-38c826bae7c3|167=FXNDF|541=20261127|693=QR-000201|694=1|1079=18:00:00Z|20007=qkLfhj7/MD7qVi349vO0LP4zn70FCyXxFP0sad06SNAl+zxxUrXfGVFvDw7x4/WjUS78kNoM6UtlsHdWBb/1ABw=|10=230|
```

- CrxSignature (20007): the EIP-712 `Trade` signature, 65 bytes, base64 of 88 characters.

QuoteRequest (R) to a maker, CRX to the signature proxy ([`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix)):

```text
8=FIX.4.4|9=359|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:33:16.016|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|62=20261026-09:42:45.000|126=20261026-09:33:20.781|60=20261026-09:33:15.781|95=88|96=TTiOCgP1HDhRlYk+T9oTWzT8z426sVdMO86OAu/d5avkCDsmFBqdCwinfMJ31nS52oVJvxMLbFIIVE1wvDc3Rw==|10=242|
```

- RawDataLength (95) = 88 and RawData (96): the signature data of the R, 64 bytes, base64 of 88 characters. The signature proxy keeps it for the quote. See [5.3 Maker quote signature](rules-of-engagement.md#53-maker-quote-signature).

Quote (S) from a maker, signature proxy to CRX ([`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix)):

```text
8=FIX.4.4|9=330|35=S|34=2|49=MKR1|52=20261026-09:33:16.044|56=CRX-TRD|15=USD|38=1000000|54=1|55=USD/MXN|62=20261026-09:42:45.000|64=20261127|117=Q-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|20007=0fTVsTaYLViaVBwNzUclzYxecAfNBRjwSgwKt2Nnz88PRb/E0OjQaU0AFLu+zrHwxZY4RGLRMp5PlNs4HsPdUBw=|10=137|
```

- CrxSignature (20007): the EIP-712 `Quote` signature, 65 bytes, base64 of 88 characters.

Unsigned QuoteResponse (AJ), signature proxy to CRX ([`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix)):

```text
8=FIX.4.4|9=307|35=AJ|34=4|49=TKR1|52=20261026-09:36:47.809|56=CRX-TRD|11=ORD-001001|38=1000000|44=18.4850|54=1|55=USD/MXN|60=20261026-09:36:47.809|64=20261127|117=11003a68-99ab-84fc-bbc4-fafb643da005|167=FXNDF|541=20261127|693=QR-001001|694=1|1079=18:00:00Z|58=TERMS_MISMATCH: The signature proxy did not sign the accept.|10=213|
```

- Text (58): the signature proxy code and one sentence, in place of a Text from the FIX engine. The AJ has no CrxSignature (20007). See [5.6 Unsigned messages](rules-of-engagement.md#56-unsigned-messages).
