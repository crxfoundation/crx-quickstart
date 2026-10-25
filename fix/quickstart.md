# FIX Quickstart

Connect a FIX 4.4 engine to CRX and make a first trade in 8 steps. Each step gives a setting or message, then the result or the CRX answer. The [Rules of Engagement](rules-of-engagement.md) give the full rules.

The samples come from a CRX test run with QuickFIX/J 2.3.3, before tags 20014 to 20017. Sample [`12-logout-daily.fix`](examples/12-logout-daily.fix) shows the format that CRX sends. `|` stands for SOH (0x01). The sample keys are test keys with no funds.

## 1. Requirements

Get these items before the first Logon.

| Item | Requirement |
|---|---|
| Seat | An approved seat: an EOA or an MPC address with one secp256k1 key. A contract wallet cannot sign for a seat. |
| Collateral | Circle USDC on the seat, on Ethereum, deposited through the CRX web app or the REST API. FIX has no deposit message. |
| Trade size | Minimum 100 USD |
| SenderCompID (49) | Provided at onboarding |
| CRX host and port | Provided at onboarding |
| CRX contract address | Provided at onboarding |
| Signature proxy | The program `crx-signature-proxy`. Provided at onboarding. |
| FIX engine | A FIX 4.4 initiator, for example QuickFIX/J |
| Host clock | On NTP. SendingTime (52) must be within 120 seconds of CRX time. |

Send CRX the seat address and, for an allowlist, the source IP addresses.

Result: CRX approves the seat and sends the SenderCompID for each role, the host and port, the CRX contract address and the status page address. See [11.1 Onboarding](rules-of-engagement.md#111-onboarding).

## 2. Dictionary

Download the CRX data dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) and load it in the FIX engine.

```ini
UseDataDictionary=Y
DataDictionary=FIX44-CRX.xml
ValidateUserDefinedFields=N
```

Result: the FIX engine reads the CRX custom tags, 20001 to 20017, and the field order of each message and group. See [8. Custom tags](rules-of-engagement.md#8-custom-tags). `ValidateUserDefinedFields=N` makes the engine accept a CRX custom tag that its dictionary lacks, instead of rejecting the message. See [4.2 Message format](rules-of-engagement.md#42-message-format).

## 3. Signature proxy

Run the signature proxy on the FIX engine host. It signs the Logon, the maker Quote and the taker accept. The key or custodian credential stays on the firm's host.

### 3.1 Path A: local key

Put the seat key, `0x` and 64 hex characters, in a file with mode 0600. Then write `proxy.toml`:

```toml
listen = "127.0.0.1:19877"
upstream = "<host>:<port>"  # Provided at onboarding
upstream_tls = true
custody = "0x<seat address>"

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
- `custody`: the seat address.
- `upstream_tls = true`: CRX rejects a plain TCP connection.

### 3.2 Path B: Fireblocks or Fordefi

Replace the `[backend]` table of path A with one of these tables. Give each credential file mode 0600.

```toml
[backend]
kind = "fireblocks"
api_key_file = "/etc/crx/fireblocks-api-key"
rsa_key_file = "/etc/crx/fireblocks-api-user.pem"
vault_id = "<vault account ID>"
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
ReconnectInterval=5
ResetOnLogon=N
ResendRequestChunkSize=1000
UseDataDictionary=Y
DataDictionary=FIX44-CRX.xml
ValidateUserDefinedFields=N
```

- TargetCompID (56): `CRX-TRD` for trading, `CRX-DC` for drop copy.
- With a custodian back end, set `LogonTimeout` and HeartBtInt (108) to 30 seconds or more.

Answer: at 17:00:00 New York time each day, CRX ends the session with Logout code `DAILY_RESET` ([`12-logout-daily.fix`](examples/12-logout-daily.fix)). Log on again from 17:00:30 with MsgSeqNum (34) = 1; the session times of this step do this. ResetSeqNumFlag (141) = Y is optional.

```text
8=FIX.4.4|9=190|35=5|49=CRX-TRD|56=TKR1|34=52|52=20261020-21:00:00.002|58=DAILY_RESET: The session ends for the daily reset. Log on from 17:00:30 America/New_York. (trace 1a159a8e2c00431)|20009=DAILY_RESET|10=055|
```

## 5. Logon

Start the FIX engine. It sends Logon (A) to the signature proxy ([`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix)).

