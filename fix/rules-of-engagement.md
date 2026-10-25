# CRX FIX 4.4 Rules of Engagement

Connect a FIX 4.4 engine to CRX to trade FX non-deliverable forwards that settle in Circle USDC.

Requirements:

1. A seat address that CRX approved. See [Onboarding](#111-onboarding).
2. The CRX dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) in the FIX engine. See [Dictionary](#13-dictionary).
3. The signature proxy on the firm's host. See [Signature proxy](#5-signature-proxy).
4. A local key, or a Fireblocks or Fordefi vault, that signs for the seat. See [Key back ends](#55-key-back-ends).
5. Circle USDC collateral on the seat. See [Trading rules](#10-trading-rules).

## Contents

1. [Document control](#1-document-control)
2. [Scope](#2-scope)
3. [Connectivity](#3-connectivity)
4. [Session](#4-session)
5. [Signature proxy](#5-signature-proxy)
6. [Message flows](#6-message-flows)
7. [Messages](#7-messages)
8. [Custom tags](#8-custom-tags)
9. [Rejects and codes](#9-rejects-and-codes)
10. [Trading rules](#10-trading-rules)
11. [Onboarding and certification](#11-onboarding-and-certification)
12. [Raw examples](#12-raw-examples)
13. [Dictionary](#13-dictionary)

## 1. Document control

| Version | Issue date | Sections | Change |
|---|---|---|---|
| 1.0 | 2026-10-20 | All | First issue. |
| 1.1 | 2026-10-24 | 2–12 | Quote withdrawals, optional test-request fields and current account checks. Version 1.0 sessions still connect, with no end date. Load the 1.1 dictionary or set `ValidateUserDefinedFields=N`: an engine that checks custom tags against the 1.0 dictionary rejects the Quote (S) and the fill to the taker, and a maker test request (R). |

Change rules:

- Each change adds a dated row to this table.
- CRX gives 3 months' notice of a breaking change: a change that makes a compliant engine fail, such as a removed message, tag or value, or a new required tag.
- Each row states if the previous version still connects, and until which date.
- A new optional tag, value or reject code is not a breaking change. Accept it. See [Unknown tags and values](#42-message-format).

## 2. Scope

### 2.1 Service

- FIX 4.4 request for quote (RFQ) for FX non-deliverable forwards (NDFs).
- Markets: USD/MXN, USD/BRL and USD/PHP. SecurityList (y) gives the live list.
- CRX settles each trade in cash, in Circle USDC on Ethereum (chain 1), at its settlement time.
- The same rules, limits and collateral checks apply on FIX, REST and WebSocket.
- An RFQ sent on FIX shows on REST and WebSocket with `client_rfq_id` = QuoteReqID (131).
- CRX holds no firm key and no custodian credential.

### 2.2 Session roles

Each SenderCompID has one role.

| Role | TargetCompID (56) | Firm sends | CRX sends |
|---|---|---|---|
| Trading | `CRX-TRD` | R, AJ (taker). S, Z, AG (maker). x, a, H. | AI, S, AG, 8, R, y, j |
| Drop copy | `CRX-DC` | Session messages only | ExecutionReport (8) fills for every trade of the seat, from FIX, REST or WebSocket |

A trading session carries the taker flow, the maker flow or both, as the seat's CRX roles set. A seat with the maker role receives QuoteRequest (R).

### 2.3 Not on FIX

- Deposits and withdrawals: use the CRX web app or the REST API.
- Market data and streaming prices.
- Early close of a trade, including mutual close: use the REST API.
- Account viewers, collateral events and settlement reports: use the REST or WebSocket API.
- Creation of test requests: use `POST /test-requests`. The maker answers the QuoteRequest (R) of a test request on FIX.

### 2.4 Terms

| Term | Meaning |
|---|---|
| Seat | Ethereum address that holds the firm's collateral and signs its quotes and trades. One seat per firm. |
| Login key | Optional address on record with CRX that signs the Logon for a seat. It cannot sign quotes or trades. |
| Taker | Firm that requests and accepts a quote. |
| Maker | Firm that sends a quote. |
| Settlement time | Time in CrxMaturityTime (20001). The fixing uses the price at this time, and the trade settles on the same date. |
| Signature | 65-byte secp256k1 ECDSA signature: `0x` and 130 lowercase hex characters (r, s, v with v 27 or 28). |
| Quote end | The earlier of the RFQ end (62 of the maker R) and CrxQuoteExpiryMax (20004). A signed quote binds until this time. |
| Signature proxy | Program `crx-signature-proxy` that the firm runs beside its FIX engine to add the signatures. |
| Trace ID | ID at the end of each Text (58). Give it to CRX support. |

## 3. Connectivity

### 3.1 Network path

```text
Firm host                                                  CRX
+------------+   FIX 4.4, TCP    +-----------------+   FIX 4.4 over TLS   +-----+
| FIX engine | <---------------> | signature proxy | <------------------> | CRX |
+------------+    127.0.0.1      +-----------------+      internet        +-----+
```

- Connect the FIX engine to the signature proxy on the same host, on 127.0.0.1.
- The signature proxy connects to CRX over TLS 1.2 or TLS 1.3. CRX rejects a plain TCP connection.
- The signature proxy connects to CRX only when the Logon signature is ready.
- Onboarding gives the CRX host name and port. Connect by host name and resolve it before each connection.
- The signature proxy checks the CRX server certificate. CRX does not ask for a client certificate.
- Each SenderCompID can have a source IP allowlist. A Logon from another address gets Logout with code `LOGON_IP_NOT_ALLOWED`.

### 3.2 CompIDs

| Field | Value |
|---|---|
| SenderCompID (49) | Given at onboarding. 1 to 64 characters: `A-Z`, `a-z`, `0-9`, period, underscore and hyphen, not starting with a period. |
| TargetCompID (56) | `CRX-TRD` for a trading session. `CRX-DC` for a drop-copy session. |

- Each SenderCompID maps to one seat and one role.
- Each SenderCompID has one live session. A second Logon gets Logout with code `LOGON_SESSION_ACTIVE`, and the first session continues.

### 3.3 Reconnect

1. Wait 5 seconds before the first reconnect.
2. Double the wait after each failed attempt, up to 60 seconds.
3. Keep the sequence numbers: send ResetSeqNumFlag (141) = N, except after the daily reset.
4. After a Logout that rejects a Logon, correct the cause before the next attempt.

### 3.4 Engine settings

QuickFIX and QuickFIX/J settings for a trading session. The FIX engine connects to the signature proxy. Onboarding gives the SenderCompID.

```ini
[SESSION]
ConnectionType=initiator
BeginString=FIX.4.4
SenderCompID=<given at onboarding>
TargetCompID=CRX-TRD
SocketConnectHost=127.0.0.1
SocketConnectPort=<listen port of the signature proxy>
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

## 4. Session

### 4.1 Logon

1. The FIX engine sends Logon (A) with HeartBtInt (108).
2. The signature proxy adds Username (553), RawDataLength (95), RawData (96) and CrxLoginChain (20017), the chain ID of its configured domain. It adds CrxLoginKey (20012) when a login key signs.
3. CRX checks the session fields, then the signature.
4. CRX answers with Logon (A). Send application messages only after this answer.
5. When CRX rejects the Logon, it sends Logout (5) with Text (58) and CrxErrorCode (20009), then closes the connection.

Connection rules:

- Send the Logon within 10 seconds of opening the TCP connection to the signature proxy, or the signature proxy closes the connection without a message.
- CRX applies the same 10-second limit to the connection from the signature proxy, TLS handshake included.
- The Logon must be the first message, or CRX closes the connection without a message.
- Do not send Password (554). CRX does not use it.
- With a custodian back end, set HeartBtInt and the FIX engine's LogonTimeout to 30 seconds or more.

#### 4.1.1 Logon signature

RawData (96) holds an EIP-191 `personal_sign` signature of the 9 lines below, joined with `\n` (0x0A), with no newline at the end.

```text
CRX-REST-LOGIN
Audience: crx-gateway
Chain: <CrxLoginChain (20017), decimal>
Method: POST
Path: /session
Custody: 0x<seat address, 40 lowercase hex>
Signer: 0x<address that signs, 40 lowercase hex>
Timestamp: <SendingTime (52) of this Logon, Unix milliseconds>
Body: 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
```

- The 9 lines are the CRX REST login message for `POST /session`. The `Body` line is the Keccak-256 hash of an empty body.
- Line 7 holds the seat address, or the login key address from CrxLoginKey (20012).
- CRX rebuilds the message from 553, 20012, 20017 and 52 and recovers the address from the signature. The address must be the seat or a login key on record for the seat.
- The timestamp must be at most 120 seconds behind and at most 5 seconds ahead of CRX time.
- CRX accepts each signature once. The signature proxy signs each Logon.
- The Logon opens an API session for the seat that lasts up to 8 hours. See [Schedule](#48-schedule) for renewal.

Legacy test vector, without 20017 and without the Chain line. Chain 1 accepts this form. Key: the public Anvil and Hardhat test account 0, which holds no funds.

| Item | Value |
|---|---|
| Seat address | `0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266` |
| SendingTime (52) | `20261020-14:30:00.000` |
| Timestamp line | `1792506600000` |
| RawData (96) | `0xd3aa9ef32ddc55ed64d26e2172e0ee5dee5bd3dfd77c36ff0a17f4c08d1c21e64d355c4bbd92051c5fc2b2857444d387bbf734a76c53de985557d6c87cc0899c1b` |

### 4.2 Message format

- BeginString (8) is `FIX.4.4` on each message.
- Times are UTC, `YYYYMMDD-HH:MM:SS.sss`. CRX sends milliseconds. It reads 0 to 9 decimal places and uses the first 3.
- SendingTime (52) must be within 120 seconds of CRX time. Keep the host clock on NTP.
- Decimals are plain text: digits and one `.` only.
- OrderQty (38), BidPx (132), OfferPx (133) and Price (44) have at most 6 decimal places.
- Keep each message below 8,192 bytes. A longer message gets Logout with code `MESSAGE_TOO_LARGE`.
- CRX drops a message with a bad BodyLength (9) or CheckSum (10) without an answer. Its MsgSeqNum stays open, so the next message shows a gap and CRX sends ResendRequest.
- A tag without a value gets Reject (3) with 373 = 4, and a repeating group out of order gets Reject (3) with 373 = 15. The rejected message uses its MsgSeqNum.

Unknown tags and values:

- CRX ignores a tag that this document does not list for the message.
- Accept an unknown tag, value or reject code from CRX without ending the session.
- In QuickFIX and QuickFIX/J, `ValidateUserDefinedFields=N` accepts a custom tag that is not in the dictionary.
- When the code in 20009 is unknown, act on the FIX reason field: 373, 380, 658, 300 or 103.

### 4.3 Heartbeat and TestRequest

- HeartBtInt (108) is 5 to 60 seconds. Use 30. CRX returns the same value in its Logon answer.
- A HeartBtInt outside 5 to 60 gets Logout with code `LOGON_HEART_BT_INT`.
- CRX sends Heartbeat (0) when it sends nothing else for HeartBtInt seconds.
- CRX sends TestRequest (1) when it receives nothing for 1.2 × HeartBtInt.
- CRX sends Logout with code `HEARTBEAT_TIMEOUT` when it then receives nothing for another 1.2 × HeartBtInt.
- Answer each TestRequest with a Heartbeat that holds the same TestReqID (112). CRX does the same.

### 4.4 Sequence numbers

| Case | CRX action |
|---|---|
| MsgSeqNum is the expected number | CRX processes the message. |
| MsgSeqNum is higher than expected | CRX holds the message and sends one ResendRequest (2): BeginSeqNo (7) = expected number, EndSeqNo (16) = 0. It processes the held messages in order when the gap closes. |
| More than 10,000 messages held | Logout with code `GAP_QUEUE_FULL`. |
| MsgSeqNum is lower than expected, PossDupFlag (43) = Y | CRX ignores the message. |
| MsgSeqNum is lower than expected, no PossDupFlag | Logout with code `SEQ_NUM_TOO_LOW`. Text gives the expected and the received numbers. |
| Logon MsgSeqNum is lower than expected | Logout with code `SEQ_NUM_TOO_LOW`. |
| Logon MsgSeqNum is higher than expected | Logon answer, then ResendRequest. |

- Sequence numbers continue across reconnects within a session day and restart at 1 after the daily reset. See [Schedule](#48-schedule).
- CRX ignores NextExpectedMsgSeqNum (789).
- A Logon with ResetSeqNumFlag (141) = Y starts both sides at 1 and must have MsgSeqNum 1. CRX answers with 141 = Y.
- A Logon with 141 = Y deletes the messages that CRX keeps for resend. Then get the state with QuoteStatusRequest (a) and OrderStatusRequest (H).

### 4.5 Resend

When the firm sends ResendRequest (2):

- CRX resends the stored application messages with PossDupFlag (43) = Y and OrigSendingTime (122) = the first SendingTime. MsgSeqNum and body are unchanged.
- CRX replaces session messages and expired content with SequenceReset-GapFill: GapFillFlag (123) = Y, NewSeqNo (36) = the next number to send.
- EndSeqNo (16) = 0 asks for all messages up to the last one sent.
- BeginSeqNo 0, or an EndSeqNo below BeginSeqNo, gets Reject (3) with 373 = 5.
- CRX answers the full range of a ResendRequest in runs of 1,000 messages, from BeginSeqNo.
- Keep one ResendRequest open at a time.
- CRX keeps every message it sent since the last daily reset.

| Message from CRX | On resend |
|---|---|
| ExecutionReport (8), QuoteStatusReport (AI), QuoteRequestReject (AG), BusinessMessageReject (j), SecurityList (y) | Sent again |
| Quote (S) to a taker | Sent again before ValidUntilTime (62). Gap-filled after it. |
| QuoteRequest (R) to a maker | Sent again before ExpireTime (126). Gap-filled after it. |
| Session messages | Gap-filled |

Repeats:

- A repeated request gets the stored answer. See [IDs and repeats](#410-ids-and-repeats).
- CRX sends a stored answer under a new MsgSeqNum, with PossResend (97) = Y and its original ExecID (17).
- Use ExecID (17) to discard a second copy of an ExecutionReport.

### 4.6 SequenceReset

- GapFill mode, GapFillFlag (123) = Y: NewSeqNo (36) must be higher than MsgSeqNum, or the message gets Reject (3) with 373 = 5.
- Reset mode, 123 = N or absent: CRX moves its expected number up to NewSeqNo. An equal value has no effect. A lower value gets Reject (3) with 373 = 5.
- Use Reset mode only when CRX support asks.

### 4.7 Logout

- Either side can start a Logout. Answer a Logout with a Logout.
- CRX answers a firm Logout with Logout code `LOGOUT_ACK`. A firm Logout with a bad SendingTime (52) gets Reject (3), then the Logout answer.
- CRX waits 10 seconds for the answer to its Logout, then closes the connection.
- After a session end or a refused Logon, CRX closes the connection within 1 second, even when the peer reads nothing. The CompID can then log on again.
- Each CRX Logout has Text (58) and CrxErrorCode (20009). See [Logout codes](#96-logout-codes). Put the reason in Text on a firm Logout too.
- More than 50 rejects in 60 seconds end the session with Logout code `ERROR_RATE`.
- The count includes each Reject (3) and each j that answers a request, except a j with code `SERVICE_UNAVAILABLE`.
- A Logout cancels nothing. See [Disconnect and recovery](#49-disconnect-and-recovery).

### 4.8 Schedule

New York uses daylight time (UTC−4) from the second Sunday of March to the first Sunday of November, and standard time (UTC−5) for the rest of the year.

| Item | New York time | UTC, daylight time | UTC, standard time |
|---|---|---|---|
| Daily reset: CRX sends Logout `DAILY_RESET` | 17:00:00 each day | 21:00:00 | 22:00:00 |
| First Logon after the reset | 17:00:30 | 21:00:30 | 22:00:30 |
| USD/MXN and USD/PHP open | Sunday 18:00 to Friday 17:00 | Sunday 22:00 to Friday 21:00 | Sunday 23:00 to Friday 22:00 |
| USD/MXN and USD/PHP daily break, Monday to Thursday | 17:00 to 18:00 | 21:00 to 22:00 | 22:00 to 23:00 |
| USD/BRL open, Monday to Friday | 08:00 to 17:00 | 12:00 to 21:00 | 13:00 to 22:00 |
| Holidays | USD/MXN and USD/PHP close at 17:00 on 24 and 31 December. USD/BRL does not open on 25 December and 1 January. | | |

Daily reset:

1. At 17:00:00 New York time, CRX sends Logout with code `DAILY_RESET`.
2. CRX deletes the messages it keeps for resend.
3. From 17:00:30, log on with MsgSeqNum (34) = 1. ResetSeqNumFlag (141) = Y is optional.

Session renewal:

- CRX ends each session with Logout code `SESSION_RENEWAL` 10 minutes before the seat's API session ends, at most 7 hours 50 minutes after the Logon.
- CRX sends this Logout only when no accept waits for its answer.
- Log on again after 5 seconds. Sequence numbers continue.

Other rules:

- The FIX service accepts a Logon at any time except during the 30 seconds of the daily reset.
- Outside market hours, CRX can reject a request, or no maker quotes it.
- The CRX status page, given at onboarding, shows the state of the FIX service.
- Set the session times as in [Engine settings](#34-engine-settings).

### 4.9 Disconnect and recovery

- A disconnect or a Logout cancels nothing.
- CRX closes a session without a Logout when its socket accepts no data for HeartBtInt, at most 10 seconds. The reports stay queued for the next Logon, and the CompID can log on again immediately.
- A signed quote stays binding until the quote end, a QuoteCancel (Z) or a fill. See [Terms](#24-terms).
- An RFQ stays open until ValidUntilTime (62) of the maker R.
- An accept that reached CRX stays valid.
- A QuoteCancel (Z) or a decline (AG) that a CRX stop interrupts runs again at the next Logon.
- CRX keeps the reports for a firm that is not logged on and sends them after its next Logon, before any new message.
- Each session of the seat gets its own reports at its own next Logon. An R that opened while the session was down goes out at that Logon, before its ExpireTime (126). A CRX restart drops it.
- An answer to a request, including to H, a or a repeat, never overtakes a report that CRX queued before it.
- CRX sends a session Reject (3) immediately, even while these reports go out.
- Such an answer carries TargetSubID (57) from the request. Its first send has no PossResend (97).
- A report on its first send has no PossResend (97), including a report made while the session was down, closing or sending these reports.
- A report held over a CRX restart carries PossResend (97) = Y.
- CRX keeps trade reports over a crash, but not a queued answer to H or a. Send that request again after the next Logon.
- A message whose send the session end cut goes out again with PossResend (97) = Y.
- An answer that CRX makes after its own Logout waits for the next Logon.

After a reconnect:

1. Log on with the next sequence number and ResetSeqNumFlag (141) = N.
2. Let the FIX engine fill each gap with ResendRequest.
3. Maker: for each quote without a final report, send OrderStatusRequest (H) with ClOrdID (11) = the QuoteID. OrdStatus (39) in the answer gives the state. See [OrderStatusRequest](#712-orderstatusrequest-h-firm-to-crx).
4. Taker: send OrderStatusRequest (H) for each ClOrdID without a final report.

### 4.10 IDs and repeats

| ID | Set by | Rule |
|---|---|---|
| QuoteReqID (131) on a taker R | Firm | 1 to 128 printable ASCII characters, unique per seat. |
| QuoteID (117) on a maker S | Firm | 1 to 128 printable ASCII characters, unique per seat. |
| QuoteRespID (693) and ClOrdID (11) on AJ | Firm | 1 to 128 printable ASCII characters, unique per seat. |
| QuoteReqID (131) on a maker R | CRX | The CRX RFQ ID, `0x` and 64 hex characters. A maker never sees the taker's QuoteReqID. |
| QuoteID (117) on a taker S | CRX | The CRX quote ID, `0x` and 64 hex characters. |
| OrderID (37) and TrdMatchID (880) | CRX | The trade ID, `0x` and 64 hex characters. |
| ExecID (17) | CRX | `X<YYYYMMDD>-<SenderCompID of the session>-<n>`. Unique per ExecutionReport across all sessions and days. `<n>` rises but does not count from 1. |

- Firm IDs are unique per seat and shared by all sessions of the seat.
- An ID stays taken until 24 hours after its order or quote ends. The daily reset does not free it.
- A maker QuoteID is single-use for the seat. While CRX holds the QuoteID, a Quote with other terms gets j 380 = 0, code `DUPLICATE`. After that, a reuse gets AI 297 = 5, code `NONCE_COLLISION`.
- An ID sent again with the same content is a repeat: CRX sends the stored answer and opens no new RFQ, quote or trade.
- An ID sent again with other content gets a BusinessMessageReject (j) with code `DUPLICATE`. The first request and its state do not change.

## 5. Signature proxy

### 5.1 Function

- CRX supplies `crx-signature-proxy`. The firm runs it on its own host, beside its FIX engine.
- The signature proxy changes no FIX message, except these three:
  - Logon (A).
  - Quote (S) from a maker.
  - QuoteResponse (AJ) with QuoteRespType (694) = 1.
- It adds signature tags to these three and sets a new BodyLength (9) and CheckSum (10) on each.
- It keeps the MsgSeqNum and sends no message of its own. The FIX session runs end to end between the FIX engine and CRX.
- The key or the custodian credential stays on the firm's host.
- The signature proxy reads one TOML file that gives:
  - the listen address for the FIX engine. It must be a loopback address, except when `allow_remote_listen = true`.
  - `state_file`: the file that keeps the signed IDs over a restart, so the signature proxy never signs one ID with other terms.
  - the CRX host and port, and an optional CA certificate
  - the seat address and an optional login key address
  - the signature domain
  - the back end and its credential files

### 5.2 Tags the signature proxy adds

| Message | Tags added | Content |
|---|---|---|
| Logon (A) | 553 when absent, 20012 when a login key signs, 95, 96 | Signature of the login message. See [Logon signature](#411-logon-signature). |
| Quote (S) from a maker | 20005, 20006, 20007 | Leg ID, salt and the EIP-712 `Quote` signature |
| QuoteResponse (AJ), 694 = 1 | 20007 | The EIP-712 `Trade` signature |

Domain of both EIP-712 signatures:

| Field | Value |
|---|---|
| name | `CRX` |
| version | `rulebook-1.0` |
| chainId | `1` |
| verifyingContract | The CRX contract address. Onboarding gives it. |

### 5.3 Maker quote signature

The signature proxy keeps each QuoteRequest (R) that it passes, by QuoteReqID. It signs the amount, currency, side, maturity, premium and rate from the FIX engine's Quote (S), each checked against the R.

A message from CRX sets no signed value. The R gives only CrxTakerRef (20003), CrxQuoteExpiryMax (20004) and the values for the checks.

The signature proxy signs the S only when all these conditions are true:

1. It passed an R with the QuoteReqID (131) of the S.
2. Symbol (55), Side (54), OrderQty (38), Currency (15), CrxMaturityTime (20001) and CrxPremiumBps (20002) are equal to the R.
3. Currency (15) is the base currency of Symbol (55), for example `USD` for `USD/MXN`.
4. QuoteType (537) is absent or `1`.
5. ValidUntilTime (62) is not earlier than CrxQuoteExpiryMax (20004) of the R.
6. The S has one rate, on the side that the R asks for.

Otherwise it sends the S unsigned with CrxSignRefusal (20013). See [Unsigned messages](#56-unsigned-messages).

For each S that it signs, it sets:

- CrxLegId (20005): 24 random bytes, then CrxQuoteExpiryMax (20004) as an 8-byte big-endian Unix time in seconds.
- CrxSalt (20006): 32 random bytes.
- CrxSignature (20007): the signature of the typed data below.

Type:

```text
Quote(address seat,bytes32 legId,bytes32 pair,int8 side,uint256 notional,uint64 rate,int16 premiumBps,uint40 expiry,uint64 nonce,bytes32 salt,bytes32 takerRef)
```

| Field | Value |
|---|---|
| seat | The seat address |
| legId | CrxLegId (20005) |
| pair | Keccak-256 of the Symbol (55) text of the S, for example `USD/MXN` |
| side | The maker's side, the opposite of the S Side (54): −1 when 54 = 1, +1 when 54 = 2 |
| notional | OrderQty (38) of the S × 10^6, in the currency of Currency (15) |
| rate | OfferPx (133) or BidPx (132) of the S × 10^6 |
| premiumBps | CrxPremiumBps (20002) of the S |
| expiry | CrxMaturityTime (20001) of the S in Unix seconds |
| nonce | Bytes 16 to 23 of legId as a big-endian uint64 |
| salt | CrxSalt (20006) |
| takerRef | CrxTakerRef (20003) of the R |

The signed quote is binding. When a taker accepts it, the trade opens with no further step from the maker.

### 5.4 Taker accept signature

For a QuoteResponse (AJ) with 694 = 1, the signature proxy finds the Quote (S) by QuoteID (117) and decodes its CrxTypedData (20008). It signs only when all these conditions are true:

1. The domain is equal to the configured domain.
2. primaryType is `Trade`.
3. pair is the Symbol (55). side is the AJ Side (54): `buy` for 1, `sell` for 2.
4. notionalE6 is OrderQty (38) × 10^6.
5. rateE6 is Price (44) × 10^6, and Price is the quoted rate.
6. premiumBps and maturity are equal to the Quote.
7. The S names a QuoteRequest (R) that the FIX engine sent. Its Symbol, Side, OrderQty, 20001 and 20002 are equal to the R.
8. Currency (15), when present on the R, the S or the AJ, is the base currency of Symbol (55).

Type:

```text
Trade(string summary,string pair,string side,uint256 notionalE6,uint64 rateE6,int16 premiumBps,uint40 maturity,bytes32 pairC,bytes32 ownLegId,uint64 ownNonce,bytes32 ownSalt)
```

The `summary` field is one line of text that a custodian shows to an approver:

```text
buy 100 000 USD vs MXN at 18.452 MXN per USD, matures 2026-10-21T18:00:00Z, upfront none
```

### 5.5 Key back ends

| Back end | Signing | Firm supplies |
|---|---|---|
| Local key | A secp256k1 key in hex, in a file with mode 0600. The signature proxy never reads the key from the command line or the environment, and never writes it to a log. | The key file |
| Fireblocks | `TYPED_MESSAGE` with type `EIP712` for Quote and Trade. `ETH_MESSAGE` for the Logon. The signature proxy reads the transaction until its status is `COMPLETED`. | API key file, API user RSA private key file, vault account ID |
| Fordefi | `evm_message` with `typed_message_type` for Quote and Trade. `personal_message_type` for the Logon. The signature proxy uses `create-and-wait`. | API user token file, API user P-256 private key file, vault ID |

- Each back end recovers the address from the signature and sends the signature only when the address is the seat, or the login key for a Logon.
- The custodian vault must allow EIP-191 and EIP-712 signing.
- Set a custodian policy that signs with no approval by a person, for these messages only:
  - EIP-712 messages with domain name `CRX`, chainId 1, the CRX contract address, and primaryType `Quote` or `Trade`.
  - EIP-191 messages that start with `CRX-REST-LOGIN`.
- Fireblocks: use a `TYPED_MESSAGE` policy rule and an approval callback that approves only transactions from the signature proxy.
- Fordefi: use a message policy on the domain and the primary type, with programmatic signing.
- A policy that waits for a person cannot meet the 5-second maker window.

### 5.6 Unsigned messages

When the signature proxy does not sign a Logon, a Quote or an accept, it sends the message unsigned with the reason in CrxSignRefusal (20013), and writes the details to its log.

CRX rejects the unsigned message with no further action, before it checks the terms. The reject carries the 20013 code in CrxErrorCode (20009).

| Unsigned message | CRX answer |
|---|---|
| Logon (A) | Logout (5) |
| Quote (S) | QuoteStatusReport (AI) 297 = 5, 300 = 99 |
| QuoteResponse (AJ), 694 = 1 | ExecutionReport (8) 150 = 8, 103 = 99 |

| CrxSignRefusal (20013) | Cause |
|---|---|
| `INVALID_FIELD` | A required field is absent or has a bad format, or the maker Quote has a QuoteType (537) other than `1`. |
| `UNKNOWN_QUOTE_REQUEST` | The signature proxy did not pass a QuoteRequest with this QuoteReqID in the last 15 minutes. |
| `UNKNOWN_QUOTE` | The signature proxy did not pass a Quote with this QuoteID in the last 15 minutes. |
| `TERMS_MISMATCH` | A field differs from the R or the S, Currency (15) is not the base currency of Symbol (55), or Username is not the seat. For an accept, the S differs from the firm's own QuoteRequest (R). A second copy of an R or S with other terms, also under a MsgSeqNum that the signature proxy already passed, stops all signatures on its ID. |
| `REPEATED_TAG` | The R or the S repeats a tag that the signature reads. |
| `WRONG_SIDE` | The maker Quote prices the side that the QuoteRequest does not ask for. |
| `SENDING_TIME_OUT_OF_RANGE` | The Logon SendingTime (52) is more than 5 seconds ahead of the clock or more than 120 seconds behind it. |
| `TYPED_DATA_MISMATCH` | CrxTypedData (20008) does not decode, or it differs from the domain, the S or the AJ. |
| `ID_REUSED` | The signature proxy saw this ID before with other terms. |
| `SIGN_TIMEOUT` | No signature before the deadline. |
| `SIGNATURE_NOT_SEAT` | The signature does not match the seat. |
| `SIGN_FAILED` | The back end gave no signature. |
| `CACHE_FULL` | The signature proxy holds its maximum number of live IDs. It signs no message on a new ID until an ID reaches its end time. |
| `INBOUND_UNREAD` | The signature proxy could not read a message from CRX, and signs nothing until the next Logon. |
| `QUOTE_LIFE_TOO_LONG` | CrxQuoteExpiryMax (20004) of the R is later than ValidUntilTime (62) of the maker Quote. |

A Quote or an accept with no signature and no 20013 gets code `SIGNATURE_MISSING`.

### 5.7 Seat address

- Use an EOA or an MPC address with one secp256k1 key.
- A contract wallet, for example a Safe or an ERC-4337 account, cannot sign for a seat. CRX rejects it at Logon with code `SEAT_CANNOT_SIGN`.

### 5.8 Timing

| Step | Deadline | Late result |
|---|---|---|
| Maker Quote (S) | ExpireTime (126) of the R: normally TransactTime (60) + 5 seconds. A shorter RFQ reserves half its life for acceptance. A test request uses the RFQ end. | AI 297 = 5, 300 = 4, code `QUOTE_WINDOW_CLOSED` |
| Taker accept, AJ 694 = 1 | ValidUntilTime (62) of the S | 8 150 = 8, 103 = 4, code `QUOTE_EXPIRED` |

- The FIX deadline is conservative when CRX uses a longer collection window. It uses the configured normal window, because the current API does not publish the actual collection deadline. Test requests use their RFQ end. CRX can close a request sooner.
- The R reaches the maker up to 1 second after TransactTime (60), plus network time. This delay counts against the 5-second window.
- The signature proxy writes the sign time of each message to its log.
- The signature proxy sends a maker quote even when it signs it more than 4.5 seconds after TransactTime. After ExpireTime (126), CRX rejects the quote with code `QUOTE_WINDOW_CLOSED`.

Choose the back end from measured sign times:

| Back end | Taker | Maker |
|---|---|---|
| Local key | Fits | Fits |
| Custodian | Fits | Fits when the 99th percentile time from R TransactTime (60) to S sent is below 4.5 seconds |

Measure the 50th and 99th percentile sign times for each back end during certification. CRX gives each maker only its own figures.

### 5.9 Resend and logs

- On a resend (43 = Y), the signature proxy adds the same tags as on the first copy and never signs a message twice.
- The signature proxy writes JSON lines to standard error. Keep these logs for certification.

## 6. Message flows

### 6.1 Steps

Taker:

1. Request: send QuoteRequest (R). CRX answers immediately with QuoteStatusReport (AI) 297 = 10 (Pending).
2. Quote: CRX normally collects maker quotes for 5 seconds; collection can close sooner or use a longer window. CRX then sends the best Quote (S) or QuoteRequestReject (AG), 5 to 20 seconds after the R.
3. Accept or pass: before ValidUntilTime (62), send QuoteResponse (AJ) with 694 = 1 to accept or 694 = 6 to pass.
4. Confirm: CRX sends ExecutionReport (8) 150 = A (Pending New) within 100 milliseconds of the accept, then 150 = 0 (New) when it takes the accept.
5. Fill: CRX sends 8 150 = F when the trade is final, or 8 150 = 8 when the trade does not open.

- Measured time from AJ to 8 150 = F in CRX tests: 2.6 seconds at the 50th percentile, 2.9 seconds at the 99th, plus the time to the Ethereum block of the trade.
- CRX support calls the firm about an order at 39 = A for more than 10 minutes.

Maker:

1. Request: CRX sends QuoteRequest (R) for each RFQ. Side (54) is the taker's side.
2. Quote: before ExpireTime (126), send Quote (S) with the terms of the R. CRX answers with AI 297 = 0 (live) or 297 = 5 (rejected). To decline, send QuoteRequestReject (AG).
3. Accept or pass: before a taker accepts, the maker can cancel its quote with QuoteCancel (Z).
4. Confirm: when a taker accepts the quote, CRX sends 8 150 = 0 (New). The quote stays binding.
5. Fill: CRX sends 8 150 = F when the quote wins and the trade is final. A quote that does not win gets AI 297 = 7 at the quote end.

### 6.2 RFQ and quote

```text
Taker                          CRX                              Maker
  | R QuoteRequest ----------->  |                                  |
  | <------- AI 297=10 (Pending) |                                  |
  |                              | R QuoteRequest ----------------> |
  |                              | <------- S Quote, signed (< 5 s) |
  |                              | AI 297=0 ----------------------> |
  | <-------- S Quote (best one) |                                  |
```

### 6.3 Accept

```text
Taker                          CRX                              Maker
  | AJ 694=1, signed --------->  |                                  |
  | <-------- 8 150=A (< 100 ms) |                                  |
  | <-------------- 8 150=0      | 8 150=0 -----------------------> |
  |                              |   (trade opens on Ethereum)      |
  | <----- 8 150=F, TrdMatchID X | 8 150=F, TrdMatchID X ---------> |
  |                              | AI 297=7 to each other maker --> |
```

### 6.4 Pass

```text
Taker                          CRX                              Maker
  | AJ 694=6 ----------------->  |                                  |
  | <-------------- AI 297=11    |                                  |
  |                              | AI 297=7 at the quote end -----> |
```

### 6.5 Expiry

```text
Taker                          CRX                              Maker
  | (no AJ before 62)            |                                  |
  | <-- AI 297=7 QUOTE_EXPIRED   | AI 297=7 at the quote end -----> |
  | AJ 694=1 after 62 -------->  |                                  |
  | <-- 8 150=8, QUOTE_EXPIRED   |                                  |
```

### 6.6 No quote and decline

```text
Taker                          CRX                              Maker
  | R QuoteRequest ----------->  |                                  |
  | <------- AI 297=10 (Pending) | R QuoteRequest ----------------> |
  |                              | <-------- AG decline (optional)  |
  | <--------- AG 658=8 NO_QUOTE |                                  |
```

When every live maker declines and no quote arrives, the RFQ ends before the 5-second window ends.

### 6.7 Cancel

```text
Maker                          CRX
  | Z QuoteCancel ------------>  |
  | <-------------- AI 297=1     |   (no accept before the cancel)
  | <-- j 380=0 QUOTE_ACCEPTED   |   (a taker accepted first)
  | <-- j 380=0 QUOTE_NOT_LIVE   |   (the quote has ended)
```

### 6.8 States

| Message | State | Meaning | Final | Next action |
|---|---|---|---|---|
| AI 297 = 10 to the taker | Pending | CRX received the R and asks the makers. | No | Wait for S or AG. |
| S to the taker | Quoted | One binding quote, valid until ValidUntilTime (62). | No | Send AJ 694 = 1 (accept) or 694 = 6 (pass). |
| AG to the taker | Rejected or no quote | No quote for this request. | Yes | Correct the cause and send a new R with a new QuoteReqID. |
| AI 297 = 7 to the taker | Expired | The quote expired with no accept. | Yes | Send a new R. |
| AI 297 = 11 | Passed | The taker passed. | Yes | None. |
| 8 150 = A, 39 = A | Pending New | CRX received the accept and checks it. The order stays here until the outcome is clear. | No | Wait for 150 = F or 150 = 8. |
| 8 150 = 0, 39 = 0 | New | CRX took the accept, or a taker accepted the maker's quote. The trade is not final. | No | Wait for the fill. |
| 8 150 = F, 39 = 2 | Filled | The trade is final. | Yes | Book the trade with TrdMatchID (880). |
| 8 150 = 8, 39 = 8 | Rejected | No trade. | Yes | Read 20009. Send a new R if the code allows a retry. |
| 8 150 = H, 39 = 4 | Trade Cancel | Correction by CRX only, outside normal operation. | Yes | Remove the trade from the books. |
| AI 297 = 0 to the maker | Quote live | CRX accepted the signed quote. It is binding. | No | Wait. |
| AI 297 = 5 | Quote rejected | CRX rejected the quote. | Yes | Read 20009. |
| AI 297 = 1 | Quote canceled | CRX confirmed the quote withdrawal. | Yes | None. |
| AI 297 = 7 to the maker | Quote expired | The quote expired with no trade. | Yes | None. |
| AI 297 = 9 | Not found | CRX has no quote with this QuoteID for the seat. | Yes | Check the QuoteID. |

### 6.9 Races

| Race | Result |
|---|---|
| AJ reaches CRX after ValidUntilTime (62) | 8 150 = 8, 103 = 4, code `QUOTE_EXPIRED`. No trade. |
| AJ reaches CRX shortly before ValidUntilTime (62) | CRX checks the price before it compares its own clock with 62, so an AJ received before 62 can get `QUOTE_EXPIRED`. Keep the host clock on NTP. |
| Taker disconnects after it sends AJ | The accept stays valid if it reached CRX. After the Logon, resend or H gives the state. |
| Maker disconnects after it quotes | The quote stays binding and can fill. The maker gets 8 150 = F after its next Logon. |
| Taker AJ 694 = 6 after its accept on the same quote | j 380 = 0, code `QUOTE_ACCEPTED`. The trade stays valid. |
| CRX refuses or retracts a trade after the fill | 8 150 = H (Trade Cancel), 39 = 4, code `TRADE_CANCELLED`. |
| CRX refuses a trade before the fill | 8 150 = 8, 39 = 8. |
| CRX retracts a trade before the fill | No report. The order waits for the trade. |
| Maker Z while CRX posts the quote | CRX waits for the result of the quote, then answers the Z. |
| Taker AJ 694 = 6 after 62 | j 380 = 0, code `QUOTE_NOT_LIVE`. |
| Maker Z and taker AJ on one quote | The first to reach CRX wins. If AJ is first, the trade opens and Z gets j 380 = 0, code `QUOTE_ACCEPTED`. If Z is first, AJ gets 8 150 = 8, code `QUOTE_NOT_LIVE`. |
| Second AJ, same QuoteRespID and ClOrdID | A repeat: CRX sends the stored answer with PossResend (97) = Y and opens no second trade. |
| Second AJ on one quote, new ClOrdID | 8 150 = 8, 103 = 6, code `DUPLICATE`. No second trade. |
| Maker S after ExpireTime (126) | AI 297 = 5, 300 = 4, code `QUOTE_WINDOW_CLOSED`. |
| AJ in the last seconds before the daily reset | The answer goes out after the 17:00:30 Logon. Send OrderStatusRequest (H) after that Logon. |
| CRX has no clear outcome for an accept | The order stays at 150 = A, 39 = A. 150 = F or 150 = 8 follows when CRX has the outcome. H answers 39 = A until then. |
| No ExecutionReport 5 seconds after an AJ | The state is unknown. Send OrderStatusRequest (H). Do not send a new AJ with a new ClOrdID for the same quote. |

## 7. Messages

Req is Y (required), N (optional) or C (required under the condition in the notes). `→` marks a field in the NoRelatedSym (146) group. The [dictionary](#13-dictionary) gives the field order. MaturityDate (541) and SettlDate (64) hold the same date.

### 7.1 Header and trailer

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 8 | BeginString | Y | `FIX.4.4` |
| 9 | BodyLength | Y | |
| 35 | MsgType | Y | |
| 49 | SenderCompID | Y | Firm CompID inbound; `CRX-TRD` or `CRX-DC` outbound. |
| 56 | TargetCompID | Y | `CRX-TRD` or `CRX-DC` inbound; firm CompID outbound. |
| 34 | MsgSeqNum | Y | |
| 43 | PossDupFlag | C | `Y` on a message resent under its original MsgSeqNum. |
| 97 | PossResend | C | `Y` on a stored answer resent under a new MsgSeqNum, a message cut off by a session end, or a report held over a CRX restart. |
| 52 | SendingTime | Y | UTC with milliseconds. |
| 50 | SenderSubID | N | Inbound only. CRX returns it in TargetSubID (57) on each answer. |
| 57 | TargetSubID | C | Outbound only. SenderSubID (50) of the message CRX answers. |
| 122 | OrigSendingTime | C | Required when 43 = Y. Not later than 52. |
| 10 | CheckSum | Y | Trailer. |

CRX sends header tags in this order: 8, 9, 35, 49, 56, 34, 43, 97, 52, 122, 57.

### 7.2 Logon (A)

Firm to CRX, as received from the signature proxy:

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 98 | EncryptMethod | Y | `0` |
| 108 | HeartBtInt | Y | 5 to 60 seconds. Use 30; at least 30 with a custodian back end. |
| 141 | ResetSeqNumFlag | N | `Y` restarts both sides at 1; MsgSeqNum must then be 1. Defaults to `N`. |
| 553 | Username | Y | Seat address: `0x` and 40 lowercase hex characters. The signature proxy adds it if absent. |
| 20012 | CrxLoginKey | C | Login key address, if the login key signs. Omitted when the seat signs. |
| 20017 | CrxLoginChain | C | Chain ID bound in the Logon signature, as a positive decimal. The signature proxy adds it. |
| 95 | RawDataLength | Y | `132` |
| 96 | RawData | Y | Login message signature, added by the signature proxy. |
| 20013 | CrxSignRefusal | C | Why the signature proxy did not sign. See [Unsigned messages](#56-unsigned-messages). |

CRX to firm: 98 = `0`, 108 = the firm's value, 141 = `Y` if the firm sent `Y`.

Samples: [`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix), [`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix), [`03-logon-answer.fix`](examples/03-logon-answer.fix), [`04-logon-rejected.fix`](examples/04-logon-rejected.fix). See [Raw examples](#12-raw-examples).

### 7.3 Logout (5)

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 58 | Text | C | Always on a CRX Logout. See [Text format](#92-text-format). |
| 20009 | CrxErrorCode | C | Always on a CRX Logout. See [Logout codes](#96-logout-codes). |

Samples: [`11-logout-renewal.fix`](examples/11-logout-renewal.fix), [`12-logout-daily.fix`](examples/12-logout-daily.fix).

### 7.4 Heartbeat (0), TestRequest (1), ResendRequest (2), SequenceReset (4)

| Message | Tag | Name | Req | Values and notes |
|---|---|---|---|---|
| Heartbeat (0) | 112 | TestReqID | C | Required in the answer to a TestRequest. |
| TestRequest (1) | 112 | TestReqID | Y | Any text. |
| ResendRequest (2) | 7 | BeginSeqNo | Y | 1 or more. |
| ResendRequest (2) | 16 | EndSeqNo | Y | `0` = up to the last message sent. CRX resends in batches of 1,000 messages. |
| SequenceReset (4) | 123 | GapFillFlag | N | `Y` = GapFill mode. |
| SequenceReset (4) | 36 | NewSeqNo | Y | |

Samples: [`05-heartbeat.fix`](examples/05-heartbeat.fix), [`06-test-request.fix`](examples/06-test-request.fix), [`07-heartbeat-answer.fix`](examples/07-heartbeat-answer.fix), [`08-resend-request.fix`](examples/08-resend-request.fix), [`09-gap-fill.fix`](examples/09-gap-fill.fix).

### 7.5 Reject (3)

CRX to firm.

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 45 | RefSeqNum | Y | MsgSeqNum of the rejected message. |
| 371 | RefTagID | C | Tag at fault, if any. |
| 372 | RefMsgType | C | MsgType of the rejected message. |
| 373 | SessionRejectReason | Y | See [Session Reject values](#93-session-reject-values). |
| 58 | Text | Y | Coded Text. |

CRX sends a Reject (3) immediately, ahead of any reports queued at a Logon.

Sample: [`10-session-reject.fix`](examples/10-session-reject.fix).

### 7.6 QuoteRequest (R), taker to CRX

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 131 | QuoteReqID | Y | Request ID: 1 to 128 printable ASCII characters, unique per seat. |
| 146 | NoRelatedSym | Y | `1`. Any other value gets AG, code `INVALID_REQUEST`. |
| →55 | Symbol | Y | `USD/MXN`, `USD/BRL` or `USD/PHP`. First field of the group. |
| →167 | SecurityType | N | `FXNDF` |
| →541 | MaturityDate | N | UTC date of 20001, as `YYYYMMDD`. Any other date gets AG, code `MATURITY_MISMATCH`. |
| →537 | QuoteType | N | `1` (Tradeable). Any other value gets AG, code `INVALID_REQUEST`. |
| →54 | Side | Y | Taker's side in USD: `1` = buy USD, `2` = sell USD. |
| →38 | OrderQty | Y | Notional in USD: minimum 100, up to 6 decimal places. |
| →64 | SettlDate | N | Same as 541. |
| →15 | Currency | N | Base currency of 55: `USD`. Any other value gets AG, code `CURRENCY_NOT_BASE`. |
| →60 | TransactTime | N | |
| →20001 | CrxMaturityTime | Y | Settlement time, UTC with milliseconds. See [Settlement time](#103-settlement-time). |
| →20002 | CrxPremiumBps | N | Upfront premium in basis points of the notional: positive if the taker pays, negative if the maker pays. Defaults to 0. |
| 1 | Account | N | Seat address, if present. |

CRX returns AI 297 = 10 immediately, then S or AG. A request that fails a field check gets AG immediately.

Sample: [`20-quote-request.fix`](examples/20-quote-request.fix).

### 7.7 QuoteStatusReport (AI), CRX to taker

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 649 | QuoteStatusReqID | C | Echoed from QuoteStatusRequest (a), if the request had it. |
| 131 | QuoteReqID | C | The firm's QuoteReqID. Absent on 297 = 9. |
| 117 | QuoteID | Y | CRX quote ID. On 297 = 10, the QuoteReqID; on 297 = 9, the QuoteID of the a or AJ; in an answer to an a that names a QuoteReqID, that QuoteReqID. |
| 693 | QuoteRespID | C | QuoteRespID of the AJ, on 297 = 11 and on 297 = 9 to a pass. |
| 55 | Symbol | Y | On 297 = 9, the Symbol of the AJ or `N/A`. |
| 60 | TransactTime | Y | |
| 297 | QuoteStatus | Y | `10` = Pending. `11` = Pass. `7` = Expired. `9` = Quote not found (a pass on an unknown QuoteID). In an answer to a: `0` = accepted (also after 62) or live; `5` = the R got AG; `9` = Quote not found. |
| 58 | Text | C | With 20009. |
| 20009 | CrxErrorCode | C | On 297 = 9, and on 297 = 7 at the quote end. |

Samples: [`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix), [`31-quote-status-pass.fix`](examples/31-quote-status-pass.fix), [`32-quote-status-expired.fix`](examples/32-quote-status-expired.fix).

### 7.8 Quote (S), CRX to taker

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 131 | QuoteReqID | Y | The firm's QuoteReqID. |
| 117 | QuoteID | Y | CRX quote ID, for the AJ. |
| 537 | QuoteType | Y | `1` |
| 55 | Symbol | Y | |
| 167 | SecurityType | Y | `FXNDF` |
| 541 | MaturityDate | Y | |
| 54 | Side | Y | Same as the R. |
| 38 | OrderQty | Y | Same as the R. |
| 64 | SettlDate | Y | Same as 541. |
| 15 | Currency | Y | Base currency of 55: `USD`. |
| 133 | OfferPx | C | Rate if the taker buys (54 = 1). |
| 132 | BidPx | C | Rate if the taker sells (54 = 2). |
| 190 | OfferSpotRate | C | Spot part of OfferPx, if CRX has a price breakdown. |
| 191 | OfferForwardPoints | C | Forward points of OfferPx, with 190. OfferPx = OfferSpotRate + OfferForwardPoints. |
| 188 | BidSpotRate | C | Spot part of BidPx, if CRX has a price breakdown. |
| 189 | BidForwardPoints | C | Forward points of BidPx, with 188. BidPx = BidSpotRate + BidForwardPoints. |
| 631 | MidPx | C | Forward mid rate, if CRX has one. |
| 62 | ValidUntilTime | Y | Quote expiry: the deadline to accept. See [Terms](#24-terms). |
| 60 | TransactTime | Y | |
| 20001 | CrxMaturityTime | Y | |
| 20002 | CrxPremiumBps | Y | |
| 20008 | CrxTypedData | Y | `Trade` for the signature proxy to sign, as Base64 of the JSON typed data `{types, primaryType, domain, message}`. |
| 20016 | CrxSpotTime | C | Time of the spot observation that CRX supplies. Absent when unavailable. |

- Spot and forward points come from the quote that CRX supplies; an absent value stays absent. Forward points are in rate units and can be negative.
- CRX sends at most one S per RFQ, and no other S after it expires.

Sample: [`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix).

### 7.9 QuoteRequestReject (AG), CRX to taker

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 131 | QuoteReqID | Y | |
| 658 | QuoteRequestRejectReason | Y | `1`, `2`, `3`, `4`, `6`, `8` or `99`. See [Business reject codes](#94-business-reject-codes). |
| 146 | NoRelatedSym | Y | `1` |
| →55 | Symbol | Y | Symbol of the R, or `N/A` if the R has none. |
| 58 | Text | Y | Coded Text. |
| 20009 | CrxErrorCode | Y | |

Sample: [`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix).

### 7.10 QuoteResponse (AJ), taker to CRX

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 693 | QuoteRespID | Y | Response ID: 1 to 128 printable ASCII characters, unique per seat. |
| 117 | QuoteID | Y | QuoteID of the S. |
| 694 | QuoteRespType | Y | `1` = Hit/Lift (accept). `6` = Pass. |
| 11 | ClOrdID | C | Order ID: 1 to 128 printable ASCII characters, unique per seat. Required if 694 = 1. |
| 55 | Symbol | Y | Same as the S. |
| 167 | SecurityType | N | Same as the S. |
| 541 | MaturityDate | N | Same as the S. |
| 54 | Side | Y | Same as the S. |
| 38 | OrderQty | Y | Same as the S: the full amount only. |
| 64 | SettlDate | N | Same as the S. |
| 15 | Currency | N | Base currency of 55: `USD`. Any other value gets 8 150 = 8, code `CURRENCY_NOT_BASE`. |
| 44 | Price | Y | Quoted rate. |
| 60 | TransactTime | Y | |
| 1 | Account | N | Seat address, if present. |
| 20007 | CrxSignature | C | Accept signature, added by the signature proxy. Required if 694 = 1. |
| 20013 | CrxSignRefusal | C | Why the signature proxy did not sign. |

- A value that differs from the S gets 8 150 = 8 and no trade: code `QUOTE_MISMATCH`, or `MATURITY_MISMATCH` for a 541 or 64 off the date of the S.
- On a quote that another session of the seat holds, 694 = 6 gets j 380 = 0, code `QUOTE_OTHER_SESSION`, and 694 = 1 gets 8 150 = 8, code `UNKNOWN_QUOTE`.
- A pass (694 = 6) gets AI 297 = 11. On a quote past 62, passed or expired, it gets j 380 = 0, code `QUOTE_NOT_LIVE`.
- NewOrderSingle (D) is not an accept; it gets j 380 = 3, code `UNSUPPORTED_MESSAGE`.

Samples: [`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix), [`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix), [`30-quote-response-pass.fix`](examples/30-quote-response-pass.fix), [`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix).

### 7.11 ExecutionReport (8), CRX to firm

A fill is a report with 150 = F, or with 150 = I and 39 = 2. A known order is an accept or a quote that CRX holds.

- Book a trade on 150 = F, once per TrdMatchID (880).
- 150 = I repeats the fill fields for status only. Do not book it.

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 37 | OrderID | Y | Trade ID, or `NONE` until CRX assigns one. |
| 11 | ClOrdID | C | Taker: the AJ ClOrdID. Maker: its QuoteID. Absent if the AJ had none. |
| 693 | QuoteRespID | C | Taker: QuoteRespID of the AJ. |
| 790 | OrdStatusReqID | C | Echoed from H, if the request had it. |
| 17 | ExecID | Y | Report ID, unique per report. |
| 19 | ExecRefID | C | On 150 = H, the ExecID of the cancelled fill. |
| 150 | ExecType | Y | `A`, `0`, `F`, `8`, `H` or `I`. |
| 39 | OrdStatus | Y | `A`, `0`, `2`, `4`, `8` or `C`. |
| 103 | OrdRejReason | C | On 150 = 8, and on 150 = I for an unknown order. |
| 64 | SettlDate | C | For a known order. Same as 541. |
| 55 | Symbol | Y | `N/A` if CRX does not know it. |
| 167 | SecurityType | Y | `FXNDF` |
| 541 | MaturityDate | C | For a known order. |
| 54 | Side | Y | Receiver's own side. |
| 38 | OrderQty | Y | `0` for an unknown order. |
| 15 | Currency | Y | Base currency of 55: `USD`. |
| 32 | LastQty | C | On a fill. |
| 31 | LastPx | C | Fill rate, on a fill. |
| 194 | LastSpotRate | C | Spot part of LastPx, on a fill with a price breakdown. |
| 195 | LastForwardPoints | C | Forward points of LastPx, with 194. LastPx = LastSpotRate + LastForwardPoints. |
| 20016 | CrxSpotTime | C | Spot observation time kept from the accepted quote, when available. |
| 151 | LeavesQty | Y | OrderQty while 39 = A or 0. `0` in other states. |
| 14 | CumQty | Y | OrderQty on a fill. `0` in other reports. |
| 6 | AvgPx | Y | The rate on a fill. `0` in other reports. |
| 75 | TradeDate | C | UTC trade date, on a fill. |
| 60 | TransactTime | Y | |
| 120 | SettlCurrency | C | `USD`, with 541. |
| 851 | LastLiquidityInd | C | Seat's role: `1` maker (added liquidity), `2` taker (removed liquidity). On 150 = F if CRX has the role; never on 150 = I. A drop-copy fill can omit it. |
| 58 | Text | C | With 103, on 150 = H, and with `QUOTE_LIVE` on the status of a live maker quote. |
| 117 | QuoteID | C | Taker: the CRX quote ID. Maker: its QuoteID. Absent if CRX does not know the quote. |
| 880 | TrdMatchID | C | Trade match ID, the same for taker and maker. On a fill. |
| 20001 | CrxMaturityTime | C | With 541. |
| 20002 | CrxPremiumBps | C | With 541. |
| 20009 | CrxErrorCode | C | With 103, and on 150 = H. `QUOTE_LIVE` on the status of a live maker quote. |

| Report | Fields in addition to the Y fields |
|---|---|
| 150 = A or 0 | 64, 541, 120, 20001, 20002. 151 = 38. |
| 150 = F | 64, 541, 120, 20001, 20002, 851, 32, 31, 75 and 880. 194 and 195 when CRX has a price breakdown. 151 = 0. |
| 150 = 8 | 103, 58, 20009. Also 64, 541, 120, 20001 and 20002 for a known order. |
| 150 = H | 19, 58, 20009, 880, 64, 541, 120, 20001 and 20002. 151 = 0, 14 = 0, 6 = 0. |
| 150 = I | Fields of the current state. For an unknown order: 39 = 8, 103 = 5, 58 and 20009, with no dates. |

Each taker report on an accept also has 693.

| 150 ExecType | 39 OrdStatus | When | Final |
|---|---|---|---|
| `A` Pending New | `A` Pending New | Taker only. CRX received the accept; sent within 100 milliseconds. The order stays at `A` until its outcome is clear. | No |
| `0` New | `0` New | Taker: CRX took the accept. Maker: a taker accepted the quote. | No |
| `F` Trade | `2` Filled | The trade is final on Ethereum. | Yes |
| `8` Rejected | `8` Rejected | CRX rejected the accept, or the trade did not open. | Yes |
| `H` Trade Cancel | `4` Canceled | CRX correction only, outside normal operation. Code `TRADE_CANCELLED`. | Yes |
| `I` Order Status | The current state. For a maker quote, see [OrderStatusRequest](#712-orderstatusrequest-h-firm-to-crx). | Answer to OrderStatusRequest (H). | As the state |

- A fill (150 = F) is final. CRX sends 150 = H only to correct an error.
- CRX sends each fill once, to the session that sent the accept or the quote.
- A drop-copy session receives the same 150 = F report for each trade of its seat.

Samples: [`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix), [`27-exec-new.fix`](examples/27-exec-new.fix), [`28-exec-fill.fix`](examples/28-exec-fill.fix), [`29-exec-rejected.fix`](examples/29-exec-rejected.fix), [`34-exec-status.fix`](examples/34-exec-status.fix), [`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix), [`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix).

### 7.12 OrderStatusRequest (H), firm to CRX

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 790 | OrdStatusReqID | N | Request ID, echoed in the answer. |
| 11 | ClOrdID | Y | Taker: the AJ ClOrdID. Maker: its own QuoteID. |
| 55 | Symbol | Y | |
| 54 | Side | Y | |

CRX returns 8 150 = I with the current state from the seat's records. An unknown ClOrdID gets 8 150 = I, 39 = 8, 103 = 5, code `UNKNOWN_ORDER`, with ClOrdID and 790.

For a maker, ClOrdID is its QuoteID, and the answer gives the quote state:

| 39 OrdStatus | State of the quote |
|---|---|
| `A` | Live and not accepted, with 20009 = `QUOTE_LIVE`. Also while the posting of the quote is pending. |
| `0` | Accepted by a taker; the fill is pending. |
| `2` | Filled. |
| `C` | Ended with no trade. |
| `4` | Canceled. |
| `8` | CRX rejected the quote, or the trade failed. |

Samples: [`33-order-status-request.fix`](examples/33-order-status-request.fix), [`34-exec-status.fix`](examples/34-exec-status.fix).

### 7.13 QuoteRequest (R), CRX to maker

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 131 | QuoteReqID | Y | The CRX RFQ ID. |
| 146 | NoRelatedSym | Y | `1` |
| →55 | Symbol | Y | |
| →167 | SecurityType | Y | `FXNDF` |
| →541 | MaturityDate | Y | |
| →54 | Side | Y | The taker's side. `1` = the taker buys USD: send OfferPx. `2` = the taker sells USD: send BidPx. |
| →38 | OrderQty | Y | Notional in USD. |
| →64 | SettlDate | Y | Same as 541. |
| →15 | Currency | Y | Base currency of 55: `USD`. |
| →62 | ValidUntilTime | Y | RFQ end: TransactTime + 120 seconds. |
| →126 | ExpireTime | Y | Quote deadline: normally TransactTime + 5 seconds, and at most half the RFQ life. A test request uses 62. CRX can close collection sooner. |
| →60 | TransactTime | Y | RFQ open time. |
| →20001 | CrxMaturityTime | Y | |
| →20002 | CrxPremiumBps | Y | |
| →20003 | CrxTakerRef | Y | Taker reference that the signature proxy signs. It does not identify the taker. |
| →20004 | CrxQuoteExpiryMax | Y | Latest time the quote binds, UTC with seconds. Copy it into ValidUntilTime (62) of the Quote. |
| →20014 | CrxTestRequest | N | `Y` for a maker test request. The quote stays binding. |
| →20015 | CrxRequestExpiresAt | C | End of the test request, when CRX supplies it. It does not extend 126 or 62. |

Sample: [`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix).

### 7.14 Quote (S), maker to CRX

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 131 | QuoteReqID | Y | From the R. |
| 117 | QuoteID | Y | Quote ID: 1 to 128 printable ASCII characters, unique per seat. |
| 537 | QuoteType | N | `1`. Any other value gets AI 297 = 5, code `QUOTE_NOT_TRADEABLE` or `INVALID_FIELD`. |
| 55 | Symbol | Y | Same as the R. |
| 167 | SecurityType | N | Same as the R: `FXNDF`. |
| 541 | MaturityDate | N | Same as the R: the date of 20001. |
| 54 | Side | Y | Same as the R: the taker's side. |
| 38 | OrderQty | Y | Same as the R. The full amount only. |
| 64 | SettlDate | N | Same as 541. |
| 15 | Currency | Y | Same as the R: base currency of 55, `USD`. |
| 1 | Account | N | Seat address, if present. |
| 132 | BidPx | C | Rate if the R Side is 2. |
| 133 | OfferPx | C | Rate if the R Side is 1. |
| 62 | ValidUntilTime | Y | The latest time the quote binds. Not earlier than CrxQuoteExpiryMax (20004) of the R. |
| 20001 | CrxMaturityTime | Y | Same as the R. |
| 20002 | CrxPremiumBps | Y | Same as the R. `0` when the R has none. |
| 20005 | CrxLegId | Y | Leg ID, added by the signature proxy. |
| 20006 | CrxSalt | Y | Salt, added by the signature proxy. |
| 20007 | CrxSignature | Y | Quote signature, added by the signature proxy. |
| 20013 | CrxSignRefusal | C | Why the signature proxy did not sign. |

- Copy 54, 38, 15, 20001 and 20002 from the R. Set 62 to CrxQuoteExpiryMax (20004) of the R.
- The signature proxy signs these fields. See [Maker quote signature](#53-maker-quote-signature).
- A field that differs from the R, a 62 earlier than 20004, or a 541 or 64 other than the date of 20001 gets AI 297 = 5, 300 = 99, code `QUOTE_TERMS_MISMATCH`.
- Send exactly one of 132 and 133.
- A price on the other side gets AI 297 = 5, 300 = 99, code `WRONG_SIDE`.
- A rejected second Quote on one RFQ gets AI 297 = 5; CrxErrorCode (20009) gives the cause.
- A Quote with other terms on a QuoteID that CRX holds gets j 380 = 0, code `DUPLICATE`; the first quote does not change.

Samples: [`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix), [`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix). Unsigned quotes: [`63-quote-unsigned.fix`](examples/63-quote-unsigned.fix), [`64-quote-status-unsigned.fix`](examples/64-quote-status-unsigned.fix), [`65-quote-status-life.fix`](examples/65-quote-status-life.fix).

### 7.15 QuoteRequestReject (AG), maker to CRX

A maker declines an RFQ with AG.

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 131 | QuoteReqID | Y | The CRX RFQ ID. |
| 658 | QuoteRequestRejectReason | Y | `10` = pass. `2` = market closed. `3` = size not offered. `8` = no price. `99` with Text `TENOR` = tenor not offered. Any other value = no reason given. |
| 146 | NoRelatedSym | N | `1` |
| →55 | Symbol | N | |
| 58 | Text | N | |

- CRX does not answer a valid decline; a rejected decline gets j with the code.
- Decline only before ExpireTime (126). A maker that declines sends no quote on that RFQ.

Sample: [`59-maker-decline.fix`](examples/59-maker-decline.fix).

### 7.16 QuoteStatusReport (AI), CRX to maker

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 649 | QuoteStatusReqID | C | Echoed from QuoteStatusRequest (a), if the request had it. |
| 131 | QuoteReqID | C | The CRX RFQ ID. On 297 = 9, the QuoteReqID of the Z, if it had one. |
| 117 | QuoteID | Y | The maker's QuoteID. |
| 55 | Symbol | Y | `N/A` on 297 = 9. |
| 60 | TransactTime | Y | |
| 297 | QuoteStatus | Y | `0` = Accepted (quote live). `1` = Canceled. `5` = Rejected. `7` = Expired. `9` = Quote not found. In an answer to a: `0` = live, won or filled; `5` = rejected, or the trade failed or CRX cancelled it; `10` = Pending, while CRX checks the quote. For the trade state, send [OrderStatusRequest](#712-orderstatusrequest-h-firm-to-crx) (H). |
| 58 | Text | C | On 297 = 9, on 297 = 7 at the quote end, and on 297 = 5 outside an answer to a. |
| 300 | QuoteRejectReason | C | On 297 = 5, outside an answer to a. |
| 20009 | CrxErrorCode | C | With 58. |

Samples: [`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix), [`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix), [`57-quote-status-canceled.fix`](examples/57-quote-status-canceled.fix), [`58-quote-status-expired.fix`](examples/58-quote-status-expired.fix), [`61-quote-status-answer.fix`](examples/61-quote-status-answer.fix).

A confirmed withdrawal through REST, WebSocket or an account control also sends AI 297 = 1 for each affected FIX quote. A repeated withdrawal sends no second report. A quote that was accepted keeps its trade state.

### 7.17 QuoteCancel (Z), maker to CRX

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 117 | QuoteID | Y | The maker's QuoteID. |
| 298 | QuoteCancelType | Y | `5` = cancel the quote in QuoteID. |
| 131 | QuoteReqID | N | The CRX RFQ ID. |

Answers:

| Case | Answer |
|---|---|
| The quote is live | AI 297 = 1. |
| A taker accepted the quote | j 380 = 0, code `QUOTE_ACCEPTED`. 379 holds the QuoteID. The quote binds and the trade stands. |
| The quote has ended | j 380 = 0, code `QUOTE_NOT_LIVE`. 379 holds the QuoteID. |
| Another session of the seat holds the quote | j 380 = 0, code `QUOTE_OTHER_SESSION`. Text names the SenderCompID that holds it. |
| CRX has no quote with this QuoteID | AI 297 = 9, code `UNKNOWN_QUOTE`. |
| QuoteCancelType (298) is not 5 | Reject (3), 373 = 5. |
| CRX is posting the quote, or the posting outcome is unclear | CRX waits for the outcome, across reconnects, then cancels the quote or answers with its actual state as above. CRX answers the Z once. |

Samples: [`56-quote-cancel.fix`](examples/56-quote-cancel.fix), [`57-quote-status-canceled.fix`](examples/57-quote-status-canceled.fix).

### 7.18 QuoteStatusRequest (a), firm to CRX

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 649 | QuoteStatusReqID | N | Request ID, echoed in the AI. |
| 117 | QuoteID | Y | A CRX quote ID (taker) or the maker's QuoteID. |
| 55 | Symbol | Y | |

CRX returns AI with the current state from the seat's records. An unknown QuoteID gets AI 297 = 9, code `UNKNOWN_QUOTE`.

Samples: [`60-quote-status-request.fix`](examples/60-quote-status-request.fix), [`61-quote-status-answer.fix`](examples/61-quote-status-answer.fix).

### 7.19 SecurityListRequest (x) and SecurityList (y)

SecurityListRequest (x), firm to CRX:

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 320 | SecurityReqID | Y | |
| 559 | SecurityListRequestType | Y | `4` = all securities. `0` = the Symbol in 55 only. |
| 55 | Symbol | C | Required if 559 = 0. |

SecurityList (y), CRX to firm:

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 320 | SecurityReqID | Y | From the x. |
| 322 | SecurityResponseID | Y | |
| 560 | SecurityRequestResult | Y | `0` = valid request. |
| 146 | NoRelatedSym | Y | Number of markets. |
| →55 | Symbol | Y | A live market; paused markets are not listed. |
| →167 | SecurityType | Y | `FXNDF` |
| →15 | Currency | Y | Base currency: `USD`. |
| →562 | MinTradeVol | C | Minimum notional in USD, if CRX sets one: `100`. |

- One y holds all markets.
- Rates have at most 6 decimal places. See [Message format](#42-message-format).
- If CRX cannot read the markets, it returns j with the SecurityReqID in 379.

Samples: [`39-security-list-request.fix`](examples/39-security-list-request.fix), [`40-security-list.fix`](examples/40-security-list.fix).

### 7.20 BusinessMessageReject (j), CRX to firm

| Tag | Name | Req | Values and notes |
|---|---|---|---|
| 45 | RefSeqNum | C | MsgSeqNum of the rejected message. Absent if CRX rejects a request after it starts processing it. |
| 372 | RefMsgType | Y | |
| 379 | BusinessRejectRefID | C | ID of the rejected request, if known, such as QuoteReqID, QuoteID, QuoteRespID, ClOrdID or SecurityReqID. Absent on `UNSUPPORTED_MESSAGE`. |
| 380 | BusinessRejectReason | Y | `0` = other. `1` = unknown ID. `3` = unsupported message type. `4` = application not available. `6` = not authorized. |
| 58 | Text | Y | Coded Text. |
| 20009 | CrxErrorCode | Y | |

Samples: [`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix), [`36-rate-limited.fix`](examples/36-rate-limited.fix), [`62-business-reject.fix`](examples/62-business-reject.fix).

## 8. Custom tags

CRX uses tags 20001 to 20099. Tags not listed are reserved.

| Tag | Name | Type | Messages | Value | REST field |
|---|---|---|---|---|---|
| 20001 | CrxMaturityTime | UTCTimestamp, milliseconds | R, S, 8 | Settlement time | `expiry`, Unix time in milliseconds |
| 20002 | CrxPremiumBps | int, signed | R, S, 8 | Upfront premium in basis points | `premium_bps` |
| 20003 | CrxTakerRef | `0x` and 64 hex | R to maker | Reference that the maker signs | `taker_ref` |
| 20004 | CrxQuoteExpiryMax | UTCTimestamp, seconds | R to maker | The latest time the quote binds | `quote_expiry_max`, Unix time in seconds |
| 20005 | CrxLegId | `0x` and 64 hex | S from maker | Leg ID | `leg_id` |
| 20006 | CrxSalt | `0x` and 64 hex | S from maker | Salt | `salt` |
| 20007 | CrxSignature | `0x` and 130 hex | S from maker, AJ 694 = 1 | Signature | `sig` |
| 20008 | CrxTypedData | Base64 | S to taker | JSON typed data of the `Trade` | `trade_template.typed_data` |
| 20009 | CrxErrorCode | String | AG, AI, 8, j, Logout | Code in `UPPER_SNAKE` case | `code`, in upper case |
| 20010 | — | — | — | Not used | — |
| 20011 | — | — | — | Not used | — |
| 20012 | CrxLoginKey | `0x` and 40 hex | A | Login key address | — |
| 20013 | CrxSignRefusal | String | A, S, AJ from the signature proxy | Why the signature proxy did not sign | — |
| 20014 | CrxTestRequest | Boolean | R to maker | `Y` for a maker test request | — |
| 20015 | CrxRequestExpiresAt | UTCTimestamp | R to maker | End of the test request | `request_expires_at` |
| 20016 | CrxSpotTime | UTCTimestamp | S to taker, 8 | Observation time of the quoted spot rate | `pyth_spot_at` |
| 20017 | CrxLoginChain | String | A | Chain ID bound by the Logon signature | `x-crx-chain` |

## 9. Rejects and codes

### 9.1 Which message rejects

| Problem | Answer |
|---|---|
| A bad session field or a malformed message | Reject (3) with SessionRejectReason (373) |
| An unsupported MsgType, a rate limit, or CRX cannot answer | BusinessMessageReject (j) with BusinessRejectReason (380) |
| A rejected QuoteRequest (R) | QuoteRequestReject (AG) with QuoteRequestRejectReason (658) |
| A rejected maker Quote (S) | QuoteStatusReport (AI) 297 = 5 with QuoteRejectReason (300) |
| A rejected QuoteCancel (Z) | See [QuoteCancel](#717-quotecancel-z-maker-to-crx): AI 297 = 9, j or Reject (3) |
| A rejected accept, AJ 694 = 1 | ExecutionReport (8) 150 = 8 with OrdRejReason (103) |
| A rejected Logon or a session end | Logout (5) |

### 9.2 Text format

Each Text (58) from CRX has this form:

```text
<CODE>: <effect>[ <action>] (trace <id>)
```

- `<CODE>` is the value of CrxErrorCode (20009), in `UPPER_SNAKE` case. On a Reject (3), it names the SessionRejectReason.
- `<effect>` is one sentence that names the value at fault and any limit.
- `<action>` is an optional sentence with the corrective step.
- `<id>` is the trace ID, for CRX support.
- Use 20009 in FIX engine logic and show Text to operators. Codes are stable; sentences can change.

### 9.3 Session Reject values

A rejected message consumes its MsgSeqNum; CRX does not request it again.

| 373 | Name | Code in Text | Cause | Then |
|---|---|---|---|---|
| 1 | Required tag missing | `REQUIRED_TAG_MISSING` | A required tag is absent. | The session continues. |
| 4 | Tag specified without a value | `TAG_WITHOUT_VALUE` | A tag has an empty value. | The session continues. |
| 5 | Value is incorrect | `VALUE_INCORRECT` | A NewSeqNo or a resend range is not valid. | The session continues. |
| 6 | Incorrect data format | `INCORRECT_DATA_FORMAT` | A time, number or flag has a bad format. | The session continues. |
| 9 | CompID problem | `COMP_ID_PROBLEM` | 49 or 56 is not the session's CompID. | Logout |
| 10 | SendingTime accuracy problem | `SENDING_TIME_ACCURACY` | 52 is more than 120 seconds from CRX time, or 122 is later than 52. | Logout |
| 15 | Repeating group fields out of order | `GROUP_ORDER` | A group field is out of order. | The session continues. |
| 16 | Incorrect NumInGroup count | `INCORRECT_NUM_IN_GROUP` | A group count does not match the group. | The session continues. |

CRX can send other FIX 4.4 values of 373; treat each as a reject of the message in RefSeqNum (45).

### 9.4 Business reject codes

Retry column:

- Yes: send a new request with a new ID, after the wait in Text.
- No: correct the cause first.
- Never: the result is final.

| Code (20009) | Cause | AG 658 | AI 300 | 8 103 | Retry | Correction |
|---|---|---|---|---|---|---|
| `NO_QUOTE` | No maker quoted in the window. | 8 | — | — | Yes | Send a new R later, or with other terms. |
| `MISSING_FIELD` | A required field is absent. | 99 | 99 | 99 | No | Add the field that Text names. |
| `INVALID_FIELD` | A field has a value that CRX does not take. | 99 | 99 | 99 | No | Correct the field that Text names. |
| `INVALID_REQUEST` | NoRelatedSym (146) is not 1, QuoteRequestType (303) is 2, or QuoteType (537) is not 1. | 99 | — | — | No | Send one instrument, a tradeable request type and 537 = 1. |
| `INVALID_QUANTITY` | OrderQty is not positive or has more than 6 decimal places. | 99 | — | — | No | Correct OrderQty. |
| `INVALID_PRICE` | A quote has no rate, two rates, or more than 6 decimal places. | — | 8 | — | No | Send exactly one rate. |
| `UNKNOWN_SYMBOL` | CRX does not list the Symbol, or it does not have the form `USD/MXN`. | 1 | — | — | No | Use a Symbol from SecurityList (y). |
| `BAD_REQUEST` | The settlement time is outside 1 hour to 90 days. | 3 | 3 | 3 | No | Use a time in the range that Text gives. |
| `BAD_REQUEST` | Another field is not valid. | 99 | 99 | 99 | No | Correct the field that Text names. |
| `MATURITY_MISMATCH` | MaturityDate or SettlDate is not the date of CrxMaturityTime, or of the S. | 99 | — | 99 | No | Send the date of 20001. |
| `CURRENCY_NOT_BASE` | Currency (15) is not the base currency of Symbol (55). | 99 | — | 99 | No | Send the base currency, such as `USD` for `USD/MXN`, or omit 15. |
| `PLATFORM_PAUSED` | CRX paused trading. | 2 | 2 | 2 | Yes | Resend after the pause. |
| `MARKET_PAUSED` | CRX paused the market. | 2 | 2 | 2 | Yes | Resend after the time in Text. |
| `NOTIONAL_BELOW_MINIMUM` | OrderQty is below 100 USD. | 3 | 3 | 3 | No | Increase OrderQty. |
| `NOTIONAL_ABOVE_MAXIMUM` | OrderQty is above the maximum in Text. | 3 | 3 | 3 | No | Decrease OrderQty. |
| `EXPIRY_OUTSIDE_HOURS` | The settlement time falls in a market closure, or in the first 15 minutes after a reopen. | 3 | — | — | No | Use the earliest time in Text or later. |
| `EXPIRY_PAST_FENCE` | The settlement time is after the latest date that CRX takes. | 3 | — | — | No | Use an earlier time. |
| `EXPIRY_AFTER_DELIST` | The settlement time is after the last trading time of the market. | 3 | — | — | No | Use an earlier time. |
| `QUOTE_WINDOW_CLOSED` | The maker quote reached CRX after ExpireTime (126). | — | 4 | — | Never | Quote the next RFQ sooner. |
| `QUOTE_EXPIRED` | The accept reached CRX after ValidUntilTime (62). | 4 | 4 | 4 | Yes | Send a new R. |
| `RFQ_EXPIRED` | The RFQ ended. | 4 | 4 | 4 | Yes | Send a new R. |
| `ACCOUNT_PAUSED` | Trading is paused for the account. | 6 | 99 | 99 | No | Contact CRX support. |
| `ELIGIBILITY_EXPIRED` | The account eligibility representation expired. | 6 | 99 | 99 | No | Renew the representation through CRX. |
| `NOT_WHITELISTED` | CRX did not approve the seat for this action. | 6 | 9 | 99 | No | Contact CRX support. |
| `SEAT_CANNOT_SIGN` | The seat is a contract wallet. | 6 | 99 | 99 | No | Use an EOA or MPC seat. |
| `UNAUTHORIZED` | CRX rejected the API session of the seat. | 6 | 99 | 99 | No | Log on again. |
| `ACCOUNT_MISMATCH` | Account (1) is not the seat address. | 6 | 99 | 15 | No | Send the seat address, or omit Account. |
| `WRONG_SIDE` | The maker priced the other side. | — | 99 | — | No | Send OfferPx when 54 = 1 and BidPx when 54 = 2. |
| `QUOTE_TERMS_MISMATCH` | A maker Quote field differs from the R: 55, 167, 541, 54, 38, 64, 15, 20001 or 20002. Or ValidUntilTime (62) is earlier than CrxQuoteExpiryMax (20004). | — | 99 | — | No | Copy the fields from the R. Set 62 to 20004. |
| `QUOTE_NOT_TRADEABLE` | The maker Quote has a QuoteType (537) other than `1`. | — | 99 | — | No | Send 537 = 1, or omit 537. |
| `QUOTE_MISMATCH` | An accept field differs from the S. 103 = 13 when OrderQty differs. | — | — | 99 | No | Copy the fields from the S. |
| `INVALID_SIGNATURE`, `SIGNATURE_INVALID` | The signature does not match the seat, or is malformed. | 99 | 99 | 99 | No | Check the signature proxy domain and key. |
| `SIGNATURE_MISSING` | The message has no signature and no 20013. | — | 99 | 99 | No | Send the message through the signature proxy. |
| A 20013 code | The signature proxy did not sign. See [Unsigned messages](#56-unsigned-messages). | — | 99 | 99 | No | Read the signature proxy log. |
| `QUOTE_FORMAT_OUTDATED` | The quote uses a previous signature format. | — | 99 | — | No | Update the signature proxy. |
| `NONCE_COLLISION` | The maker reused a QuoteID or a nonce. | — | 6 | — | No | Use a new QuoteID. |
| `LEG_ID_TAKEN` | The maker reused a leg ID. | — | 6 | — | No | Let the signature proxy make a new leg ID. |
| `DUPLICATE` | The quote already has an accept under another ClOrdID, or CRX holds this request with other content. | 99 | 6 | 6 | No | Send a new R. |
| `INSUFFICIENT_COLLATERAL` | The seat has insufficient free collateral. | 99 | 99 | 99 | No | Deposit USDC or reduce OrderQty. |
| `RATE_OUT_OF_BAND` | The quote is too far from the market price. | — | — | 99 | Yes | Send a new R. |
| `UNKNOWN_RFQ` | The QuoteReqID is not an RFQ that CRX sent to this session. | — | 99 | — | No | Copy QuoteReqID from the R. |
| `UNKNOWN_QUOTE` | CRX has no quote with this QuoteID for the seat. On a Z or an a: AI 297 = 9 with no 300. | — | — | 99 | No | Check the QuoteID. |
| `UNKNOWN_ORDER` | CRX has no accept with this ClOrdID for the seat. | — | — | 5 | No | Check the ClOrdID. |
| `QUOTE_NOT_LIVE` | The maker canceled the quote, or the quote expired. | — | — | 99 | Yes | Send a new R. |
| `QUOTE_PASSED` | The taker passed this quote. | — | — | 99 | Yes | Send a new R. |
| `QUOTE_ACCEPTED` | A taker already accepted this quote. CRX sends it on j for a Z or a pass. See [BusinessMessageReject codes](#95-businessmessagereject-codes). | — | — | — | Never | None. The trade stays valid. |
| `TRADE_CANCELLED` | CRX refused or retracted the trade after the fill. CRX sends it on 8 150 = H. | — | — | — | Never | Remove the trade from the books. |
| `REFUSED` | The trade did not open. | — | — | 99 | Yes | Send a new R. |
| `CONFLICT` | The request conflicts with a rule, for example a quote on an RFQ of the maker's own firm. | 99 | 99 | 99 | No | Read Text. |
| Other code | Any other reject. | 99 | 99 | 99 | No | Read Text. |

End codes on QuoteStatusReport (AI) 297 = 7:

| Code | Cause |
|---|---|
| `QUOTE_EXPIRED` | The quote expired with no accept or no trade. |
| `QUOTE_LOST` | Legacy maker report, kept for replay. A current request ends without disclosure of another maker's award. |

### 9.5 BusinessMessageReject codes

| Code | 380 | Cause | Retry | Correction |
|---|---|---|---|---|
| `RATE_LIMITED` | 0 | The request exceeds a seat rate limit. 379 holds the request ID. | Yes | Wait for the time in Text. |
| `QUOTE_ACCEPTED` | 0 | A Z or a pass on an accepted quote. 45 and 379 name the message and its QuoteID or QuoteRespID; a Z answered after a wait has no 45. | Never | None. The trade stays valid. |
| `QUOTE_OTHER_SESSION` | 0 | A Z or a pass on a quote that another session of the seat holds. Text names that SenderCompID. | No | Send the message on that session. |
| `QUOTE_NOT_LIVE` | 0 | A Z on a quote that has ended, or a pass on a quote past 62, passed or expired. 45 and 379 name the message and the ID; a Z answered after a wait has no 45. | Never | None. |
| `DUPLICATE` | 0 | An ID is in use with other terms: QuoteReqID, QuoteID, QuoteRespID or ClOrdID. 45 and 379 name the message and the ID. The first request and its state do not change. | No | Send the request under a new ID. |
| `UNKNOWN_RFQ` | 1 | A decline (AG) on an RFQ that CRX did not send to the session. 379 holds the QuoteReqID. | No | Decline only an R that the session received. |
| A code of a refused decline | 0, 1 or 6 | CRX refused the decline, for example `QUOTE_WINDOW_CLOSED`. 380 = 6 when the seat is not authorized. | No | Read Text. |
| `UNSUPPORTED_MESSAGE` | 3 | CRX does not take this MsgType, for example NewOrderSingle (D). Or a drop-copy session sent an application message. | No | Accept a quote with QuoteResponse (AJ). Send no application message on a drop-copy session. |
| `SERVICE_UNAVAILABLE` | 4 | CRX cannot answer now, or it cannot record the answer to H or a. The session stays up. | Yes | Check the state with a, H or the REST API, then resend. After an AJ, send H before any new accept. |

An AJ with 694 = 1 gets `RATE_LIMITED` and `SERVICE_UNAVAILABLE` in 8 150 = 8, 103 = 99, not in j. Exception: an AJ that CRX cannot record gets j 380 = 4, code `SERVICE_UNAVAILABLE`, and no trade; H then answers `UNKNOWN_ORDER`.

### 9.6 Logout codes

| Code | Cause | Retry |
|---|---|---|
| `LOGON_BEGIN_STRING` | BeginString (8) is not `FIX.4.4`. | After a correction |
| `LOGON_COMP_ID_UNKNOWN` | CRX has no record of the SenderCompID, or TargetCompID is wrong for the role. | After a correction |
| `LOGON_ACCOUNT_MISMATCH` | Username (553) is not the seat of this SenderCompID. | After a correction |
| `LOGON_ADDRESS_INVALID` | CrxLoginKey (20012) is not `0x` and 40 hex characters. | After a correction |
| `LOGON_SIGNATURE_INVALID` | RawData (96) is malformed, or the signature does not match the signing address. | After a correction |
| `LOGON_TIME_INVALID` | SendingTime (52) is not valid. | After a correction |
| `LOGON_TIME_AHEAD` | SendingTime (52) is more than 5 seconds ahead of CRX time. | After a clock correction |
| `LOGON_IP_NOT_ALLOWED` | The source address is not on the allowlist of this SenderCompID. | After a correction |
| `LOGON_SESSION_ACTIVE` | The SenderCompID has a live session. | After the other session ends |
| `LOGON_HEART_BT_INT` | HeartBtInt (108) is outside 5 to 60. | After a correction |
| `LOGON_ENCRYPT_METHOD` | EncryptMethod (98) is not `0`. | After a correction |
| `LOGON_RESET_SEQ_NUM` | ResetSeqNumFlag (141) = Y with MsgSeqNum other than 1, or 141 is not Y or N. | After a correction |
| `SENDING_TIME_ACCURACY` | SendingTime (52) is more than 120 seconds from CRX time. | After a clock correction |
| `LOGON_SEQ_INVALID` | The Logon MsgSeqNum (34) is absent or not a valid number. | After a correction |
| `LOGON_RESET_WINDOW` | The Logon arrived during the daily reset. | From the time in Text |
| `SEQ_NUM_TOO_LOW` | MsgSeqNum is lower than expected, with no PossDupFlag. | After a correction |
| `SEQ_INVALID` | A message after the Logon has no valid MsgSeqNum (34). | After a correction |
| `BEGIN_STRING` | A message after the Logon has a BeginString (8) other than `FIX.4.4`. | After a correction |
| `MESSAGE_TOO_LARGE` | A message is longer than 8,192 bytes. | After a correction |
| `UNAUTHORIZED` | CRX rejected the Logon signature: no match, timestamp out of range, or reused. | Yes, with a new signature |
| `ACCOUNT_PAUSED` | Trading is paused for the account. | After CRX support confirms access. |
| `ELIGIBILITY_EXPIRED` | The account eligibility representation expired. | After renewal through CRX. |
| `NOT_WHITELISTED` | CRX did not approve the seat. | No. Contact CRX support. |
| `SEAT_CANNOT_SIGN` | The seat is a contract wallet. | No |
| A 20013 code | The signature proxy did not sign the Logon. | After a correction |
| `LOGON_RATE` | More than 5 Logons in 60 seconds for the SenderCompID. Text gives no wait time. | After 60 seconds |
| `RATE_LIMITED` | The seat is above a request limit at the Logon. | After the wait in Text |
| `SERVICE_UNAVAILABLE` | CRX cannot check the Logon now. | Yes, with the reconnect wait |
| `HEARTBEAT_TIMEOUT` | No message after a TestRequest. | Yes |
| `GAP_QUEUE_FULL` | More than 10,000 messages wait above a gap. | Yes, then fill the gap |
| `LOGON_ON_LIVE_SESSION` | A Logon arrived on a live session. | Yes |
| `COMP_ID_PROBLEM` | A message had a wrong CompID. | After a correction |
| `ERROR_RATE` | More than 50 rejects in 60 seconds. | After a correction |
| `LOGOUT_ACK` | The answer to a firm Logout. | Yes |
| `DAILY_RESET` | Daily reset at 17:00 New York time. | Yes, from 17:00:30 with MsgSeqNum 1 |
| `SESSION_RENEWAL` | The API session of the seat ends in 10 minutes. | Yes, after 5 seconds |
| `SESSION_EXPIRED` | The API session of the seat ended early, or the FIX session has none, for example after a CRX restart. | Yes, after 5 seconds |
| `GATEWAY_STOP` | CRX stops the FIX service. | Yes, with the reconnect wait |

Text examples:

```text
NO_QUOTE: No dealer quoted this request. (trace 1a15968acee00cd)
QUOTE_EXPIRED: The quote reached its ValidUntilTime with no accept. (trace 1a1596b1fe301df)
NOTIONAL_ABOVE_MAXIMUM: Maximum trade size is 100000000 USD. (trace 1a1596e99ba033b)
UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace 1a1596e51640336)
QUOTE_WINDOW_CLOSED: Too late to quote this request. (trace 1a15968c61700e4)
SEQ_NUM_TOO_LOW: MsgSeqNum too low, expecting 20 but received 17. (trace 1a1597091830019)
```

## 10. Trading rules

### 10.1 Markets

- USD/MXN, USD/BRL and USD/PHP. SecurityList (y) gives the live markets.
- CRX rejects a request for any other Symbol.
- A paused market is not in SecurityList. A request for it gets AG 658 = 2.

### 10.2 Quotes

- Every maker receives every RFQ, except RFQs from its own firm and RFQs its free collateral cannot cover.
- CRX sends no R after its ExpireTime (126).
- The R gives the taker's side; the maker prices that side only.
- Submit the quote by ExpireTime (126); CRX decides whether collection is still open. A late quote gets AI 297 = 5, code `QUOTE_WINDOW_CLOSED`. See [Timing](#58-timing).
- The taker receives one quote: the best rate for its side. On equal rates, the earlier quote wins.
- CRX does not select a quote that is too far from the market price.
- Quotes are binding, with no last look. The maker's signed quote is its signature on the trade: when the taker accepts, the trade opens, and the maker cannot decline it.
- A maker can cancel a quote with QuoteCancel (Z) only before a taker accepts it.
- A quote is for the full OrderQty; a trade fills all of it or none.

### 10.3 Settlement time

| Item | Rule |
|---|---|
| Earliest | 1 hour after the request |
| Latest | 90 days after the request |
| Market closures | CRX accepts a time in a market closure only if it can price that time, and rejects a time in the first 15 minutes after a reopen. `GET /markets?chain=ethereum` gives the next rejected period for each market. |
| Fixing | At CrxMaturityTime (20001), set by the taker. |
| Settlement date | UTC date of CrxMaturityTime, held in both MaturityDate (541) and SettlDate (64). |

Fixing source:

| Market | Fixing source |
|---|---|
| USD/MXN | Pyth Network spot price |
| USD/BRL | Pyth Network spot price |
| USD/PHP | Pyth Network spot price |

Each trade settles on the first Pyth Network spot price published in the hour after its settlement time. If none is published in that hour, CRX proposes a manual price, public for 2 hours before it is final.

### 10.4 Size and collateral

- Minimum notional: 100 USD. A maximum can apply, given in Text.
- Collateral: Circle USDC on the seat, on Ethereum (chain 1).
- CRX checks the free collateral of the taker at the request and at the accept.
- The margin rules of the REST API apply to each trade.

### 10.5 Rate limits

Limits apply per seat and are shared by FIX, REST and WebSocket. Rejected requests count.

| Group | FIX messages | Burst | Per minute |
|---|---|---|---|
| RFQ open | QuoteRequest (R) | 10 | 20. Also 120 across all seats. |
| Quote and accept | Quote (S), QuoteCancel (Z), QuoteResponse (AJ) 694 = 1, maker QuoteRequestReject (AG) | 120 | 600 |
| Trade feed and market list | SecurityListRequest (x), and the trade feed reads that CRX makes for the seat | 60 | 300 |
| No limit | QuoteStatusRequest (a), OrderStatusRequest (H), QuoteResponse (AJ) 694 = 6, session messages | — | — |

- While the seat has a live session, CRX reads its trade feed once per second; these 60 reads per minute count against the trade feed limit.
- A request above a limit gets j 380 = 0, code `RATE_LIMITED`. BusinessRejectRefID (379) holds the request ID. Text gives the limit and the wait.
- An AJ above a limit gets 8 150 = 8, 103 = 99, code `RATE_LIMITED`.
- CRX does not queue a request above a limit.
- CRX answers a and H from the seat's records, across its sessions. They use no limit.
- More than 50 rejects in 60 seconds end the session. See [Logout](#47-logout).
- Other per-firm limits can apply, such as on failed trades per hour. Text names the limit and the next valid time.

## 11. Onboarding and certification

### 11.1 Onboarding

1. Send CRX the seat address and, for an allowlist, the source IP addresses. CRX requires no other credential.
2. CRX approves the seat and sends the SenderCompID for each role, the host and port, the CRX contract address and the status page address.
3. Install the signature proxy and configure its back end.
4. Run the certification cases on production at 100 USD. Use the CRX test RFQ for the maker cases.
5. CRX reviews the logs and signs the report.
6. Go live.

### 11.2 Certification rules

- Finish the firm's own tests before certification.
- Run the session cases before the taker and maker cases.
- For each case, keep the FIX engine log and the signature proxy log.
- CRX signs one report per firm and software version, naming the FIX engine and signature proxy versions.
- A maker's first production quote is the off-market quote of case M02. CRX does not select it, and it expires.

Certify again when:

- The FIX engine or the signature proxy version changes.
- The back end changes, for example from a local key to a custodian.
- The firm adds a role: taker, maker or drop copy.
- CRX issues a breaking change.
- The session does not operate in production as this document specifies.
- The seat has no Logon for 90 days.

### 11.3 Summary

M = Mandatory. C = Conditional: required when the firm uses the feature.

| ID | Cat | Case | ID | Cat | Case |
|---|---|---|---|---|---|
| S01 | M | Logon | T01 | C | SecurityList |
| S02 | M | Logon, wrong seat | T02 | C | RFQ and quote |
| S03 | M | HeartBtInt out of range | T03 | C | Accept and fill |
| S04 | M | SendingTime out of range | T04 | C | Pass |
| S05 | M | Second Logon | T05 | C | Late accept |
| S06 | M | Heartbeat | T06 | C | Below minimum |
| S07 | M | TestRequest from the firm | T07 | C | Settlement time too soon |
| S08 | M | TestRequest from CRX | T08 | C | Unknown Symbol |
| S09 | M | Heartbeat timeout | T09 | C | OrderQty missing |
| S10 | M | ResendRequest, one message | T10 | C | Accept differs from the quote |
| S11 | M | ResendRequest, range | T11 | C | Repeat accept |
| S12 | M | ResendRequest, open end | T12 | C | Status requests |
| S13 | M | GapFill | T13 | C | NewOrderSingle |
| S14 | M | Firm MsgSeqNum too high | T14 | C | Rate limit |
| S15 | M | Firm MsgSeqNum too low | T15 | C | Disconnect after accept |
| S16 | M | Firm MsgSeqNum too low, PossDup | T16 | C | Too many decimal places |
| S17 | M | CRX MsgSeqNum too high | T17 | C | MaturityDate differs |
| S18 | M | CRX MsgSeqNum too low | T18 | C | Seat approval removed |
| S19 | M | SequenceReset-GapFill, bad NewSeqNo | T19 | C | CRX restart during an RFQ |
| S20 | M | SequenceReset-Reset, low NewSeqNo | T20 | C | Quote expires |
| S21 | M | Logout from the firm | M01 | C | Receive an RFQ |
| S22 | M | Logout from CRX and reconnect | M02 | C | Off-market quote expires |
| S23 | M | Disconnect and reconnect | M03 | C | Quote wins |
| S24 | M | Daily reset | M04 | C | Late quote |
| S25 | M | Logon with ResetSeqNumFlag | M05 | C | Cancel |
| S26 | M | Required tag missing | M06 | C | Cancel after accept |
| S27 | M | Empty tag | M07 | C | Disconnect after a quote |
| S28 | M | Error rate | M08 | C | Custodian sign time |
| P01 | M | Proxy domain check | M09 | C | Quote status |
| P02 | M | Proxy resend | M10 | C | Wrong side |
| P03 | M | CRX not available | M11 | C | Decline |
| D01 | C | Drop-copy fill | D02 | C | Drop-copy send |
| M12 | C | Quote terms differ from the R | | | |

### 11.4 Session cases

Precondition for all cases: the FIX engine connects through the signature proxy.

| ID | Steps | Expected from CRX |
|---|---|---|
| S01 | 1. Send A with 108 = 30. | A with 98 = 0 and 108 = 30. |
| S02 | 1. Send A with 553 = an address that is not the seat. | 5 with 20009 = `LOGON_ACCOUNT_MISMATCH`. The connection closes. |
| S03 | 1. Send A with 108 = 90. | 5 with 20009 = `LOGON_HEART_BT_INT`. |
| S04 | 1. Send A with 52 three minutes behind CRX time. | 5 with 20009 = `SENDING_TIME_ACCURACY`. |
| S05 | 1. Log on. 2. Log on again from a second connection with the same CompID. 3. Send 1 on the first session. | Step 2: 5 with 20009 = `LOGON_SESSION_ACTIVE`. Step 3: 0 with the same 112. |
| S06 | 1. Log on. 2. Send nothing but Heartbeats for 3 × HeartBtInt. | 0 each HeartBtInt. |
| S07 | 1. Send 1 with 112 = `T1`. | 0 with 112 = `T1`. |
| S08 | 1. Stop all messages for 1.2 × HeartBtInt. 2. Answer the TestRequest. | 1 with 112. The session continues. |
| S09 | 1. Stop all messages. Do not answer the TestRequest. | 1, then 5 with 20009 = `HEARTBEAT_TIMEOUT`. |
| S10 | 1. Send 2 with 7 = N and 16 = N for one application message. | The message again with 43 = Y and 122. |
| S11 | 1. Send 2 for a range of 5 messages. | Application messages with 43 = Y. Session messages as 4 with 123 = Y. |
| S12 | 1. Send 2 with 16 = 0. | All messages from 7 to the last one sent. |
| S13 | 1. Send 2 for a range that holds only session messages. | One 4 with 123 = Y and 36 = the end of the range + 1. |
| S14 | 1. Send an application message with 34 = expected + 5. 2. Answer the ResendRequest. | 2 with 7 = the expected number and 16 = 0. Then CRX processes the held message. |
| S15 | 1. Send a message with 34 = expected − 1, without 43. | 5 with 20009 = `SEQ_NUM_TOO_LOW`. Text gives both numbers. |
| S16 | 1. Send a message with 34 = expected − 1 and 43 = Y. | No answer. The session continues. |
| S17 | 1. Log out. 2. Set the expected inbound number of the engine 3 below the correct value. 3. Log on. | The engine sends 2. CRX sends again or gap-fills. |
| S18 | 1. Log out. 2. Set the expected inbound number of the engine 3 above the correct value. 3. Log on. | The engine finds a CRX message too low without 43 and sends 5. |
| S19 | 1. Send 4 with 123 = Y and 36 below its 34. | 3 with 373 = 5. |
| S20 | 1. Send 4 with 123 = N and 36 below the expected number. | 3 with 373 = 5. |
| S21 | 1. Send 5. | 5 with 20009 = `LOGOUT_ACK`. The connection closes. |
| S22 | 1. Ask CRX support for a renewal Logout. 2. Reconnect after 5 seconds. | 5 with 20009 = `SESSION_RENEWAL`. A after the reconnect. Sequence numbers continue. |
| S23 | 1. Close the TCP connection. 2. Reconnect after 5 seconds with 141 = N. | A. Each gap fills with 2 and the resend. |
| S24 | 1. Stay logged on through 17:00 New York time. 2. At 17:00:30, log on with 34 = 1 and 141 = Y. | 5 with 20009 = `DAILY_RESET`. A with 34 = 1 and 141 = Y. |
| S25 | 1. Send A with 141 = Y and 34 = 1. | A with 141 = Y and 34 = 1. |
| S26 | 1. Send R without 52. | 3 with 373 = 1 and 371 = 52. |
| S27 | 1. Send R with an empty 131. | 3 with 373 = 4. |
| S28 | 1. Send 51 R messages without 52 in 60 seconds. | 3 for each. After the 51st: 5 with 20009 = `ERROR_RATE`. |

### 11.5 Taker cases

Precondition: the seat has the taker role and at least 100 USD of free collateral.

| ID | Steps | Expected from CRX |
|---|---|---|
| T01 | 1. Send x with 559 = 4. | y with USD/MXN, USD/BRL and USD/PHP. Each has 167 = FXNDF, 15 = USD and 562 = 100. |
| T02 | 1. Send R: USD/MXN, 54 = 1, 38 = 100, 20001 = one day ahead. | AI 297 = 10 immediately. 5 to 20 seconds later: S with 537 = 1, 62 and 20008, or AG with 20009 = `NO_QUOTE`. |
| T03 | 1. Do T02. 2. Send AJ with 694 = 1 before 62. | 8 150 = A within 100 milliseconds. Then 8 150 = 0. Then 8 150 = F with 880, 75, 541, 64, 120 and 151 = 0. |
| T04 | 1. Do T02. 2. Send AJ with 694 = 6. | AI 297 = 11. |
| T05 | 1. Do T02. 2. Wait past 62. 3. Send AJ with 694 = 1. | 8 150 = 8, 103 = 4, 20009 = `QUOTE_EXPIRED`. |
| T06 | 1. Send R with 38 = 99. | AG 658 = 3, 20009 = `NOTIONAL_BELOW_MINIMUM`. |
| T07 | 1. Send R with 20001 = 30 minutes ahead. | AG 658 = 3, 20009 = `BAD_REQUEST`. Text gives the earliest time. |
| T08 | 1. Send R with 55 = `USD/XYZ`. | AG 658 = 1. |
| T09 | 1. Send R without 38. | AG with 20009 = `MISSING_FIELD`. |
| T10 | 1. Do T02. 2. Send AJ with 38 = 200. | 8 150 = 8, 20009 = `QUOTE_MISMATCH`. No trade. |
| T11 | 1. Do T03. 2. Send the same AJ again with 43 = Y. | The stored answer. No second trade. |
| T12 | 1. Do T03. 2. Send H for the ClOrdID. 3. Send a for the QuoteID. | 8 150 = I with the current state. AI with the current state. |
| T13 | 1. Send D. | j 380 = 3, 20009 = `UNSUPPORTED_MESSAGE`. |
| T14 | 1. Send 11 R messages in one second. | The 11th gets j 380 = 0, 20009 = `RATE_LIMITED`. |
| T15 | 1. Do T02. 2. Send AJ. 3. Close the TCP connection immediately. 4. Reconnect. 5. Send H. | 8 150 = A, 0 and F, by resend or after the Logon. 8 150 = I. |
| T16 | 1. Send R with 38 = 100.1234567. | AG with 20009 = `INVALID_QUANTITY`. |
| T17 | 1. Send R with 541 one day after the date of 20001. | AG with 20009 = `MATURITY_MISMATCH`. |
| T18 | 1. Ask CRX support to remove the approval of the seat. 2. Send R. 3. Ask CRX support to restore it. | AG 658 = 6, 20009 = `NOT_WHITELISTED`. |
| T19 | 1. Send R. 2. Ask CRX support to restart the CRX FIX service before the S. 3. Reconnect. 4. When no S or AG arrives by resend, send a or H. | After the Logon: the S or AG by resend, or the state by a. No second RFQ. |
| T20 | 1. Do T02. 2. Do not answer the S. | At 62: AI 297 = 7, 20009 = `QUOTE_EXPIRED`. |

### 11.6 Maker cases

Precondition: the seat has the maker role. CRX sends the CRX test RFQ at 100 USD.

| ID | Steps | Expected from CRX |
|---|---|---|
| M01 | 1. Log on. 2. Wait for the CRX test RFQ. | R with 131 = `0x`… and 54 = the taker's side. A maker test request carries 20014 = Y and 126 = 62; an ordinary RFQ normally carries 126 = 60 + 5 seconds. The R also has 20003 and 20004. |
| M02 | 1. Answer the test RFQ before 126 with a rate far from the market. | AI 297 = 0. At the quote end: AI 297 = 7 with 20009 = `QUOTE_EXPIRED`. No trade. |
| M03 | 1. Answer the next test RFQ before 126 at the market rate. | AI 297 = 0. Then 8 150 = F with 880. |
| M04 | 1. Answer a test RFQ after 126. | AI 297 = 5, 300 = 4, 20009 = `QUOTE_WINDOW_CLOSED`. |
| M05 | 1. Answer a test RFQ. 2. Send Z for the QuoteID before an accept. | AI 297 = 1. |
| M06 | 1. Answer a test RFQ. 2. Ask CRX support to accept it. 3. Send Z. | j 380 = 0, 20009 = `QUOTE_ACCEPTED`. Then 8 150 = F. |
| M07 | 1. Answer a test RFQ. 2. Log out. 3. CRX support accepts the quote. 4. Log on. | The trade fills. 8 150 = F after the Logon. |
| M08 | 1. With a custodian back end, answer 50 test RFQs. | The signature proxy log shows a 99th percentile time below 4.5 seconds, from TransactTime (60) to the S sent. |
| M09 | 1. Send a for an own QuoteID. | AI with the current state. |
| M10 | 1. Answer a test RFQ with 54 = 1 by BidPx. | AI 297 = 5, 300 = 99, 20009 = `WRONG_SIDE`. |
| M11 | 1. Answer a test RFQ with AG 658 = 8. | No answer. No quote from this maker on the RFQ. |
| M12 | 1. Answer a test RFQ with 38 = 200. | The signature proxy sends the S unsigned with 20013 = `TERMS_MISMATCH`. CRX answers AI 297 = 5, 300 = 99, 20009 = `TERMS_MISMATCH`. |

### 11.7 Proxy and drop-copy cases

| ID | Steps | Expected |
|---|---|---|
| P01 | 1. Set a wrong verifyingContract in the signature proxy. 2. Do T02. 3. Send AJ. | The signature proxy sends the AJ unsigned with 20013 = `TYPED_DATA_MISMATCH`. CRX answers 8 150 = 8 with 20009 = `TYPED_DATA_MISMATCH`. |
| P02 | 1. Do T03. 2. Send the AJ again with 43 = Y. | The signature proxy log shows one signature only for the AJ. |
| P03 | 1. Ask CRX support to stop the trading service. 2. Send R. | j 380 = 4, 20009 = `SERVICE_UNAVAILABLE`. The session stays up. |
| D01 | 1. Log on the drop-copy CompID with 56 = `CRX-DC`. 2. Trade on FIX or REST. | 8 150 = F for the trade. |
| D02 | 1. Send R on the drop-copy session. | j 380 = 3, 20009 = `UNSUPPORTED_MESSAGE`. |

## 12. Raw examples

`|` stands for SOH (0x01). BodyLength (9) and CheckSum (10) are correct. Select a sample's file name to download it.

- The samples come from a CRX test session with CompIDs `MKR1` (maker) and `TKR1` (taker).
- The keys are unfunded test keys, and verifyingContract is a test value. Use the CRX contract address provided at onboarding.
- Samples 11, 12, 36 and 62 show the CRX format and do not come from the test session.
- The test session ran before tags 20014 to 20017: sample 02 has no CrxLoginChain (20017), and samples 22 and 28 have no CrxSpotTime (20016).

### 12.1 Session

Logon from the FIX engine ([`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix)):

```text
8=FIX.4.4|9=72|35=A|34=1|49=TKR1|52=20261021-05:25:47.534|56=CRX-TRD|98=0|108=30|141=Y|10=083|
```

Logon as CRX receives it, after the signature proxy ([`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix)):

```text
8=FIX.4.4|9=262|35=A|34=1|49=TKR1|52=20261021-05:25:47.534|56=CRX-TRD|98=0|108=30|141=Y|553=0xd4916d52ff44110267b24151e94cce2b32d176b3|95=132|96=0xeb35008c6d30141663d447f61647c6aa27995c4538ed4f813b1c1b67d292e0553508863b675dea9f0e33d0b5fe83bae999d803d136170ef9865b95d2a55229281c|10=203|
```

Logon answer ([`03-logon-answer.fix`](examples/03-logon-answer.fix)):

```text
8=FIX.4.4|9=72|35=A|49=CRX-TRD|56=TKR1|34=1|52=20261021-05:25:47.592|98=0|108=30|141=Y|10=087|
```

Rejected Logon ([`04-logon-rejected.fix`](examples/04-logon-rejected.fix)):

```text
8=FIX.4.4|9=155|35=5|49=CRX-TRD|56=TKR1|34=1|52=20261021-05:33:39.403|58=LOGON_BEGIN_STRING: BeginString must be FIX.4.4. (trace 1a15cf36ccb0017)|20009=LOGON_BEGIN_STRING|10=061|
```

Heartbeat and TestRequest ([`05-heartbeat.fix`](examples/05-heartbeat.fix), [`06-test-request.fix`](examples/06-test-request.fix), [`07-heartbeat-answer.fix`](examples/07-heartbeat-answer.fix)):

```text
8=FIX.4.4|9=54|35=0|34=4|49=TKR1|52=20261021-05:27:15.546|56=CRX-TRD|10=255|
8=FIX.4.4|9=63|35=1|49=TKR1|56=CRX-TRD|34=3|52=20261021-05:33:50.953|112=TR-1|10=211|
8=FIX.4.4|9=63|35=0|49=CRX-TRD|56=TKR1|34=2|52=20261021-05:33:50.958|112=TR-1|10=214|
```

ResendRequest and GapFill ([`08-resend-request.fix`](examples/08-resend-request.fix), [`09-gap-fill.fix`](examples/09-gap-fill.fix)):

```text
8=FIX.4.4|9=63|35=2|49=TKR1|56=CRX-TRD|34=6|52=20261021-05:33:51.034|7=3|16=3|10=120|
8=FIX.4.4|9=97|35=4|49=TKR1|56=CRX-TRD|34=9|43=Y|52=20261021-05:33:51.048|122=20261021-05:33:51.048|123=Y|36=12|10=059|
```

Session Reject ([`10-session-reject.fix`](examples/10-session-reject.fix)):

```text
8=FIX.4.4|9=148|35=3|49=CRX-TRD|56=TKR1|34=8|52=20261021-05:33:51.078|45=19|371=112|372=1|373=4|58=TAG_WITHOUT_VALUE: Tag 112 has no value. (trace 1a15cf39a630019)|10=020|
```

Renewal and daily reset ([`11-logout-renewal.fix`](examples/11-logout-renewal.fix), [`12-logout-daily.fix`](examples/12-logout-daily.fix)):

```text
8=FIX.4.4|9=175|35=5|49=CRX-TRD|56=TKR1|34=41|52=20261020-20:52:27.464|58=SESSION_RENEWAL: The session ends for signature renewal. Log on again. (trace 1a159a0c3b10412)|20009=SESSION_RENEWAL|10=072|
8=FIX.4.4|9=190|35=5|49=CRX-TRD|56=TKR1|34=52|52=20261020-21:00:00.002|58=DAILY_RESET: The session ends for the daily reset. Log on from 17:00:30 America/New_York. (trace 1a159a8e2c00431)|20009=DAILY_RESET|10=055|
```

### 12.2 Taker

QuoteRequest and Pending ([`20-quote-request.fix`](examples/20-quote-request.fix), [`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix)):

```text
8=FIX.4.4|9=212|35=R|34=3|49=TKR1|52=20261021-05:25:47.617|56=CRX-TRD|131=TKR1-R-1792560347616-2|146=1|55=USD/MXN|167=FXNDF|541=20261021|537=1|54=1|38=1000|64=20261021|15=USD|60=20261021-05:25:47.616|20001=20261021-07:25:00.000|10=166|
8=FIX.4.4|9=152|35=AI|49=CRX-TRD|56=TKR1|34=2|52=20261021-05:25:47.610|131=TKR1-R-1792560347616-2|117=TKR1-R-1792560347616-2|55=USD/MXN|60=20261021-05:25:47.606|297=10|10=162|
```

Quote to the taker ([`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix)); the file holds the full message. Decoded CrxTypedData (20008) `message`:

```json
{
 "maturity": "1792567500",
 "notionalE6": "1000000000",
 "ownLegId": "0x016639309c03504ca0bd862bbde1ba87fa19bf516a3b0ed7000000006ad84f15",
 "ownNonce": "1792560352882",
 "ownSalt": "0x41b750c5459eb7eee9c8ad9efe9ba314ff5dfa33a394867a19fbb43e16f884b9",
 "pair": "USD/MXN",
 "pairC": "0x5d06630f4ca6ad8b9afa053ea271147fa9f73e7095d6b6c848e12b5138127782",
 "premiumBps": "0",
 "rateE6": "18500000",
 "side": "buy",
 "summary": "buy 1 000 USD vs MXN at 18.5 MXN per USD, matures 2026-10-21T07:25:00Z, upfront none"
}
```

Rejected request, unknown Symbol ([`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix)):

```text
8=FIX.4.4|9=237|35=AG|49=CRX-TRD|56=TKR1|34=4|52=20261021-05:31:22.612|131=TKR1-R-1792560682596-2|658=1|146=1|55=USD/XXX|58=UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace 1a15cf156590349)|20009=UNKNOWN_SYMBOL|10=065|
```

Accept from the FIX engine, and as CRX receives it ([`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix), [`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix)):

```text
8=FIX.4.4|9=278|35=AJ|34=4|49=TKR1|52=20261021-05:25:52.921|56=CRX-TRD|11=TKR1-O-1792560352921-4|38=1000|44=18.5|54=1|55=USD/MXN|60=20261021-05:25:52.921|64=20261021|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|167=FXNDF|541=20261021|693=TKR1-QR-1792560352921-3|694=1|10=096|
8=FIX.4.4|9=417|35=AJ|34=4|49=TKR1|52=20261021-05:25:52.921|56=CRX-TRD|11=TKR1-O-1792560352921-4|38=1000|44=18.5|54=1|55=USD/MXN|60=20261021-05:25:52.921|64=20261021|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|167=FXNDF|541=20261021|693=TKR1-QR-1792560352921-3|694=1|20007=0xecbc3ca2310ab29be6f8b97d57850e7a2459bc286c395891d41acf7517493fbd60703cac4afface929bbe5796a2e3421bc39c6f5db8db723facc17cb360718661b|10=205|
```

Pending New, New and fill ([`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix), [`27-exec-new.fix`](examples/27-exec-new.fix), [`28-exec-fill.fix`](examples/28-exec-fill.fix)):

```text
8=FIX.4.4|9=389|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261021-05:25:52.919|37=NONE|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000001|150=A|39=A|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=1000|14=0|6=0|60=20261021-05:25:52.914|120=USD|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|20001=20261021-07:25:00.000|20002=0|10=074|
8=FIX.4.4|9=389|35=8|49=CRX-TRD|56=TKR1|34=6|52=20261021-05:25:52.971|37=NONE|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000002|150=0|39=0|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=1000|14=0|6=0|60=20261021-05:25:52.967|120=USD|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|20001=20261021-07:25:00.000|20002=0|10=048|
8=FIX.4.4|9=559|35=8|49=CRX-TRD|56=TKR1|34=7|52=20261021-05:25:55.179|37=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000003|150=F|39=2|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261021|60=20261021-05:25:55.169|120=USD|851=2|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|880=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|20001=20261021-07:25:00.000|20002=0|10=007|
```

Late accept ([`29-exec-rejected.fix`](examples/29-exec-rejected.fix)):

```text
8=FIX.4.4|9=512|35=8|49=CRX-TRD|56=TKR1|34=9|52=20261021-05:28:46.098|37=NONE|11=TKR1-O-1792560526099-4|693=TKR1-QR-1792560526099-3|17=X20261021-TKR1-1792560347546000021|150=8|39=8|103=4|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=0|14=0|6=0|60=20261021-05:28:46.092|120=USD|58=QUOTE_EXPIRED: The accept arrived after the ValidUntilTime of the quote. (trace 1a15ceef30b01e8)|117=0x93fa2894f5a98181c94512d248099e1cf93284194643fcb51ccf4c570d68b65a|20001=20261021-07:26:00.000|20002=0|20009=QUOTE_EXPIRED|10=194|
```

Pass ([`30-quote-response-pass.fix`](examples/30-quote-response-pass.fix), [`31-quote-status-pass.fix`](examples/31-quote-status-pass.fix)):

```text
8=FIX.4.4|9=252|35=AJ|34=4|49=TKR1|52=20261021-05:29:06.483|56=CRX-TRD|38=1000|44=18.5|54=1|55=USD/MXN|60=20261021-05:29:06.483|64=20261021|117=0x6c4f5fc71457092629f8153c8af9624fe1e84fccf782d727f9ce51df2451a0b5|167=FXNDF|541=20261021|693=TKR1-QR-1792560546483-3|694=6|10=205|
8=FIX.4.4|9=224|35=AI|49=CRX-TRD|56=TKR1|34=5|52=20261021-05:29:06.475|131=TKR1-R-1792560541182-2|117=0x6c4f5fc71457092629f8153c8af9624fe1e84fccf782d727f9ce51df2451a0b5|693=TKR1-QR-1792560546483-3|55=USD/MXN|60=20261021-05:29:06.471|297=11|10=246|
```

Quote expires with no accept ([`32-quote-status-expired.fix`](examples/32-quote-status-expired.fix)):

```text
8=FIX.4.4|9=310|35=AI|49=CRX-TRD|56=TKR1|34=8|52=20261021-05:28:44.872|131=TKR1-R-1792560404594-2|117=0x93fa2894f5a98181c94512d248099e1cf93284194643fcb51ccf4c570d68b65a|55=USD/MXN|60=20261021-05:28:44.863|297=7|58=QUOTE_EXPIRED: The quote reached its ValidUntilTime with no accept. (trace 1a15ceeee3f01e5)|20009=QUOTE_EXPIRED|10=117|
```

Order status ([`33-order-status-request.fix`](examples/33-order-status-request.fix), [`34-exec-status.fix`](examples/34-exec-status.fix)):

```text
8=FIX.4.4|9=96|35=H|34=5|49=TKR1|52=20261021-05:25:55.199|56=CRX-TRD|11=TKR1-O-1792560352921-4|54=1|55=USD/MXN|10=034|
8=FIX.4.4|9=553|35=8|49=CRX-TRD|56=TKR1|34=8|52=20261021-05:25:55.187|37=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|11=TKR1-O-1792560352921-4|693=TKR1-QR-1792560352921-3|17=X20261021-TKR1-1792560347546000004|150=I|39=2|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261021|60=20261021-05:25:55.187|120=USD|117=0xcb9900c1e1b66e52f251e2c866564c477f5d7ccf81246165e07865458c0ee524|880=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|20001=20261021-07:25:00.000|20002=0|10=247|
```

NewOrderSingle rejected, and a rate limit ([`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix), [`36-rate-limited.fix`](examples/36-rate-limited.fix)):

```text
8=FIX.4.4|9=185|35=j|49=CRX-TRD|56=TKR1|34=2|52=20261021-05:32:36.834|45=2|372=D|380=3|58=UNSUPPORTED_MESSAGE: Accept a quote with QuoteResponse (AJ). (trace 1a15cf2786203fb)|20009=UNSUPPORTED_MESSAGE|10=125|
8=FIX.4.4|9=200|35=j|49=CRX-TRD|56=TKR1|34=14|52=20261020-13:20:01.010|372=R|379=TKR1-R-1792502401004-21|380=0|58=RATE_LIMITED: The limit is 20 requests a minute. Wait 3 s. (trace 1a15977f0d10402)|20009=RATE_LIMITED|10=182|
```

Accept that the signature proxy did not sign, and the CRX answer ([`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix), [`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix)):

```text
8=FIX.4.4|9=298|35=AJ|34=4|49=TKR1|52=20261021-05:28:56.260|56=CRX-TRD|11=TKR1-O-1792560536260-4|38=1000|44=1.0|54=1|55=USD/MXN|60=20261021-05:28:56.260|64=20261021|117=0xd01b3b6ec15b60edc12272a106f91df8601bc79294d3cf723ab9e946dfd18423|167=FXNDF|541=20261021|693=TKR1-QR-1792560536260-3|694=1|20013=TERMS_MISMATCH|10=112|
8=FIX.4.4|9=546|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261021-05:28:56.254|37=NONE|11=TKR1-O-1792560536260-4|693=TKR1-QR-1792560536260-3|17=X20261021-TKR1-1792560347546000022|150=8|39=8|103=99|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|15=USD|151=0|14=0|6=0|60=20261021-05:28:56.248|120=USD|58=TERMS_MISMATCH: The signature proxy did not sign the accept. Send a new QuoteResponse after a new Quote. (trace 1a15cef1ab80203)|117=0xd01b3b6ec15b60edc12272a106f91df8601bc79294d3cf723ab9e946dfd18423|20001=20261021-07:28:00.000|20002=0|20009=TERMS_MISMATCH|10=234|
```

Security list ([`39-security-list-request.fix`](examples/39-security-list-request.fix), [`40-security-list.fix`](examples/40-security-list.fix)):

```text
8=FIX.4.4|9=88|35=x|34=2|49=TKR1|52=20261021-05:25:47.615|56=CRX-TRD|320=TKR1-SL-1792560347613-1|559=4|10=083|
8=FIX.4.4|9=222|35=y|49=CRX-TRD|56=TKR1|34=3|52=20261021-05:25:47.631|320=TKR1-SL-1792560347613-1|322=1a15cec39d20009|560=0|146=3|55=USD/BRL|167=FXNDF|15=USD|562=100|55=USD/MXN|167=FXNDF|15=USD|562=100|55=USD/PHP|167=FXNDF|15=USD|562=100|10=042|
```

### 12.3 Maker

QuoteRequest to the maker ([`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix)):

```text
8=FIX.4.4|9=406|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261021-05:25:47.973|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|146=1|55=USD/MXN|167=FXNDF|541=20261021|54=1|38=1000|64=20261021|15=USD|62=20261021-05:27:47.622|126=20261021-05:25:52.622|60=20261021-05:25:47.622|20001=20261021-07:25:00.000|20002=0|20003=0x113d551ab20a5fa350ea92e1e777267ce9fb3d8609da18612fc8e7d561c5a8dd|20004=20261021-05:35:17|10=154|
```

Quote from the FIX engine, and as CRX receives it ([`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix), [`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix)):

```text
8=FIX.4.4|9=290|35=S|34=2|49=MKR1|52=20261021-05:25:47.998|56=CRX-TRD|15=USD|38=1000|54=1|55=USD/MXN|62=20261021-05:35:17|64=20261021|117=MKR1-Q-1792560347995-1|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|133=18.5|167=FXNDF|537=1|541=20261021|20001=20261021-07:25:00.000|20002=0|10=050|
8=FIX.4.4|9=575|35=S|34=2|49=MKR1|52=20261021-05:25:47.998|56=CRX-TRD|15=USD|38=1000|54=1|55=USD/MXN|62=20261021-05:35:17|64=20261021|117=MKR1-Q-1792560347995-1|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|133=18.5|167=FXNDF|537=1|541=20261021|20001=20261021-07:25:00.000|20002=0|20005=0x28d6a72865294b3ea639963477370c11ac53adf6f1dea3bf000000006ad84f15|20006=0xa4fdd26c0a73db8432ca601c8319fe00979eda742ce143faa307b5fe17151508|20007=0xdc58e7b339f4f025ff9a9338b20a3802cb343450032412890be6adcbc1bd241127e8af9032f1f43ec087fcda39cc727de766cb7a94a2047399c7f4a41c5a3b3e1c|10=116|
```

Quote live and late quote ([`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix), [`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix)):

```text
8=FIX.4.4|9=195|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261021-05:25:48.014|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|117=MKR1-Q-1792560347995-1|55=USD/MXN|60=20261021-05:25:48.009|297=0|10=021|
8=FIX.4.4|9=307|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261021-05:26:39.338|131=0x6cdc62e9de360acbf1e35111a3c6d5fa74d5685d72a1b3f65d5e8edf419d608f|117=MKR1-Q-1792560399326-1|55=USD/MXN|60=20261021-05:26:39.332|297=5|58=QUOTE_WINDOW_CLOSED: Too late to quote this request. (trace 1a15ced03d800e4)|300=4|20009=QUOTE_WINDOW_CLOSED|10=195|
```

Unsigned quote, its answer, and the answer to an early ValidUntilTime ([`63-quote-unsigned.fix`](examples/63-quote-unsigned.fix), [`64-quote-status-unsigned.fix`](examples/64-quote-status-unsigned.fix), [`65-quote-status-life.fix`](examples/65-quote-status-life.fix)):

```text
8=FIX.4.4|9=311|35=S|34=3|49=MKR1|52=20261021-05:32:08.645|56=CRX-TRD|15=USD|38=2000|54=1|55=USD/MXN|62=20261021-05:41:38|64=20261021|117=MKR1-Q-1792560728639-1|131=0xed0bf4cceb58b7750d779966a42b300192e2f6f757020737b634af74f14c5128|133=18.5|167=FXNDF|537=1|541=20261021|20001=20261021-07:31:00.000|20002=0|20013=TERMS_MISMATCH|10=132|
8=FIX.4.4|9=356|35=AI|49=CRX-TRD|56=MKR1|34=4|52=20261021-05:32:08.636|131=0xed0bf4cceb58b7750d779966a42b300192e2f6f757020737b634af74f14c5128|117=MKR1-Q-1792560728639-1|55=USD/MXN|60=20261021-05:32:08.632|297=5|58=TERMS_MISMATCH: The signature proxy did not sign the quote. Correct the quote terms and send a new Quote. (trace 1a15cf20a3703ba)|300=99|20009=TERMS_MISMATCH|10=249|
8=FIX.4.4|9=366|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261021-05:32:19.296|131=0x6a509b2b129e38cd060ff6f9fce176e06c4b3f10dbc92f905ca131b58cceb5d7|117=MKR1-Q-1792560739301-1|55=USD/MXN|60=20261021-05:32:19.291|297=5|58=QUOTE_LIFE_TOO_LONG: The signature proxy did not sign the quote. Correct the quote terms and send a new Quote. (trace 1a15cf233db03d2)|300=99|20009=QUOTE_LIFE_TOO_LONG|10=196|
```

Maker fill ([`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix)):

```text
8=FIX.4.4|9=487|35=8|49=CRX-TRD|56=MKR1|34=6|52=20261021-05:25:55.055|37=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|11=MKR1-Q-1792560347995-1|17=X20261021-MKR1-1792560344893000002|150=F|39=2|64=20261021|55=USD/MXN|167=FXNDF|541=20261021|54=2|38=1000|15=USD|32=1000|31=18.5|151=0|14=1000|6=18.5|75=20261021|60=20261021-05:25:55.047|120=USD|851=1|117=MKR1-Q-1792560347995-1|880=0x20faeb8c2cd79db68a0d620cdb06938e73d4535e49b42ac2fcfcb1040b86e156|20001=20261021-07:25:00.000|20002=0|10=122|
```

Cancel ([`56-quote-cancel.fix`](examples/56-quote-cancel.fix), [`57-quote-status-canceled.fix`](examples/57-quote-status-canceled.fix)):

```text
8=FIX.4.4|9=158|35=Z|34=4|49=MKR1|52=20261021-05:32:29.556|56=CRX-TRD|117=MKR1-Q-1792560749516-1|131=0x03aad3e0a0a2daa705a4364ca2f5637e85340fce902318300b883ccaeacd5ec9|298=5|10=125|
8=FIX.4.4|9=195|35=AI|49=CRX-TRD|56=MKR1|34=5|52=20261021-05:32:29.571|131=0x03aad3e0a0a2daa705a4364ca2f5637e85340fce902318300b883ccaeacd5ec9|117=MKR1-Q-1792560749516-1|55=USD/MXN|60=20261021-05:32:29.563|297=1|10=049|
```

Quote expires ([`58-quote-status-expired.fix`](examples/58-quote-status-expired.fix)):

```text
8=FIX.4.4|9=290|35=AI|49=CRX-TRD|56=MKR1|34=8|52=20261021-05:30:51.222|131=0x52f4d13215a756d0717d6b37c9424974dc06fe68f1fa5b49414827d027ba2db5|117=MKR1-Q-1792560531373-1|55=USD/MXN|60=20261021-05:30:51.213|297=7|58=QUOTE_EXPIRED: The quote ended without a trade. (trace 1a15cf0dbc302f2)|20009=QUOTE_EXPIRED|10=174|
```

Decline ([`59-maker-decline.fix`](examples/59-maker-decline.fix)):

```text
8=FIX.4.4|9=150|35=AG|34=2|49=MKR1|52=20261021-05:31:07.218|56=CRX-TRD|131=0x62d14c21e5b43b0ff31ad9d6c666d324d27e3cb7a340aeab3bfa5408def10306|658=10|146=1|55=USD/MXN|10=222|
```

Quote status ([`60-quote-status-request.fix`](examples/60-quote-status-request.fix), [`61-quote-status-answer.fix`](examples/61-quote-status-answer.fix)):

```text
8=FIX.4.4|9=120|35=a|34=3|49=MKR1|52=20261021-05:25:48.038|56=CRX-TRD|55=USD/MXN|117=MKR1-Q-1792560347995-1|649=MKR1-QS-1792560348038-2|10=183|
8=FIX.4.4|9=223|35=AI|49=CRX-TRD|56=MKR1|34=4|52=20261021-05:25:48.024|649=MKR1-QS-1792560348038-2|131=0x06d7743d0dfb37ae27b80b0fd7f2af13f6160d22d3598b3f2e50db1f4cd3824c|117=MKR1-Q-1792560347995-1|55=USD/MXN|60=20261021-05:25:48.024|297=0|10=013|
```

CRX not available ([`62-business-reject.fix`](examples/62-business-reject.fix)):

```text
8=FIX.4.4|9=198|35=j|49=CRX-TRD|56=MKR1|34=16|52=20261020-13:21:00.010|372=S|379=MKR1-Q-1792502459998-7|380=4|58=SERVICE_UNAVAILABLE: The service is not available. (trace 1a15978d7e20410)|20009=SERVICE_UNAVAILABLE|10=168|
```

## 13. Dictionary

- CRX publishes the QuickFIX data dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) with this document.
- It is the FIX 4.4 dictionary with the CRX custom tags, groups and values in this document.
- Load it in the FIX engine with `UseDataDictionary=Y`.
- It gives the field order in each message and group. Report any difference from this document to CRX support.