```text
8=FIX.4.4|9=72|35=A|34=1|49=TKR1|52=20261021-05:25:47.534|56=CRX-TRD|98=0|108=30|141=Y|10=083|
```

Samples 01 to 03 carry ResetSeqNumFlag (141) = Y. With the settings of step 4, the FIX engine sends no 141 on this Logon and the CRX answer has none. CRX accepts the Logon in both forms.

The signature proxy adds Username (553), CrxLoginChain (20017), RawDataLength (95) and RawData (96), then sends the Logon to CRX ([`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix)). CrxLoginChain holds the `chain_id` of step 3, `1`, and the Logon signature covers it. The sample has no 20017; CRX also accepts that form on chain 1.

```text
8=FIX.4.4|9=262|35=A|34=1|49=TKR1|52=20261021-05:25:47.534|56=CRX-TRD|98=0|108=30|141=Y|553=0xd4916d52ff44110267b24151e94cce2b32d176b3|95=132|96=0xeb35008c6d30141663d447f61647c6aa27995c4538ed4f813b1c1b67d292e0553508863b675dea9f0e33d0b5fe83bae999d803d136170ef9865b95d2a55229281c|10=203|
```

Answer: CRX sends Logon (A) ([`03-logon-answer.fix`](examples/03-logon-answer.fix)). Send application messages only after this answer.

```text
8=FIX.4.4|9=72|35=A|49=CRX-TRD|56=TKR1|34=1|52=20261021-05:25:47.592|98=0|108=30|141=Y|10=087|
```

A rejected Logon gets Logout (5) with the code in CrxErrorCode (20009) ([`04-logon-rejected.fix`](examples/04-logon-rejected.fix)). See [9.6 Logout codes](rules-of-engagement.md#96-logout-codes).

```text
8=FIX.4.4|9=155|35=5|49=CRX-TRD|56=TKR1|34=1|52=20261021-05:33:39.403|58=LOGON_BEGIN_STRING: BeginString must be FIX.4.4. (trace 1a15cf36ccb0017)|20009=LOGON_BEGIN_STRING|10=061|
```

## 6. Taker: first trade

### 6.1 Request

Send QuoteRequest (R) ([`20-quote-request.fix`](examples/20-quote-request.fix)). Set CrxMaturityTime (20001), the settlement time, 1 hour to 90 days ahead. Set MaturityDate (541) and SettlDate (64) to the UTC date of 20001; any other date gets QuoteRequestReject (AG), code `MATURITY_MISMATCH`.

```text
8=FIX.4.4|9=212|35=R|34=3|49=TKR1|52=20261021-05:25:47.617|56=CRX-TRD|131=TKR1-R-1792560347616-2|146=1|55=USD/MXN|167=FXNDF|541=20261021|537=1|54=1|38=1000|64=20261021|15=USD|60=20261021-05:25:47.616|20001=20261021-07:25:00.000|10=166|
```

Answer: QuoteStatusReport (AI) 297 = 10 (Pending), immediately ([`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix)).

```text
8=FIX.4.4|9=152|35=AI|49=CRX-TRD|56=TKR1|34=2|52=20261021-05:25:47.610|131=TKR1-R-1792560347616-2|117=TKR1-R-1792560347616-2|55=USD/MXN|60=20261021-05:25:47.606|297=10|10=162|
```

Then CRX sends the best Quote (S), 5 to 20 seconds after the R ([`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix)). The rate is in OfferPx (133) when the taker buys and in BidPx (132) when the taker sells. With no quote, CRX sends QuoteRequestReject (AG) 658 = 8, code `NO_QUOTE`. The S and the fill can also carry CrxSpotTime (20016), the time of the spot observation.

```text
8=FIX.4.4|9=1942|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261021-05:25:52.900|131=TKR1-R-1792560347616-2|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|537=1|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|64=20261021|15=USD|133=18.5|62=20261021-05:27:47.622|60=20261021-05:25:52.895|20001=20261021-07:25:00.000|20002=0|20008=eyJkb21haW4iOnsiY2hhaW5JZCI6MSwibmFtZSI6IkNSWCIsInZlcmlmeWluZ0NvbnRyYWN0IjoiMHgwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMGU3ZTAxIiwidmVyc2lvbiI6InJ1bGVib29rLTEuMCJ9LCJtZXNzYWdlIjp7Im1hdHVyaXR5IjoiMTc5MjU2NzUwMCIsIm5vdGlvbmFsRTYiOiIxMDAwMDAwMDAwIiwib3duTGVnSWQiOiIweDAxNjYzOTMwOWMwMzUwNGNhMGJkODYyYmJkZTFiYTg3ZmExOWJmNTE2YTNiMGVkNzAwMDAwMDAwNmFkODRmMTUiLCJvd25Ob25jZSI6IjE3OTI1NjAzNTI4ODIiLCJvd25TYWx0IjoiMHg0MWI3NTBjNTQ1OWViN2VlZTljOGFkOWVmZTliYTMxNGZmNWRmYTMzYTM5NDg2N2ExOWZiYjQzZTE2Zjg4NGI5IiwicGFpciI6IlVTRC9NWE4iLCJwYWlyQyI6IjB4NWQwNjYzMGY0Y2E2YWQ4YjlhZmEwNTNlYTI3MTE0N2ZhOWY3M2U3MDk1ZDZiNmM4NDhlMTJiNTEzODEyNzc4MiIsInByZW1pdW1CcHMiOiIwIiwicmF0ZUU2IjoiMTg1MDAwMDAiLCJzaWRlIjoiYnV5Iiwic3VtbWFyeSI6ImJ1eSAxIDAwMCBVU0QgdnMgTVhOIGF0IDE4LjUgTVhOIHBlciBVU0QsIG1hdHVyZXMgMjAyNi0xMC0yMVQwNzoyNTowMFosIHVwZnJvbnQgbm9uZSJ9LCJwcmltYXJ5VHlwZSI6IlRyYWRlIiwidHlwZXMiOnsiRUlQNzEyRG9tYWluIjpbeyJuYW1lIjoibmFtZSIsInR5cGUiOiJzdHJpbmcifSx7Im5hbWUiOiJ2ZXJzaW9uIiwidHlwZSI6InN0cmluZyJ9LHsibmFtZSI6ImNoYWluSWQiLCJ0eXBlIjoidWludDI1NiJ9LHsibmFtZSI6InZlcmlmeWluZ0NvbnRyYWN0IiwidHlwZSI6ImFkZHJlc3MifV0sIlRyYWRlIjpbeyJuYW1lIjoic3VtbWFyeSIsInR5cGUiOiJzdHJpbmcifSx7Im5hbWUiOiJwYWlyIiwidHlwZSI6InN0cmluZyJ9LHsibmFtZSI6InNpZGUiLCJ0eXBlIjoic3RyaW5nIn0seyJuYW1lIjoibm90aW9uYWxFNiIsInR5cGUiOiJ1aW50MjU2In0seyJuYW1lIjoicmF0ZUU2IiwidHlwZSI6InVpbnQ2NCJ9LHsibmFtZSI6InByZW1pdW1CcHMiLCJ0eXBlIjoiaW50MTYifSx7Im5hbWUiOiJtYXR1cml0eSIsInR5cGUiOiJ1aW50NDAifSx7Im5hbWUiOiJwYWlyQyIsInR5cGUiOiJieXRlczMyIn0seyJuYW1lIjoib3duTGVnSWQiLCJ0eXBlIjoiYnl0ZXMzMiJ9LHsibmFtZSI6Im93bk5vbmNlIiwidHlwZSI6InVpbnQ2NCJ9LHsibmFtZSI6Im93blNhbHQiLCJ0eXBlIjoiYnl0ZXMzMiJ9XX19|10=051|
```

### 6.2 Accept

Before ValidUntilTime (62) of the S, send QuoteResponse (AJ) with 694 = 1 ([`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix)). Copy QuoteID (117), Symbol (55), Side (54) and OrderQty (38) from the S. Set Price (44) to the quoted rate. Set TransactTime (60), a new QuoteRespID (693) and a new ClOrdID (11).

```text
8=FIX.4.4|9=278|35=AJ|34=4|49=TKR1|52=20261021-05:25:52.921|56=CRX-TRD|11=TKR1-O-1792560352921-4|38=1000|44=18.5|54=1|55=USD/MXN|60=20261021-05:25:52.921|64=20261021|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|167=FXNDF|541=20261021|693=TKR1-QR-1792560352921-3|694=1|10=096|
```

The signature proxy adds CrxSignature (20007).

Answer: ExecutionReport (8) 150 = A (Pending New) within 100 milliseconds ([`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix)), then 150 = 0 (New) when CRX takes the accept ([`27-exec-new.fix`](examples/27-exec-new.fix)).

```text
8=FIX.4.4|9=389|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261021-05:25:52.919|37=NONE|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000001|150=A|39=A|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=1000|14=0|6=0|60=20261021-05:25:52.914|120=USD|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|20001=20261021-07:25:00.000|20002=0|10=074|
8=FIX.4.4|9=389|35=8|49=CRX-TRD|56=TKR1|34=6|52=20261021-05:25:52.971|37=NONE|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000002|150=0|39=0|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=1000|14=0|6=0|60=20261021-05:25:52.967|120=USD|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|20001=20261021-07:25:00.000|20002=0|10=048|
```

### 6.3 Fill

Wait for ExecutionReport (8) 150 = F. Book the trade on 150 = F, once for each TrdMatchID (880).

Answer: 8 150 = F, 39 = 2 when the trade is final on Ethereum ([`28-exec-fill.fix`](examples/28-exec-fill.fix)), or 8 150 = 8 when the trade does not open.

```text
8=FIX.4.4|9=559|35=8|49=CRX-TRD|56=TKR1|34=7|52=20261021-05:25:55.179|37=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000003|150=F|39=2|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261021|60=20261021-05:25:55.169|120=USD|851=2|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|880=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|20001=20261021-07:25:00.000|20002=0|10=007|
```

If no ExecutionReport arrives 5 seconds after the AJ, send OrderStatusRequest (H). Do not send a new AJ for the same quote.

## 7. Maker: first quote

For the maker cases, CRX sends a test RFQ at 100 USD. See [11.6 Maker cases](rules-of-engagement.md#116-maker-cases).

### 7.1 Request

Wait for QuoteRequest (R) ([`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix), an ordinary RFQ). Side (54) is the taker's side. ExpireTime (126) is the quote deadline: normally TransactTime (60) + 5 seconds. A maker test request carries CrxTestRequest (20014) = Y and sets 126 to ValidUntilTime (62), the RFQ end. CRX can close collection before 126. See [5.8 Timing](rules-of-engagement.md#58-timing).

```text
8=FIX.4.4|9=406|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261021-05:25:47.973|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|146=1|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|64=20261021|15=USD|62=20261021-05:27:47.622|126=20261021-05:25:52.622|60=20261021-05:25:47.622|20001=20261021-07:25:00.000|20002=0|20003=0x113d551ab20a5fa350ea92e1e777267ce9fb3d8609da18612fc8e7d561c5a8dd|20004=20261021-05:35:17|10=154|
```

### 7.2 Quote

Before ExpireTime (126), send Quote (S) ([`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix)). Copy QuoteReqID (131), Symbol (55), Side (54), OrderQty (38), Currency (15), CrxMaturityTime (20001) and CrxPremiumBps (20002) from the R. Set a new QuoteID (117), unique per seat. Set ValidUntilTime (62) to CrxQuoteExpiryMax (20004). Send OfferPx (133) when 54 = 1 and BidPx (132) when 54 = 2.

```text
8=FIX.4.4|9=290|35=S|34=2|49=MKR1|52=20261021-05:25:47.998|56=CRX-TRD|15=USD|38=1000|54=1|55=USD/MXN|62=20261021-05:35:17|64=20261021|117=MKR1-Q-1792560347995-1|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|133=18.5|167=FXNDF|537=1|541=20261021|20001=20261021-07:25:00.000|20002=0|10=050|
```

The signature proxy adds CrxLegId (20005), CrxSalt (20006) and CrxSignature (20007) ([`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix)).

```text
8=FIX.4.4|9=575|35=S|34=2|49=MKR1|52=20261021-05:25:47.998|56=CRX-TRD|15=USD|38=1000|54=1|55=USD/MXN|62=20261021-05:35:17|64=20261021|117=MKR1-Q-1792560347995-1|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|133=18.5|167=FXNDF|537=1|541=20261021|20001=20261021-07:25:00.000|20002=0|20005=0x28d6a72865294b3ea639963477370c11ac53adf6f1dea3bf000000006ad84f15|20006=0xa4fdd26c0a73db8432ca601c8319fe00979eda742ce143faa307b5fe17151508|20007=0xdc58e7b339f4f025ff9a9338b20a3802cb343450032412890be6adcbc1bd241127e8af9032f1f43ec087fcda39cc727de766cb7a94a2047399c7f4a41c5a3b3e1c|10=116|
```

Answer: QuoteStatusReport (AI) 297 = 0 ([`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix)). The quote is live and binding, with no last look.

```text
8=FIX.4.4|9=195|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261021-05:25:48.014|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|117=MKR1-Q-1792560347995-1|55=USD/MXN|60=20261021-05:25:48.009|297=0|10=021|
```

### 7.3 Fill

Wait for ExecutionReport (8). To cancel the quote before a taker accepts it, send QuoteCancel (Z).

Answer: 8 150 = 0 (New) when a taker accepts the quote, then 8 150 = F when the trade is final ([`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix)). Taker and maker get the same TrdMatchID (880). A quote that does not win gets AI 297 = 7 at the quote end.

```text
8=FIX.4.4|9=487|35=8|49=CRX-TRD|56=MKR1|34=6|52=20261021-05:25:55.055|37=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|11=MKR1-Q-1792560347995-1|17=X20261021-MKR1-1792560344893000002|150=F|39=2|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=2|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261021|60=20261021-05:25:55.047|120=USD|851=1|117=MKR1-Q-1792560347995-1|880=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|20001=20261021-07:25:00.000|20002=0|10=122|
```

To decline an RFQ, send QuoteRequestReject (AG) 658 = 10 before ExpireTime (126) ([`59-maker-decline.fix`](examples/59-maker-decline.fix)).

## 8. Common rejects and fixes

Each CRX reject carries the code in CrxErrorCode (20009) and Text (58) in the form `<CODE>: <effect>[ <action>] (trace <id>)`. Base reject handling in the FIX engine on 20009. Give the trace ID to CRX support.

| Code (20009) | Message | Cause | Fix |
|---|---|---|---|
| `LOGON_COMP_ID_UNKNOWN` | Logout (5) | CRX has no record of the SenderCompID, or TargetCompID (56) is wrong for the role. | Use the SenderCompID from onboarding. Use `CRX-TRD`, or `CRX-DC` for drop copy. |
| `LOGON_SIGNATURE_INVALID` | Logout (5) | RawData (96) has a bad format, or the signature does not match the address that signs. | Check `custody` and the key of the signature proxy. |
| `SENDING_TIME_ACCURACY` | Logout (5) | SendingTime (52) is more than 120 seconds from CRX time. | Keep the host clock on NTP. |
| `LOGON_SESSION_ACTIVE` | Logout (5) | The SenderCompID has a live session. | Log on after the other session ends. |
| `SEAT_CANNOT_SIGN` | Logout (5) | The seat is a contract wallet. | Use an EOA or MPC seat. |
| `NOT_WHITELISTED` | Logout (5), AG, AI or 8 | CRX did not approve the seat for this action. | Contact CRX support. |
| `NO_QUOTE` | AG 658 = 8 | No maker quoted within the quote window. | Send a new R later, or with other terms. |
| `UNKNOWN_SYMBOL` | AG 658 = 1 | CRX does not list the Symbol. | Use a Symbol from SecurityList (y). |
| `NOTIONAL_BELOW_MINIMUM` | AG 658 = 3 | OrderQty (38) is below 100 USD. | Increase OrderQty. |
| `BAD_REQUEST` | AG 658 = 3 | The settlement time is not 1 hour to 90 days ahead. | Use a time in the range that Text gives. |
| `EXPIRY_OUTSIDE_HOURS` | AG 658 = 3 | The settlement time falls in a market closure, or in the first 15 minutes after a reopen. | Use the earliest time in Text or later. |
| `INSUFFICIENT_COLLATERAL` | AG, AI or 8 | The seat has insufficient free collateral. | Deposit USDC or reduce OrderQty. |
| `QUOTE_EXPIRED` | 8 150 = 8, 103 = 4 | The accept reached CRX after ValidUntilTime (62). | Send a new R. |
| `QUOTE_MISMATCH` | 8 150 = 8 | An accept field differs from the S. | Copy the fields from the S. |
| `QUOTE_WINDOW_CLOSED` | AI 297 = 5, 300 = 4 | The maker Quote reached CRX after ExpireTime (126). | Quote the next RFQ sooner. |
| `QUOTE_TERMS_MISMATCH` | AI 297 = 5, 300 = 99 | A maker Quote field differs from the R, or 62 is earlier than 20004. | Copy the fields from the R. Set 62 to 20004. |
| A CrxSignRefusal (20013) code, for example `TERMS_MISMATCH` | Logout (5), AI 297 = 5 or 8 150 = 8 | The signature proxy did not sign. | Read the signature proxy log. |
| `SIGNATURE_MISSING` | AI 297 = 5 or 8 150 = 8 | The message has no signature and no 20013. | Send the message through the signature proxy. |
| `UNSUPPORTED_MESSAGE` | j 380 = 3 | CRX does not take this MsgType, for example NewOrderSingle (D). | Accept a quote with QuoteResponse (AJ). |
| `RATE_LIMITED` | j 380 = 0. On an AJ: 8 150 = 8, 103 = 99 | The request exceeds a rate limit of the seat. | Wait for the time in Text. |

Unknown Symbol ([`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix)):

```text
8=FIX.4.4|9=237|35=AG|49=CRX-TRD|56=TKR1|34=4|52=20261021-05:31:22.612|131=TKR1-R-1792560682596-2|658=1|146=1|55=USD/XXX|58=UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace 1a15cf156590349)|20009=UNKNOWN_SYMBOL|10=065|
```

Late accept ([`29-exec-rejected.fix`](examples/29-exec-rejected.fix)):

```text
8=FIX.4.4|9=512|35=8|49=CRX-TRD|56=TKR1|34=9|52=20261021-05:28:46.098|37=NONE|11=TKR1-O-1792560526099-4|693=TKR1-QR-1792560526099-3|17=X20261021-TKR1-1792560347546000021|150=8|39=8|103=4|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=0|14=0|6=0|60=20261021-05:28:46.092|120=USD|58=QUOTE_EXPIRED: The accept arrived after the ValidUntilTime of the quote. (trace 1a15ceef30b01e8)|117=0x93fa2894f5a98181c94512d248099e1cf93284194643fcb51ccf4c570d68b65a|20001=20261021-07:26:00.000|20002=0|20009=QUOTE_EXPIRED|10=194|
```

Late maker Quote ([`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix)):

```text
8=FIX.4.4|9=307|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261021-05:26:39.338|131=0x6cdc62e9de360acbf1e35111a3c6d5fa74d5685d72a1b3f65d5e8edf419d608f|117=MKR1-Q-1792560399326-1|55=USD/MXN|60=20261021-05:26:39.332|297=5|58=QUOTE_WINDOW_CLOSED: Too late to quote this request. (trace 1a15ced03d800e4)|300=4|20009=QUOTE_WINDOW_CLOSED|10=195|
```

Accept that the signature proxy did not sign ([`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix)):

```text
8=FIX.4.4|9=546|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261021-05:28:56.254|37=NONE|11=TKR1-O-1792560536260-4|693=TKR1-QR-1792560536260-3|17=X20261021-TKR1-1792560347546000022|150=8|39=8|103=99|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=0|14=0|6=0|60=20261021-05:28:56.248|120=USD|58=TERMS_MISMATCH: The signature proxy did not sign the accept. Send a new QuoteResponse after a new Quote. (trace 1a15cef1ab80203)|117=0xd01b3b6ec15b60edc12272a106f91df8601bc79294d3cf723ab9e946dfd18423|20001=20261021-07:28:00.000|20002=0|20009=TERMS_MISMATCH|10=234|
```

NewOrderSingle (D) ([`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix)):

```text
8=FIX.4.4|9=185|35=j|49=CRX-TRD|56=TKR1|34=2|52=20261021-05:32:36.834|45=2|372=D|380=3|58=UNSUPPORTED_MESSAGE: Accept a quote with QuoteResponse (AJ). (trace 1a15cf2786203fb)|20009=UNSUPPORTED_MESSAGE|10=125|
```

See [9. Rejects and codes](rules-of-engagement.md#9-rejects-and-codes) for every code.

**Next:** run the certification cases on production at 100 USD. See [11. Onboarding and certification](rules-of-engagement.md#11-onboarding-and-certification).
