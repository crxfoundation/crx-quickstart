# CRX FIX 4.4 Rules of Engagement

| Item | Value |
|---|---|
| Version | 2.0.1 |
| Issue date | 2026-10-26 |
| Readers | FIX developers and FIX operators of a taker or maker firm |

Connect a FIX 4.4 engine to CRX to trade FX non-deliverable forwards that settle in Circle USDC. The wire is FIX 4.4 with the FIX Latest extensions in [section 8](#8-custom-tags) (EP312).

Requirements:

1. A seat address that CRX approved. See [Onboarding](#111-onboarding).
2. The CRX dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) in the FIX engine. See [Dictionary](#13-dictionary).
3. The signature proxy on the firm's host. See [Signature proxy](#5-signature-proxy).
4. A local key, or a Fireblocks or Fordefi vault, that signs for the seat. See [Key back ends](#55-key-back-ends).
5. Circle USDC collateral on the seat. See [Trading rules](#10-trading-rules).

## Contents

1. [Document control](#1-document-control)
2. [Scope](#2-scope)
   - [2.1 Service](#21-service)
   - [2.2 Session roles](#22-session-roles)
   - [2.3 Not on FIX](#23-not-on-fix)
   - [2.4 Terms](#24-terms)
   - [2.5 References](#25-references)
3. [Connectivity](#3-connectivity)
   - [3.1 Network path](#31-network-path)
   - [3.2 CompIDs](#32-compids)
   - [3.3 Reconnect](#33-reconnect)
   - [3.4 Engine settings](#34-engine-settings)
4. [Session](#4-session)
   - [4.1 Logon](#41-logon)
      - [4.1.1 Logon signature](#411-logon-signature)
   - [4.2 Message format](#42-message-format)
   - [4.3 Heartbeat and TestRequest](#43-heartbeat-and-testrequest)
   - [4.4 Sequence numbers](#44-sequence-numbers)
   - [4.5 Resend](#45-resend)
   - [4.6 SequenceReset](#46-sequencereset)
   - [4.7 Logout](#47-logout)
   - [4.8 Schedule](#48-schedule)
   - [4.9 Disconnect and recovery](#49-disconnect-and-recovery)
   - [4.10 IDs and repeats](#410-ids-and-repeats)
   - [4.11 Encodings](#411-encodings)
5. [Signature proxy](#5-signature-proxy)
   - [5.1 Function](#51-function)
   - [5.2 Tags the signature proxy adds and removes](#52-tags-the-signature-proxy-adds-and-removes)
   - [5.3 Maker quote signature](#53-maker-quote-signature)
   - [5.4 Taker accept signature](#54-taker-accept-signature)
   - [5.5 Key back ends](#55-key-back-ends)
   - [5.6 Unsigned messages](#56-unsigned-messages)
   - [5.7 Seat address](#57-seat-address)
   - [5.8 Timing](#58-timing)
   - [5.9 Resend and logs](#59-resend-and-logs)
   - [5.10 Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx)
6. [Message flows](#6-message-flows)
   - [6.1 Steps](#61-steps)
   - [6.2 RFQ and quote](#62-rfq-and-quote)
   - [6.3 Accept](#63-accept)
   - [6.4 Pass](#64-pass)
   - [6.5 Expiry](#65-expiry)
   - [6.6 No quote and decline](#66-no-quote-and-decline)
   - [6.7 Cancel](#67-cancel)
   - [6.8 States](#68-states)
   - [6.9 Races](#69-races)
7. [Messages](#7-messages)
   - [7.1 Header and trailer](#71-header-and-trailer)
   - [7.2 Logon (A)](#72-logon-a)
   - [7.3 Logout (5)](#73-logout-5)
   - [7.4 Heartbeat (0), TestRequest (1), ResendRequest (2), SequenceReset (4)](#74-heartbeat-0-testrequest-1-resendrequest-2-sequencereset-4)
   - [7.5 Reject (3)](#75-reject-3)
   - [7.6 QuoteRequest (R), taker to CRX](#76-quoterequest-r-taker-to-crx)
   - [7.7 QuoteStatusReport (AI), CRX to taker](#77-quotestatusreport-ai-crx-to-taker)
   - [7.8 Quote (S), CRX to taker](#78-quote-s-crx-to-taker)
   - [7.9 QuoteRequestReject (AG), CRX to taker](#79-quoterequestreject-ag-crx-to-taker)
   - [7.10 QuoteResponse (AJ), taker to CRX](#710-quoteresponse-aj-taker-to-crx)
   - [7.11 ExecutionReport (8), CRX to firm](#711-executionreport-8-crx-to-firm)
   - [7.12 OrderStatusRequest (H), firm to CRX](#712-orderstatusrequest-h-firm-to-crx)
   - [7.13 QuoteRequest (R), CRX to maker](#713-quoterequest-r-crx-to-maker)
   - [7.14 Quote (S), maker to CRX](#714-quote-s-maker-to-crx)
   - [7.15 QuoteRequestReject (AG), maker to CRX](#715-quoterequestreject-ag-maker-to-crx)
   - [7.16 QuoteStatusReport (AI), CRX to maker](#716-quotestatusreport-ai-crx-to-maker)
   - [7.17 QuoteCancel (Z), maker to CRX](#717-quotecancel-z-maker-to-crx)
   - [7.18 QuoteStatusRequest (a), firm to CRX](#718-quotestatusrequest-a-firm-to-crx)
   - [7.19 SecurityListRequest (x) and SecurityList (y)](#719-securitylistrequest-x-and-securitylist-y)
   - [7.20 BusinessMessageReject (j), CRX to firm](#720-businessmessagereject-j-crx-to-firm)
8. [Custom tags](#8-custom-tags)
9. [Rejects and codes](#9-rejects-and-codes)
   - [9.1 Which message rejects](#91-which-message-rejects)
   - [9.2 Text format](#92-text-format)
   - [9.3 Session Reject values](#93-session-reject-values)
   - [9.4 Business reject codes](#94-business-reject-codes)
   - [9.5 BusinessMessageReject codes](#95-businessmessagereject-codes)
   - [9.6 Logout codes](#96-logout-codes)
10. [Trading rules](#10-trading-rules)
   - [10.1 Markets](#101-markets)
   - [10.2 Quotes](#102-quotes)
   - [10.3 Settlement time](#103-settlement-time)
   - [10.4 Size and collateral](#104-size-and-collateral)
   - [10.5 Rate limits](#105-rate-limits)
11. [Onboarding and certification](#11-onboarding-and-certification)
   - [11.1 Onboarding](#111-onboarding)
   - [11.2 Certification rules](#112-certification-rules)
   - [11.3 Summary](#113-summary)
   - [11.4 Session cases](#114-session-cases)
   - [11.5 Taker cases](#115-taker-cases)
   - [11.6 Maker cases](#116-maker-cases)
   - [11.7 Proxy and drop-copy cases](#117-proxy-and-drop-copy-cases)
   - [11.8 Support](#118-support)
12. [Raw examples](#12-raw-examples)
   - [12.1 Session](#121-session)
   - [12.2 Taker](#122-taker)
   - [12.3 Maker](#123-maker)
13. [Dictionary](#13-dictionary)
14. [Legal notice](#14-legal-notice)

## 1. Document control

| Version | Issue date | Sections | Change |
|---|---|---|---|
| 1.0 | 2026-10-20 | All | First issue. |
| 1.1 | 2026-10-24 | 2, 5–7, 9–10 | Quote withdrawals, optional test-request fields and current account checks. Version 1.0 engines remain compatible. No withdrawal date. |
| 1.2 | 2026-10-24 | 3, 4, 7–9 | Limits for each source address: 8 connections without an accepted Logon, and 120 new connections in 60 s. `LOGON_RATE` counts only accepted Logons. CrxMaturityTime (20001) is UTC to the second. CRX refuses decimals in the seconds. Version 1.1 engines that send 20001 to the second remain compatible. No withdrawal date. |
| 2.0 | 2026-10-25 | All | Breaking change: standard FIX fields. The FIX engine sends and receives no custom tag. One custom tag remains, CrxSignature (20007), from the signature proxy to CRX. Tags 20001 to 20006 and 20008 to 20017 go. The settlement time is in MaturityDate (541) and MaturityTime (1079). The upfront premium is in UpfrontPriceType (1741) and UpfrontPrice (1742). RawData (96) holds the signature data on the R to a maker and on the S to a taker. RawDataLength (95) gives its length. The signature proxy removes both tags. Every ID that CRX assigns in 131, 117, 37, 880 and 17 is a UUID of 36 characters. SecondaryExecID (527) carries the 66-character on-chain trade hash. Username (553) is the address that signs the Logon. The Logon signature text has 9 lines. Signatures are base64. The reject code is the first token of Text (58). CRX uses a closed set of codes. Text (58) has at most 256 characters. R and AJ must carry SecurityType (167) = `FXNDF`. SecurityList (y) gives MinPriceIncrement (969). The Logon takes ApplicationSystemName (1603), ApplicationSystemVersion (1604) and ApplicationSystemVendor (1605). CRX reads Account (1) on R, S and AJ only. A second Quote (S) on one R and leg replaces the first. The Logon answer gives MaxMessageSize (383). A fill gives CalculatedCcyLastQty (1056), and it has the same ExecID (17) on order entry and drop copy. A firm ID with `=` or `|` gets Reject (3). Replaces 1.2 from 2026-10-25 18:23 UTC. Version 1.2 engines no longer connect. No firm holds a certification on version 1.2, so the 3-month notice does not apply. At the cutover CRX ends every FIX session. Signed quotes and open RFQs stay as on any disconnect (4.9). At the cutover, install the new signature proxy and dictionary. Start the signature proxy with a new `state_file`. It refuses a `state_file` from version 1.x. |
| 2.0.1 | 2026-10-26 | 2 to 7, 9, 11, 12 | Editorial change with no message change. Sections 7 and 12 show each message as the FIX engine sends or receives it. The new 5.10 shows the messages between the signature proxy and CRX. Version 2.0 engines remain compatible. No withdrawal date. |

Change rules:

- CRX adds one row with its date to this table for each change.
- CRX gives each certified firm 3 months' notice before a breaking change. See [Certification rules](#112-certification-rules). A breaking change makes a compliant engine fail. Examples: a removed message, tag or value, or a new required tag.
- Each row states if the previous version still connects, and until which date.
- A new optional tag, a new value or a new reject code is not a breaking change. Accept them. See [Unknown tags and values](#42-message-format).
- A new tag inside a repeating group is a breaking change. CRX publishes a new [`FIX44-CRX.xml`](FIX44-CRX.xml) with it.

## 2. Scope

### 2.1 Service

- FIX 4.4 request for quote (RFQ) for FX non-deliverable forwards (NDFs).
- Markets: USD/MXN, USD/BRL and USD/PHP. SecurityList (y) gives the live list.
- CRX settles each trade in cash, in Circle USDC on Ethereum (chain 1), at its settlement time.
- FIX runs beside the CRX REST and WebSocket API. The same rules, limits and collateral checks apply to each.
- An RFQ sent on FIX shows on REST and WebSocket with `client_rfq_id` = QuoteReqID (131).
- CRX holds no firm key and no custodian credential.

### 2.2 Session roles

Each SenderCompID has one role.

| Role | TargetCompID (56) | Firm sends | CRX sends |
|---|---|---|---|
| Trading | `CRX-TRD` | Session messages. R, AJ (taker). S, Z, AG (maker). x, a, H. | Session messages. AI, S, AG, 8, R, y, j. |
| Drop copy | `CRX-DC` | Session messages only | Session messages. ExecutionReport (8) fills for every trade of the seat, from FIX, REST or WebSocket. |

Session messages: Logon (A), Logout (5), Heartbeat (0), TestRequest (1), ResendRequest (2), SequenceReset (4) and Reject (3).

A trading session carries the taker flow, the maker flow or both. The CRX roles of the seat decide which. A seat with the maker role receives QuoteRequest (R) messages.

| MsgType | Message | Direction | Section |
|---|---|---|---|
| A | Logon | Both ways | [7.2](#72-logon-a) |
| 5 | Logout | Both ways | [7.3](#73-logout-5) |
| 0, 1, 2, 4 | Heartbeat, TestRequest, ResendRequest, SequenceReset | Both ways | [7.4](#74-heartbeat-0-testrequest-1-resendrequest-2-sequencereset-4) |
| 3 | Reject | CRX to firm | [7.5](#75-reject-3) |
| R | QuoteRequest | Taker to CRX | [7.6](#76-quoterequest-r-taker-to-crx) |
| AI | QuoteStatusReport | CRX to taker | [7.7](#77-quotestatusreport-ai-crx-to-taker) |
| S | Quote | CRX to taker | [7.8](#78-quote-s-crx-to-taker) |
| AG | QuoteRequestReject | CRX to taker | [7.9](#79-quoterequestreject-ag-crx-to-taker) |
| AJ | QuoteResponse | Taker to CRX | [7.10](#710-quoteresponse-aj-taker-to-crx) |
| 8 | ExecutionReport | CRX to firm | [7.11](#711-executionreport-8-crx-to-firm) |
| H | OrderStatusRequest | Firm to CRX | [7.12](#712-orderstatusrequest-h-firm-to-crx) |
| R | QuoteRequest | CRX to maker | [7.13](#713-quoterequest-r-crx-to-maker) |
| S | Quote | Maker to CRX | [7.14](#714-quote-s-maker-to-crx) |
| AG | QuoteRequestReject | Maker to CRX | [7.15](#715-quoterequestreject-ag-maker-to-crx) |
| AI | QuoteStatusReport | CRX to maker | [7.16](#716-quotestatusreport-ai-crx-to-maker) |
| Z | QuoteCancel | Maker to CRX | [7.17](#717-quotecancel-z-maker-to-crx) |
| a | QuoteStatusRequest | Firm to CRX | [7.18](#718-quotestatusrequest-a-firm-to-crx) |
| x, y | SecurityListRequest, SecurityList | Firm to CRX, CRX to firm | [7.19](#719-securitylistrequest-x-and-securitylist-y) |
| j | BusinessMessageReject | CRX to firm | [7.20](#720-businessmessagereject-j-crx-to-firm) |

### 2.3 Not on FIX

- Deposits and withdrawals. Use the CRX web app or the REST API.
- Market data and streaming prices.
- Early close of a trade, including mutual close. Use the REST API.
- Account viewers, collateral events and settlement reports. Use the REST or WebSocket API.
- New test requests. Use `POST /test-requests`. A maker answers its QuoteRequest (R) on FIX.

### 2.4 Terms

| Term | Meaning |
|---|---|
| Seat | The Ethereum address that holds the firm's collateral and signs its quotes and trades. One seat for each firm. |
| Login key | An address that CRX has on record to sign the Logon for a seat. Optional. It cannot sign quotes or trades. |
| Taker | The firm that requests a quote and accepts it. |
| Maker | The firm that sends a quote. |
| Settlement time | The UTC instant in MaturityDate (541) and MaturityTime (1079). The fixing uses the price at this time. The trade settles on the same date. |
| Upfront premium | UpfrontPrice (1742), in percent of the notional. Positive: the taker pays. Negative: the maker pays. Absent: 0. |
| Signature | A 65-byte secp256k1 ECDSA signature: r (32 bytes), s (32 bytes) and v (1 byte, 27 or 28). FIX carries it in base64, 88 characters. See [Encodings](#411-encodings). |
| Signature data | The CRX values that a signature covers and that no FIX field holds. RawData (96) holds these values on the R to a maker and on the S to a taker. |
| RFQ end | The time an RFQ closes: TransactTime (60) of the R + the RFQ life. The RFQ life is 120 s for an R from FIX. An RFQ from the REST API can set another life. A test request ends at ExpireTime (126) of its R. |
| Quote end | The earlier of the RFQ end and the signature end. A signed quote binds until this time. ValidUntilTime (62) of the Quote (S) to the taker holds it. CRX sends AI 297 = 7 to the maker at this time. |
| Signature end | ValidUntilTime (62) of the R to a maker. The quote signature covers this time. A trade on the quote must reach Ethereum before it. It is later than the RFQ end. |
| Signature proxy | The program `crx-signature-proxy`. The firm runs it beside its FIX engine. It adds the signatures and removes the signature data. |
| Trace ID | The ID at the end of each Text (58) from CRX. CRX support uses it to find the event. |

### 2.5 References

| Document | Location |
|---|---|
| FIX 4.4 with Errata 20030618 | [FIX Trading Community](https://www.fixtrading.org/standards/fix-4-4/) |
| FIX Latest extension packs up to EP312, EP270 included | [FIX Trading Community](https://www.fixtrading.org/standards/extension-packs/) |
| FIX-over-TLS (FIXS) | [FIX Trading Community](https://www.fixtrading.org/standards/fixs/) |
| CRX dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) | Published with this document. See [Dictionary](#13-dictionary). |
| CRX REST and WebSocket API reference | Provided at onboarding |
| CRX status page | Provided at onboarding |
| CRX web app | Provided at onboarding |
| EIP-191, signed data | [ethereum.org](https://eips.ethereum.org/EIPS/eip-191) |
| EIP-712, typed structured data | [ethereum.org](https://eips.ethereum.org/EIPS/eip-712) |
| RFC 4648, base64 | [RFC Editor](https://www.rfc-editor.org/rfc/rfc4648) |

## 3. Connectivity

### 3.1 Network path

```text
Firm host                                                  CRX
+------------+   FIX 4.4, TCP    +-----------------+   FIX 4.4 over TLS   +-----+
| FIX engine | <---------------> | signature proxy | <------------------> | CRX |
+------------+    127.0.0.1      +-----------------+      internet        +-----+
```

- Connect the FIX engine to the signature proxy on the same host, on 127.0.0.1.
- The signature proxy connects to CRX over TLS 1.2 or TLS 1.3 only, as FIX-over-TLS (FIXS) sets. CRX rejects an older TLS version and a plain TCP connection.
- The signature proxy opens the connection to CRX only after it signs the Logon or refuses to sign it.
- Onboarding gives the CRX host name and port. Connect by the host name. Resolve it before each connection.
- The signature proxy checks the CRX server certificate. CRX does not ask for a client certificate.
- Trust the public CA roots. Do not pin the CRX certificate or key.
- A source IP allowlist is optional for each SenderCompID. A Logon from another address gets Logout with code `LOGON_IP_NOT_ALLOWED`.
- CRX closes a new connection at once when its source address already has 8 connections with no accepted Logon.
- CRX accepts at most 120 new connections from each source address in 60 s, counted from the first connection. CRX closes a further connection at once. This limit does not apply to an address on the allowlist of a SenderCompID.

### 3.2 CompIDs

| Field | Value |
|---|---|
| SenderCompID (49) | Provided at onboarding. 1 to 64 characters: `A-Z`, `a-z`, `0-9`, period, underscore and hyphen. The first character is not a period. |
| TargetCompID (56) | `CRX-TRD` for a trading session. `CRX-DC` for a drop-copy session. |

- Each SenderCompID maps to one seat and one role.
- One live session for each SenderCompID. A second Logon gets Logout with code `LOGON_SESSION_ACTIVE`. The first session continues.

### 3.3 Reconnect

1. Wait 5 s before the first reconnect.
2. Double the wait after each failed attempt, up to 60 s. A FIX engine that takes one interval waits 5 s before each attempt.
3. Keep the sequence numbers. Except after the daily reset, send ResetSeqNumFlag (141) = N.
4. After a Logout that rejects a Logon, correct the cause before the next attempt.

CRX sets no limit on the number of attempts. The limits for each source address in [Network path](#31-network-path) apply. See [Engine settings](#34-engine-settings) for ReconnectInterval.

### 3.4 Engine settings

QuickFIX/J settings for a trading session. Onboarding gives the SenderCompID and the CRX host. The FIX engine connects to the signature proxy.

```ini
[SESSION]
ConnectionType=initiator
BeginString=FIX.4.4
SenderCompID=<Provided at onboarding>
TargetCompID=CRX-TRD
SocketConnectHost=127.0.0.1
SocketConnectPort=<listen port of the signature proxy>
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

| Key | QuickFIX/J | QuickFIX C++ | QuickFIX/n | QuickFIX/Go |
|---|---|---|---|---|
| ReconnectInterval | `5;10;20;40;60`. The last value repeats. | `5`. One value only. | `5`. One value only. | `5`. One value only. |
| UseDataDictionary | `Y` | `Y` | `Y` | No such key. DataDictionary turns on the dictionary. |
| DataDictionary | [`FIX44-CRX.xml`](FIX44-CRX.xml) | [`FIX44-CRX.xml`](FIX44-CRX.xml) | [`FIX44-CRX.xml`](FIX44-CRX.xml) | [`FIX44-CRX.xml`](FIX44-CRX.xml) |
| AllowUnknownMsgFields | `Y` | `Y` | `Y` | `Y` |
| ValidateUserDefinedFields | `N` | `N` | `N` | `N` |

CRX tests [`FIX44-CRX.xml`](FIX44-CRX.xml) in QuickFIX/J. The other columns and the notes below come from the guide of each engine.

- OnixS: the engine reads its own dialect XML, not the QuickFIX format. Declare the fields of [section 8](#8-custom-tags) in a dialect. Put 1079, 1741 and 1742 in the NoRelatedSym (146) group of QuoteRequest (R).
- FIX Antenna Java 2.24.3 and later: set `customFixVersions`, `customFixVersion.<alias>.fixVersion=FIX.4.4` and `customFixVersion.<alias>.fileName=FIX44-CRX.xml`.
- Artio: generate the codecs from [`FIX44-CRX.xml`](FIX44-CRX.xml). Keep `receiverBufferSize` at 8,192 bytes or more. Artio refuses a message larger than this buffer.

Use the CRX dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml). A stock FIX 4.4 dictionary gives wrong fields:

- It declares MaturityTime (1079), UpfrontPriceType (1741) and UpfrontPrice (1742) inside the NoRelatedSym (146) group. The stock `FIX44.xml` does not declare them.
- QuickFIX C++, QuickFIX/n and QuickFIX/Go end a group at the first tag that the group does not declare. With the stock `FIX44.xml` and AllowUnknownMsgFields=Y, a QuoteRequest (R) passes validation. The application then reads Side (54) and OrderQty (38) outside the group.
- ValidateUserDefinedFields applies to tags 5000 and up only. It does not cover 1079, 1741 and 1742.
- AllowUnknownMsgFields=Y and ValidateUserDefinedFields=N keep the session up when CRX adds an optional tag. Use them only with [`FIX44-CRX.xml`](FIX44-CRX.xml) loaded.
- ResetOnLogon=N keeps the sequence numbers over a reconnect. With it, QuickFIX/J sends no ResetSeqNumFlag (141). Send 141 = Y on the first Logon after the daily reset ([4.4](#44-sequence-numbers)). In QuickFIX/J, set it in `toAdmin` on a Logon with MsgSeqNum (34) = 1.
- Without 141 = Y on that Logon, the signature proxy refuses each QuoteRequest (R) and Quote (S) from CRX whose MsgSeqNum (34) is at or below the highest number it passed before the reset. A restart of the signature proxy clears that count.

## 4. Session

### 4.1 Logon

1. The FIX engine sends Logon (A) with HeartBtInt (108).
2. The signature proxy signs the Logon. It sets Username (553) and ApplicationSystemVersion (1604), and adds RawDataLength (95) and RawData (96). See [Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx).
3. CRX checks the session fields, then the signature. See [Which message rejects](#91-which-message-rejects) for the order of the checks.
4. CRX answers with Logon (A). Send application messages only after this answer. CRX processes a message that arrives before its answer after the answer, in MsgSeqNum order.
5. When CRX rejects the Logon, it sends Logout (5) with Text (58). The first token of Text is a code from [Logout codes](#96-logout-codes). Then CRX closes the connection.

The signature proxy can refuse to sign the Logon. It then sends the Logon to CRX without RawDataLength (95) and RawData (96). CRX answers with Logout code `LOGON_SIGNATURE_MISSING`. See [Unsigned messages](#56-unsigned-messages).

A rejected Logon does not change the sequence numbers or the stored messages. This also applies with ResetSeqNumFlag (141) = Y. Its Logout has MsgSeqNum 1. After code `SEQ_NUM_TOO_LOW`, the Logout has the next MsgSeqNum of CRX.

Connection rules:

- Send the Logon within 10 s after the TCP connection to the signature proxy opens. Otherwise the signature proxy closes the connection without a message.
- CRX applies the same 10 s limit to the connection from the signature proxy. The TLS handshake counts.
- Make the Logon the first message. Otherwise CRX closes the connection without a message.
- Do not send Password (554). CRX does not use it.
- With a custodian back end, set HeartBtInt to 30 or more. Also set the LogonTimeout of the FIX engine to 30 s or more. A custodian can take several seconds to sign.
- Set ApplicationSystemName (1603) to the name and version of the FIX engine. Set ApplicationSystemVendor (1605) to its vendor. Each value is 1 to 64 printable characters. CRX logs 1603, 1604 and 1605 with the SenderCompID. They do not change the Logon result.

#### 4.1.1 Logon signature

RawData (96) holds the base64 of an EIP-191 `personal_sign` signature of the 9 lines below. Join the lines with `\n` (0x0A). Add no newline at the end.

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

- The 9 lines are the CRX REST login message for `POST /session`. The `Body` line is the Keccak-256 hash of an empty body.
- The `Chain` line holds the chainId of the signature domain: `1`. See [Tags the signature proxy adds and removes](#52-tags-the-signature-proxy-adds-and-removes).
- The `Custody` line holds the seat of the SenderCompID.
- Line 7 holds Username (553): the seat address, or a login key address on record for the seat.
- CRX builds the message again from the seat of the SenderCompID, 553, its chain ID and 52. It gets the address from the signature. The address must be 553.
- The timestamp must be at most 120 s behind and at most 5 s ahead of CRX time.
- CRX takes each signature one time. Each Logon needs a new signature. The signature proxy signs each Logon. A Logon with a signature that CRX took before gets Logout code `UNAUTHORIZED`.
- The Logon opens an API session for the seat. The API session lasts up to 8 hours. See [Schedule](#48-schedule) for the renewal.

The test vector of this signature is in [Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx).

### 4.2 Message format

- BeginString (8) is `FIX.4.4` on each message.
- Field values are UTF-8 text. An application message with a value that is not UTF-8 gets Reject (3) with 373 = 6. A Logon with one gets Logout.
- Times are UTC. Seconds are 00 to 59: CRX refuses second 60.
- SendingTime (52) must be within 120 s of CRX time. Keep the host clock on NTP. CRX syncs its clock to UTC and checks the offset at start and after each daily reset. CRX logs an alert when the offset is above 1 ms.
- Decimals are plain text: digits and one `.` only. UpfrontPrice (1742) can also start with `-`.
- SecurityList (y) gives MinPriceIncrement (969) = 0.000001 for each market.
- Signatures and signature data are base64. Ethereum addresses and the on-chain trade hash are `0x` and lowercase hex. See [Encodings](#411-encodings).
- Keep each message at most 8,192 bytes, from BeginString (8) to CheckSum (10). The Logon answer gives this size in MaxMessageSize (383).
- A Logon over 8,192 bytes gets Logout code `MESSAGE_TOO_LARGE`. A BodyLength (9) above 8,192 before the Logon closes the connection with no message.
- After the Logon, a message over 8,192 bytes ends the session with Logout code `MESSAGE_TOO_LARGE`. A BodyLength (9) above 8,192 ends the session at once with the same Logout.
- Send BeginString (8), BodyLength (9) and MsgType (35) first, in this order, and CheckSum (10) last.
- CRX drops a message with a bad BodyLength (9), a bad CheckSum (10) or another order of these 4 tags. It does not answer the message. Its MsgSeqNum stays open. The next message shows a gap, and CRX sends ResendRequest.
- A Logon with a RawDataLength (95) other than the byte count of RawData (96) gets Logout code `LOGON_SIGNATURE_INVALID`. The fields after 96 keep their place.
- A tag without a value gets Reject (3) with 373 = 4. A repeating group out of order gets Reject (3) with 373 = 15. Each uses its MsgSeqNum.

Data types, from [`FIX44-CRX.xml`](FIX44-CRX.xml):

| FIX type | Format | Precision | Tags |
|---|---|---|---|
| UTCTimestamp | `YYYYMMDD-HH:MM:SS.sss`, UTC | CRX sends milliseconds. CRX reads 0 to 9 decimal places and uses the first 3. | 52, 60, 62, 122, 126 |
| TZTimeOnly | `HH:MM:SSZ`, UTC | Seconds. CRX refuses decimals in the seconds, a missing `Z` and another offset. | 1079 |
| LocalMktDate | `YYYYMMDD` | One day | 64, 541 |
| Qty | Plain decimal | At most 6 decimal places | 38 |
| Price | Plain decimal | At most 6 decimal places. UpfrontPrice (1742): at most 2. | 44, 132, 133, 1742 |
| Float | Plain decimal | 6 decimal places | 969 |
| Length | Whole number | Not applicable | 95 |
| data | Base64 text | Not applicable | 96 |
| String | UTF-8 text | See [IDs and repeats](#410-ids-and-repeats) | IDs, 58, 553, 20007 |

Unknown tags and values:

- CRX ignores a tag that this document does not list for the message.
- CRX reads Account (1) on R, S and AJ only. A value other than the seat address gets code `ACCOUNT_MISMATCH`. CRX ignores Account (1) on every other message.
- Accept an unknown tag, value or reject code from CRX. Do not end the session for it.
- When the code in Text (58) is unknown, act on the FIX reason field: 373, 380, 658, 300 or 103.

### 4.3 Heartbeat and TestRequest

- HeartBtInt (108) is 5 to 60 seconds. Use 30. CRX sends the same value in its Logon answer.
- A HeartBtInt outside 5 to 60 gets Logout with code `LOGON_HEART_BT_INT`.
- CRX sends Heartbeat (0) when it sends nothing else for HeartBtInt seconds.
- CRX sends TestRequest (1) when it receives nothing for 1.2 × HeartBtInt.
- CRX sends Logout with code `HEARTBEAT_TIMEOUT` when it then receives nothing for another 1.2 × HeartBtInt.
- Answer each TestRequest with a Heartbeat that holds the same TestReqID (112). CRX does the same.

### 4.4 Sequence numbers

| Case | CRX action |
|---|---|
| MsgSeqNum is the expected number | CRX processes the message. |
| MsgSeqNum is higher than expected | CRX holds the message. It sends one ResendRequest (2): BeginSeqNo (7) = expected number, EndSeqNo (16) = 0. It processes the held messages in order when the gap closes. |
| More than 10,000 messages held | Logout with code `GAP_QUEUE_FULL`. |
| MsgSeqNum is lower than expected, PossDupFlag (43) = Y | CRX ignores the message. |
| MsgSeqNum is lower than expected, no PossDupFlag | Logout with code `SEQ_NUM_TOO_LOW`. Text gives the expected and the received numbers. |
| Logon MsgSeqNum is lower than expected | Logout with code `SEQ_NUM_TOO_LOW`. |
| Logon MsgSeqNum is higher than expected | Logon answer, then ResendRequest. |

- Sequence numbers continue across reconnects in one session day. They start again at 1 after the daily reset. See [Schedule](#48-schedule).
- CRX ignores NextExpectedMsgSeqNum (789).
- ResetSeqNumFlag (141) = Y on a Logon starts both sides at 1. The Logon MsgSeqNum must then be 1. CRX answers with 141 = Y.
- Send 141 = Y on the first Logon after the daily reset. At another time, send it only on a request from CRX support. CRX logs an alert for each such Logon.
- A Logon with 141 = Y deletes the messages that CRX keeps for resend. After it, use QuoteStatusRequest (a) and OrderStatusRequest (H) to get the state.

### 4.5 Resend

When the firm sends ResendRequest (2):

- CRX sends the stored application messages again. Each has PossDupFlag (43) = Y and OrigSendingTime (122) = the first SendingTime. MsgSeqNum and body do not change.
- CRX replaces session messages and expired content with SequenceReset-GapFill: GapFillFlag (123) = Y, NewSeqNo (36) = the next number to send.
- EndSeqNo (16) = 0 asks for all messages up to the last one sent.
- BeginSeqNo 0, or an EndSeqNo below BeginSeqNo, gets Reject (3) with 373 = 5.
- A BeginSeqNo above the last MsgSeqNum that CRX sent gets Reject (3) with 373 = 5 and 371 = 7. Text gives the last MsgSeqNum sent.
- CRX answers the full range of a ResendRequest in runs of 1,000 messages, from BeginSeqNo.
- Keep one ResendRequest open at a time.
- CRX keeps each message it sent since the last daily reset, MsgSeqNum 1 to the last one sent. No other limit applies.

| Message from CRX | On resend |
|---|---|
| ExecutionReport (8), QuoteStatusReport (AI), QuoteRequestReject (AG), BusinessMessageReject (j), SecurityList (y) | Sent again |
| Quote (S) to a taker | Sent again before ValidUntilTime (62). Gap-filled after it. |
| QuoteRequest (R) to a maker | Sent again before ExpireTime (126). Gap-filled after it. |
| Session messages | Gap-filled |

Repeats:

- A repeated request gets the stored answer. See [IDs and repeats](#410-ids-and-repeats).
- CRX sends a stored answer under a new MsgSeqNum with PossResend (97) = Y. The answer keeps its ExecID (17).
- Use ExecID (17) to drop a second copy of an ExecutionReport.

### 4.6 SequenceReset

- GapFill mode, GapFillFlag (123) = Y: NewSeqNo (36) must be higher than MsgSeqNum. Otherwise Reject (3) with 373 = 5.
- Reset mode, 123 = N or absent: CRX moves its expected number up to NewSeqNo. An equal value has no effect. A lower value gets Reject (3) with 373 = 5.
- Use Reset mode only on a request from CRX support.

### 4.7 Logout

- Either side can start a Logout. Answer a Logout with a Logout.
- CRX answers a firm Logout with Logout code `LOGOUT_ACK`. A firm Logout with a bad SendingTime (52) gets Reject (3), then the Logout answer.
- CRX waits 10 s for the answer to its Logout. Then it closes the connection.
- After these codes, CRX closes the connection at once and does not wait for an answer: `SEQ_NUM_TOO_LOW`, `SEQ_INVALID`, `BEGIN_STRING`, `COMP_ID_PROBLEM`, `SENDING_TIME_ACCURACY`, `MESSAGE_TOO_LARGE`, `HEARTBEAT_TIMEOUT`, `GAP_QUEUE_FULL` and `LOGON_ON_LIVE_SESSION`.
- After a session end or a refused Logon, CRX closes the connection within 1 s. A peer that reads nothing does not delay it. The next Logon for the CompID is then free.
- Each CRX Logout has Text (58) with a code. See [Logout codes](#96-logout-codes). Put the reason in Text on a firm Logout too.
- More than 50 rejects in 60 s end the session with Logout code `ERROR_RATE`.
- Each Reject (3) counts. Each j that answers a request counts, except a j with code `SERVICE_UNAVAILABLE`. A j that answers a request from an earlier connection does not count.
- A Logout cancels nothing. See [Disconnect and recovery](#49-disconnect-and-recovery).

### 4.8 Schedule

New York uses daylight time (UTC−4) from the second Sunday of March to the first Sunday of November. It uses standard time (UTC−5) for the rest of the year.

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
3. From 17:00:30, log on with MsgSeqNum (34) = 1 and ResetSeqNumFlag (141) = Y.

Session renewal:

- CRX ends each session 10 minutes before the API session of the seat ends, with Logout code `SESSION_RENEWAL`. This is at most 7 h 50 min after the Logon.
- CRX sends this Logout only when no accept waits for its answer.
- Log on again after 5 s. Sequence numbers continue.

Other rules:

- The FIX service takes a Logon at any time outside the 30 s of the daily reset.
- Outside market hours, CRX can reject a request, or no maker quotes it.
- The CRX status page shows the state of the FIX service. Onboarding gives its address.
- CRX announces planned maintenance on the status page at least 5 business days before it starts. The notice gives the start and the end in UTC.
- Set the FIX engine session to the time zone America/New_York. Set EndTime to 17:00:00 and StartTime to 17:00:30. See [Engine settings](#34-engine-settings).

### 4.9 Disconnect and recovery

- A disconnect or a Logout cancels nothing.
- CRX closes a session when its socket takes no data for HeartBtInt, at most 10 s. It sends no Logout. The reports stay queued for the next Logon. The CompID can log on again at once.
- A signed quote stays binding until the quote end, a QuoteCancel (Z) or a fill. See [Terms](#24-terms).
- An RFQ stays open until the RFQ end. See [Terms](#24-terms).
- An accept that reached CRX stays valid.
- A QuoteCancel (Z) or a decline (AG) that a CRX stop cuts runs again at the next Logon.
- CRX keeps the reports for a firm that is not logged on. They arrive after its next Logon, before any new message.
- Each session of the seat gets its own reports at its own next Logon. An R that opened while the session was down goes out at that Logon, before its ExpireTime (126). A CRX restart drops it.
- An application answer to a message sent right after the Logon waits behind these reports.
- An answer to a request never overtakes a report that CRX queued before it. This includes the answer to H or a, and a stored answer to a repeat.
- CRX sends a session Reject (3) at once, also while these reports go out.
- Such an answer carries TargetSubID (57) from the request. Its first send has no PossResend (97).
- A report that never went out has no PossResend (97). This includes a report made while the session was down, closing or sending these reports.
- A report held over a CRX restart carries PossResend (97) = Y.
- CRX keeps trade reports over a crash. It does not keep a queued answer to H or a. Send that request again after the next Logon.
- A message whose send the session end cut goes out again with PossResend (97) = Y.
- An answer that CRX makes after its own Logout waits for the next Logon.

Host move:

- CRX runs the FIX service on one host at a time.
- When CRX moves the service to another host, the CRX host name resolves to the new address. The sequence numbers and the messages kept for resend move with the service.
- A message sent again after the move carries PossDupFlag (43) = Y or PossResend (97) = Y.

After a reconnect:

1. Log on with the next sequence number and ResetSeqNumFlag (141) = N.
2. Let the FIX engine fill each gap with ResendRequest.
3. Maker: send OrderStatusRequest (H) with ClOrdID (11) = the QuoteID, for each quote without a final report. OrdStatus (39) in the answer gives the state. See [OrderStatusRequest](#712-orderstatusrequest-h-firm-to-crx).
4. Taker: send OrderStatusRequest (H) for each ClOrdID without a final report.

### 4.10 IDs and repeats

| ID | Set by | Rule |
|---|---|---|
| QuoteReqID (131) on a taker R | Firm | String(128). See the firm ID rule below. Unique for each seat. |
| QuoteID (117) on a maker S | Firm | String(128). See the firm ID rule below. Unique for each seat. |
| QuoteRespID (693) and ClOrdID (11) on AJ | Firm | String(128). See the firm ID rule below. Unique for each seat. |
| QuoteReqID (131) on a maker R | CRX | A UUID for the RFQ and the maker seat. A maker never sees the taker's QuoteReqID. |
| QuoteID (117) on a taker S | CRX | A UUID for the quote and its signature data. A new S after code `TRADE_STALE` has a new QuoteID. |
| OrderID (37) | CRX | A UUID for the RFQ and the seat. One OrderID covers every accept of the seat on one RFQ. ClOrdID (11) names each accept. It is `NONE` only on an accept that CRX refuses before 150 = A, and on the status of an unknown order. |
| TrdMatchID (880) | CRX | A UUID for the trade. The same value for the taker and the maker. |
| SecondaryExecID (527) | CRX | The on-chain trade hash, `0x` and 64 lowercase hex characters. On a fill only. |
| ExecID (17) | CRX | A UUID. A fill (150 = F) has the same ExecID on each session of the seat, order entry and drop copy. A Trade Cancel (150 = H) does too. Every other ExecutionReport has its own ExecID, unique across all sessions, days and CRX restarts. A resent report keeps its ExecID. |
| TestReqID (112) | Sender of the TestRequest | Any printable text. The Heartbeat answer copies it. |
| SecurityReqID (320) on x, QuoteStatusReqID (649) on a, OrdStatusReqID (790) on H | Firm | String(128). See the firm ID rule below. 320 is mandatory. 649 and 790 are optional. CRX copies the value to the answer and does not check it for repeats. |
| SecurityResponseID (322) | CRX | The trace ID of the SecurityList (y) |

- Every ID that CRX assigns in 131, 117, 37, 880 and 17 is a UUID version 8 (RFC 9562) of 36 characters. Its form is lowercase `8-4-4-4-12` hex. SecondaryExecID (527) carries the 66-character trade hash.
- Exception: on AI 297 = 10, QuoteID (117) repeats the QuoteReqID (131) of the firm. See [QuoteStatusReport (AI), CRX to taker](#77-quotestatusreport-ai-crx-to-taker).
- Firm ID rule: an ID that a firm chooses has 1 to 128 printable ASCII characters, 0x20 to 0x7E. It has no `=` and no `|`. This applies to 131, 117, 693, 11, 649, 790 and 320, on each message that carries them. Any other ID gets Reject (3) with 373 = 5. RefTagID (371) names the tag.
- An ID from CRX does not change after a CRX restart, on a resend or on the drop copy.
- A re-accept after code `TRADE_STALE` keeps the OrderID (37) under a new ClOrdID (11).
- The firm IDs are unique for each seat. All sessions of the seat share them.
- An ID stays taken until 24 h after its order or quote ends. The daily reset does not free it.
- A maker QuoteID is single-use for the seat. While CRX holds the QuoteID, a Quote with other terms gets j 380 = 0, code `DUPLICATE`. After that, a reuse gets AI 297 = 5, code `NONCE_COLLISION`.
- An ID sent again with the same content is a repeat. CRX sends the stored answer. It opens no new RFQ, quote or trade.
- An ID sent again with other content gets a BusinessMessageReject (j) with code `DUPLICATE`. The first request and its state do not change.

### 4.11 Encodings

| Value | Form | Tags |
|---|---|---|
| Signature | Base64 of the 65 bytes, 88 characters, one `=` at the end, no `0x` | RawData (96) of the Logon, CrxSignature (20007) |
| Signature data | Base64. RawDataLength (95) gives the number of characters. | RawData (96) of the R to a maker and of the S to a taker |
| Ethereum address | `0x` and 40 lowercase hex characters | Username (553), Account (1) |
| On-chain trade hash | `0x` and 64 lowercase hex characters | SecondaryExecID (527) |
| ID from CRX | UUID version 8 (RFC 9562), lowercase `8-4-4-4-12` hex form, 36 characters | 131 on the R to a maker, 117 on the S to a taker, 37, 880, 17 |

- Base64 is the standard alphabet of RFC 4648 section 4, with `=` padding: `A-Z`, `a-z`, `0-9`, `+` and `/`. The unused bits before the `=` are 0.
- CRX decodes each signature and encodes it again. A value that is not exactly 88 characters, or that does not give the same text again, gets code `INVALID_FIELD`: AI 297 = 5, 300 = 99 on an S, and 8 150 = 8, 103 = 99 on an AJ. On a Logon, the code is `LOGON_SIGNATURE_INVALID`.
- The signature must decode to 65 bytes with a v of 27 or 28, and it must give the seat. Otherwise the code is `SIGNATURE_INVALID`.
- The REST API gives the same 65 bytes as `0x` and 130 lowercase hex characters.

## 5. Signature proxy

### 5.1 Function

- The firm runs `crx-signature-proxy` on its own host, beside its FIX engine. CRX supplies the program.
- Run one signature proxy process for each trading session.
- A firm that uses its own signature program applies every rule of this section to the byte.
- The signature proxy changes only the messages in [Tags the signature proxy adds and removes](#52-tags-the-signature-proxy-adds-and-removes). It sets a new BodyLength (9) and CheckSum (10) on each message it changes. All other bytes stay.
- It keeps the MsgSeqNum. It sends no message of its own. The FIX session runs end to end between the FIX engine and CRX.
- The FIX engine sends and receives no custom tag.
- The key or the custodian credential stays on the firm's host.
- The signature proxy reads one TOML file. The file gives:
  - the listen address for the FIX engine. It must be a loopback address, except when `allow_remote_listen = true`.
  - `state_file`: the file that keeps the signed IDs over a restart. With it, the signature proxy never signs one ID with other terms. The signature proxy drops a torn final line, with no newline at its end, and writes a log line. Any other line that does not read stops the start. Start the signature proxy on a new state file only at the daily reset, with no live RFQ.
  - the CRX host and port, and an optional CA certificate
  - the seat address and an optional login key address
  - the signature domain. Its chainId also goes in the `Chain` line of the Logon signature.
  - the back end and its credential files

### 5.2 Tags the signature proxy adds and removes

| Message | Direction | Change |
|---|---|---|
| Logon (A) | To CRX | Sets Username (553) to the address that signs. Adds RawDataLength (95) = 88 and RawData (96) = the signature of the login message. See [Logon signature](#411-logon-signature). Sets ApplicationSystemVersion (1604) to its own version. |
| Quote (S) from a maker | To CRX | Adds CrxSignature (20007): the EIP-712 `Quote` signature. |
| QuoteResponse (AJ), 694 = 1 | To CRX | Adds CrxSignature (20007): the EIP-712 `Trade` signature. |
| A Quote (S) or an accept that it does not sign | To CRX | Sets Text (58) to the reason. See [Unsigned messages](#56-unsigned-messages). |
| A Logon that it does not sign | To CRX | Sends it without RawDataLength (95) and RawData (96). |
| QuoteRequest (R) to a maker | To the FIX engine | Reads RawDataLength (95) and RawData (96), then removes both tags. |
| Quote (S) to a taker | To the FIX engine | Reads RawDataLength (95) and RawData (96), then removes both tags. |

- The signature proxy keeps the signature data of each R and S that it passes, for the signatures.
- It removes 95 and 96 from every R and S, resends with PossDupFlag (43) = Y included. Bytes from CRX that it cannot read never reach the FIX engine. The FIX engine gets these messages again with its ResendRequest (2).
- It owns Username (553) and ApplicationSystemVersion (1604) on the Logon, and Text (58) on the S and the AJ. It replaces a value from the FIX engine and never adds a second copy.
- The FIX engine never receives the signature data. Keep it out of logs and away from third parties. The R holds the seed of the maker salt.

Domain of both EIP-712 signatures:

| Field | Value |
|---|---|
| name | `CRX` |
| version | `rulebook-1.0` |
| chainId | `1` |
| verifyingContract | The CRX contract address. Provided at onboarding. |

### 5.3 Maker quote signature

The signature proxy keeps each QuoteRequest (R) that it passes, by QuoteReqID, with its signature data. It signs the amount, currency, side, settlement time, premium and rate from the Quote (S) that the FIX engine sends. It checks each value against the R.

A message from CRX sets no signed term of the quote. The R gives the signature data, the signature end in ValidUntilTime (62) and the values for the checks. See [Terms](#24-terms).

The signature proxy signs the S only when all these conditions are true:

1. It passed an R with the QuoteReqID (131) of the S. The R had RawData (96) of 64 bytes.
2. Symbol (55), Side (54), OrderQty (38), Currency (15), MaturityDate (541), MaturityTime (1079) and UpfrontPrice (1742) are equal to the R.
3. Currency (15) is the base currency of Symbol (55), for example `USD` for `USD/MXN`.
4. QuoteType (537) is absent or `1`.
5. ValidUntilTime (62) is not earlier than ValidUntilTime (62) of the R.
6. The S has one rate, on the side that the R asks for.

Otherwise it sends the S unsigned, with the reason in Text (58). See [Unsigned messages](#56-unsigned-messages).

Signature data of the R, 64 bytes:

| Bytes | Name | Value |
|---|---|---|
| 0 to 31 | takerRef | A hash of the taker seat and its leg. It binds the quote to the taker seat of the RFQ. It does not show the taker address. |
| 32 to 63 | seed | 32 random bytes for the leg ID and the salt of this R |

For each S that it signs, the signature proxy makes the leg ID, the salt and the nonce:

```text
salt  = keccak256("CRX-FIX/salt" ‖ seed ‖ QuoteID)
legId = keccak256("CRX-FIX/leg" ‖ seed ‖ anchorQuoteID)[0..24] ‖ sigEnd
nonce = legId[16..24]
```

- `‖` joins byte strings. A text in quotes and a QuoteID are their UTF-8 bytes, with no length and no terminator.
- `QuoteID` is the QuoteID (117) of this S.
- `anchorQuoteID` is the QuoteID of the first S that the signature proxy signs on the R. A later S on the R keeps this leg ID. After a QuoteCancel (Z) on the R, the next signed S is a new anchor.
- `[0..24]` is the first 24 bytes. `legId[16..24]` is bytes 16 to 23, read as a big-endian uint64.
- `sigEnd` is the signature end, ValidUntilTime (62) of the R, in Unix seconds, as an 8-byte big-endian integer.
- CrxSignature (20007) holds the base64 signature of the typed data below.

A new signed Quote (S) on the same R and leg replaces the earlier quote of the maker. CRX sends AI 297 = 6 for the earlier QuoteID. A QuoteStatusRequest (a) on it gets 297 = 6. An OrderStatusRequest (H) on it gets 39 = 4. An S on a new leg ends no quote.

CRX does not receive the leg ID or the salt. It makes both again from the seed and the QuoteIDs. It checks the signature with these leg IDs, in this order, and uses the first one that gives the seat:

1. The leg ID of the last S on the R with a valid signature, whatever the result of that quote.
2. The leg ID anchored on this S.
3. The leg ID anchored on each signed S that CRX received on the R after that S, the oldest first. This includes an S that CRX rejected before its signature check.

CRX checks at most 32 leg IDs. When none gives the seat, CRX sends AI 297 = 5, 300 = 99, code `SIGNATURE_INVALID`.

Type:

```text
Quote(address seat,bytes32 legId,bytes32 pair,int8 side,uint256 notional,uint64 rate,int16 premiumBps,uint40 expiry,uint64 nonce,bytes32 salt,bytes32 takerRef)
```

| Field | Value |
|---|---|
| seat | The seat address |
| legId | The leg ID above |
| pair | Keccak-256 of the Symbol (55) text of the S, for example `USD/MXN` |
| side | The maker's side, the opposite of the S Side (54): −1 when 54 = 1, +1 when 54 = 2 |
| notional | OrderQty (38) of the S × 10^6, in the currency of Currency (15) |
| rate | OfferPx (133) or BidPx (132) of the S × 10^6 |
| premiumBps | UpfrontPrice (1742) of the S × 100, for example 25 for `0.25`. 0 when 1742 is absent. |
| expiry | The settlement time of the S, from 541 and 1079, in Unix seconds |
| nonce | The nonce above |
| salt | The salt above |
| takerRef | takerRef from the signature data of the R |

The signed quote binds the maker. When a taker accepts it, the trade opens with no further step from the maker.

The quote binds to the taker seat of the RFQ. An AJ from another seat on its QuoteID gets 8 150 = 8, code `UNKNOWN_QUOTE`. A Trade signature of another seat does not match takerRef.

Test vector. Key: the public Anvil and Hardhat test account 0, as in the Logon test vector of [Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx). The domain uses the test verifyingContract `0x1111111111111111111111111111111111111111`. Onboarding gives the CRX contract address.

| Item | Value |
|---|---|
| Domain separator | `0xc10b07f28873cb547d1ab61e8cacb2c0084fc537ac932f55d21f403a0194785c` |
| R fields | 55 = `USD/MXN`, 54 = `1`, 38 = `100000`, 15 = `USD`, 541 = `20261021`, 1079 = `18:00:00Z`, 62 = `20261020-14:30:30.000` |
| R RawData (96) | `EREREREREREREREREREREREREREREREREREREREREREiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIg==` |
| takerRef, seed | 32 bytes of `0x11`, 32 bytes of `0x22` |
| S fields | 117 = `Q-1`, 55 = `USD/MXN`, 54 = `1`, 38 = `100000`, 15 = `USD`, 541 = `20261021`, 1079 = `18:00:00Z`, 133 = `18.452` |
| anchorQuoteID | `Q-1` |
| sigEnd | `1792506630` |
| salt | `0xc9574c292cb5b42f827ce26fbce2dd3ffe8891e34076057d6c79570b21fc0c6e` |
| legId | `0x12c93b1e0050c6a14d786ac05bfe0862bb113dbc05eb44ee000000006ad77b06` |
| nonce | `13479623037459055854` |
| pair | `0x69f1670ccd0386df6e79b445190cb08f07e9d85ef8bb6ef820417312ea39752f` |
| side, notional, rate, premiumBps, expiry | `-1`, `100000000000`, `18452000`, `0`, `1792605600` |
| Struct hash | `0x478c9e5b98afce7e07d62c2e2a54efd231bd2e2b64bde024625bf5b49332a313` |
| Digest | `0xf949174efc9965ca72e22000a3d94de5cdde59ae8e9fe5fdf3d0c7784805193a` |
| CrxSignature (20007) | `aFQExQ1sGblBTQ2c3Mrs4RdvC9LBRlzJCXnPOati1T42eKgEkCwLMAW3lVxplerQOavPVjuMNorln8wuRgltFxs=` |
| The same 65 bytes in hex | `0x685404c50d6c19b9414d0d9cdccaece1176f0bd2c1465cc90979cf39ab62d53e3678a804902c0b3005b7955c6995ead039abcf563b8c368ae59fcc2e46096d171b` |

### 5.4 Taker accept signature

For a QuoteResponse (AJ) with 694 = 1, the signature proxy finds the Quote (S) by QuoteID (117). It reads the signature data of the S. It signs only when all these conditions are true:

1. The S had RawData (96) of 104 bytes.
2. Symbol (55), Side (54) and OrderQty (38) are equal to the S.
3. Price (44) is the quoted rate of the S.
4. The S names a QuoteRequest (R) that the FIX engine sent. Its Symbol, Side, OrderQty, 541, 1079 and 1742 are equal to the R.
5. Currency (15), when present on the R, the S or the AJ, is the base currency of Symbol (55).

Signature data of the S, 104 bytes:

| Bytes | Name |
|---|---|
| 0 to 31 | pairC |
| 32 to 63 | ownLegId |
| 64 to 71 | ownNonce, a big-endian uint64 |
| 72 to 103 | ownSalt |

Type:

```text
Trade(string summary,string pair,string side,uint256 notionalE6,uint64 rateE6,int16 premiumBps,uint40 maturity,bytes32 pairC,bytes32 ownLegId,uint64 ownNonce,bytes32 ownSalt)
```

| Field | Value |
|---|---|
| summary | The line below, made from the other fields |
| pair | The Symbol (55) text, for example `USD/MXN` |
| side | `buy` when Side (54) = 1. `sell` when 54 = 2. |
| notionalE6 | OrderQty (38) × 10^6 |
| rateE6 | Price (44) × 10^6 |
| premiumBps | UpfrontPrice (1742) of the S × 100. 0 when 1742 is absent. |
| maturity | The settlement time of the S, from 541 and 1079, in Unix seconds |
| pairC, ownLegId, ownNonce, ownSalt | The signature data of the S |

The `summary` field is one line of text that a custodian shows to an approver:

```text
<side> <notional> <BASE> vs <QUOTE> at <rate> <QUOTE> per <BASE>, matures <YYYY-MM-DDTHH:MM:SSZ>, upfront <upfront>
```

- `<side>` is the side field.
- `<notional>` is OrderQty. The whole part has a space before each group of 3 digits, counted from the right.
- `<rate>` is Price, with no spaces.
- A fraction has no zeros at its end. A value with no fraction has no `.`.
- `<BASE>` and `<QUOTE>` are the two currencies of Symbol (55).
- `<upfront>` is `none` for a premium of 0. It is `taker pays <p> %` for a positive premium and `maker pays <p> %` for a negative premium. `<p>` is the absolute value with 2 decimal places.

Example:

```text
buy 100 000 USD vs MXN at 18.452 MXN per USD, matures 2026-10-21T18:00:00Z, upfront none
```

CRX sends an S only when its signature data agrees with the fields of the S.

Test vector. Key and domain as in the [Maker quote signature](#53-maker-quote-signature) vector.

| Item | Value |
|---|---|
| AJ fields | 694 = `1`, 117 = `Q-1`, 55 = `USD/MXN`, 54 = `1`, 38 = `100000`, 44 = `18.452`. From the S: 541 = `20261021`, 1079 = `18:00:00Z`. |
| S RawData (96) | `MzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzNERERERERERERERERERERERERERERERERERERERERERAAAAAAAAAAHVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVU=` |
| pairC, ownLegId, ownNonce, ownSalt | 32 bytes of `0x33`, 32 bytes of `0x44`, `7`, 32 bytes of `0x55` |
| summary | `buy 100 000 USD vs MXN at 18.452 MXN per USD, matures 2026-10-21T18:00:00Z, upfront none` |
| pair, side, notionalE6, rateE6, premiumBps, maturity | `USD/MXN`, `buy`, `100000000000`, `18452000`, `0`, `1792605600` |
| Struct hash | `0x0fbcdc080d767d4a131ff09fc970383f6c952f4ea2ec179199d2a9e4fe4c4499` |
| Digest | `0xb1dd977d44056e8116fff81578e6e0f83e583ab7fa182b6329d525ab3acad215` |
| CrxSignature (20007) | `BPU1LMHiH0D+Z9L023rH0QjPwVOmHJW74HwKVHWT1RYRnqnvz3zlXgUGcooitleHj7PhdQmyGWJHBMKO3BMw0xs=` |
| The same 65 bytes in hex | `0x04f5352cc1e21f40fe67d2f4db7ac7d108cfc153a61c95bbe07c0a547593d516119ea9efcf7ce55e0506728a22b657878fb3e17509b219624704c28edc1330d31b` |

### 5.5 Key back ends

| Back end | Signing | Firm supplies |
|---|---|---|
| Local key | A secp256k1 key in a file with mode 0600, in hex. The signature proxy never takes the key from the command line or the environment. It never writes the key to a log. | The key file |
| Fireblocks | `TYPED_MESSAGE` with type `EIP712` for Quote and Trade. `ETH_MESSAGE` for the Logon. The signature proxy reads the transaction until its status is `COMPLETED`. | API key file, API user RSA private key file, vault account ID |
| Fordefi | `evm_message` with `typed_message_type` for Quote and Trade. `personal_message_type` for the Logon. The signature proxy uses `create-and-wait`. | API user token file, API user P-256 private key file, vault ID |

- Each back end gets the address from the signature. It sends the signature only when the address is the seat, or the login key for a Logon.
- The custodian vault must allow EIP-191 and EIP-712 signing.
- Set a custodian policy that signs with no approval by a person, for these messages only:
  - EIP-712 messages with domain name `CRX`, chainId 1, the CRX contract address, and primaryType `Quote` or `Trade`.
  - EIP-191 messages that start with `CRX-REST-LOGIN`.
- Fireblocks: use a `TYPED_MESSAGE` policy rule and the callback handler of the signature proxy.
  - The signature proxy keeps a ledger file with mode 0600. Before each request, it writes the externalTxId, the digest and the end of its wait to this file. It adds the Fireblocks transaction ID when Fireblocks returns it.
  - Set the callback handler URL of the API user to the signature proxy, path `/v2/tx_sign_request`. Use public key authentication (RSA 2048).
  - The callback needs HTTPS. Set `tls_cert_file` and `tls_key_file`, or put a TLS server in front of a loopback address.
  - The callback approves a request only when all these conditions are true:
    1. The signature proxy sent the request since its last start, and its wait is open.
    2. The transaction ID is the recorded one, when the ledger holds one.
    3. The operation is `TYPED_MESSAGE` from the vault account of the configuration.
    4. The request has one message, with the recorded digest.
    5. An `EIP712` message is a `Quote` or a `Trade` under the CRX domain. An `ETH_MESSAGE` is the CRX Logon text for the chain of the configuration.
  - The callback rejects each other request and each configuration change. After a restart, the callback rejects each request of the former process.
  - The callback answers HTTP 401 to a body that is not an RS256 JWT by the Co-Signer key. When the JWT has `exp`, an `exp` more than 60 s in the past also gets HTTP 401. When it has `iat`, an `iat` more than 60 s from now also gets HTTP 401.
  - The callback answers HTTP 413 to a request body over 1 MiB.
  - Use one API user for each signature proxy, and for nothing else.
- Fordefi: use a message policy on the domain and the primary type, with programmatic signing.
- A policy that waits for a person cannot meet the 5 s maker window.
- Each Logon, signed Quote (S) and signed accept is one signing request to the custodian. Size the custodian API limits for the quote rate of the firm. With Fireblocks, each signature takes one create request and one status read every 250 ms until it completes.
- On HTTP 429 from the custodian, the signature proxy waits the Retry-After time or longer: 250 ms, doubled on each 429 in a row, up to 2 s. A Retry-After over 3600 s counts as 3600 s. When the wait ends after the deadline of the message, it stops and sends the message unsigned.

### 5.6 Unsigned messages

When the signature proxy does not sign a Quote or an accept, it sends it unsigned. It sets Text (58) to the code and one sentence, in place of a Text from the FIX engine:

```text
<CODE>: The signature proxy did not sign the quote.
<CODE>: The signature proxy did not sign the accept.
```

When the signature proxy does not sign a Logon, it sends the Logon without RawDataLength (95) and RawData (96). CRX answers with Logout (5):

```text
LOGON_SIGNATURE_MISSING: The Logon carries no signature. (trace <id>)
```

The signature proxy writes the code and the details to its log.

CRX rejects an unsigned Quote or accept with no further action. It checks the signature before the terms. The reject carries the code from Text (58) of the unsigned message.

| Unsigned message | Answer |
|---|---|
| Logon (A) | Logout (5), code `LOGON_SIGNATURE_MISSING`. The signature proxy log gives the reason. |
| Quote (S) | QuoteStatusReport (AI) 297 = 5, 300 = 99 |
| QuoteResponse (AJ), 694 = 1 | ExecutionReport (8) 150 = 8, 103 = 99 |

| Code | Cause |
|---|---|
| `INVALID_FIELD` | A required field is absent or has a bad format, RawData (96) of the R included. Or the maker Quote has a QuoteType (537) other than `1`. |
| `UNKNOWN_QUOTE_REQUEST` | The signature proxy did not pass a QuoteRequest with this QuoteReqID in the last 15 minutes. |
| `UNKNOWN_QUOTE` | The signature proxy did not pass a Quote with this QuoteID in the last 15 minutes. |
| `TERMS_MISMATCH` | A field differs from the R or the S. Or Currency (15) is not the base currency of Symbol (55). For an accept, the S differs from the firm's own QuoteRequest (R). A second copy of an R or S with other terms stops all signatures on its ID. This applies to a copy under a MsgSeqNum that the signature proxy already passed. |
| `REPEATED_TAG` | The R or the S repeats a tag that the signature reads. |
| `WRONG_SIDE` | The maker Quote gives a price on the side that the QuoteRequest does not ask for. |
| `SENDING_TIME_OUT_OF_RANGE` | The Logon SendingTime (52) is more than 5 s ahead of the clock or more than 120 s behind it. |
| `TYPED_DATA_MISMATCH` | RawData (96) of the S that the accept names does not hold the 104 bytes of signature data. |
| `ID_REUSED` | The signature proxy saw this ID before with other terms. |
| `SIGN_TIMEOUT` | No signature before the deadline. |
| `SIGNATURE_NOT_SEAT` | The signature does not match the seat. |
| `SIGN_FAILED` | The back end gave no signature. |
| `CACHE_FULL` | The signature proxy holds its maximum number of live IDs. It signs no message on a new ID until an ID reaches its end time. |
| `INBOUND_UNREAD` | The signature proxy could not read a message from CRX. After it, the signature proxy signs nothing until the next Logon. |
| `QUOTE_LIFE_TOO_LONG` | ValidUntilTime (62) of the R is later than ValidUntilTime (62) of the maker Quote. |

A Quote or an accept with no CrxSignature (20007) and no signature proxy code in Text (58) gets code `SIGNATURE_MISSING`.

### 5.7 Seat address

- Use an EOA or an MPC address with one secp256k1 key.
- A contract wallet, for example a Safe or an ERC-4337 account, cannot sign for a seat. CRX rejects it at Logon with code `SEAT_CANNOT_SIGN`.

### 5.8 Timing

| Step | Deadline | Late result |
|---|---|---|
| Maker Quote (S) | ExpireTime (126) of the R: TransactTime (60) + 5 s, or + half the RFQ life when that is shorter. A test request: the RFQ end. | AI 297 = 5, 300 = 4, code `QUOTE_WINDOW_CLOSED` |
| Taker accept, AJ 694 = 1 | ValidUntilTime (62) of the S | 8 150 = 8, 103 = 4, code `QUOTE_EXPIRED` |

- CRX can end the quote collection before ExpireTime (126).
- The R reaches the maker up to 1 s after TransactTime (60), plus the network time. This time counts in the 5 s window.
- The signature proxy writes the sign time of each message to its log.
- When the signature proxy signs a maker quote later than 4.5 s after TransactTime, it still sends it. After ExpireTime (126), CRX rejects the quote with code `QUOTE_WINDOW_CLOSED`.

Choose the back end from measured sign times:

| Back end | Taker | Maker |
|---|---|---|
| Local key | Fits | Fits |
| Custodian | Fits | Fits when the 99th percentile time from R TransactTime (60) to S sent is below 4.5 s |

Measure the 50th and 99th percentile sign times for each back end during certification.

CRX measures two times for each maker Quote (S). The first runs from the R that CRX sent to the S that CRX received. The second runs from SendingTime (52) of the S to its receipt. CRX gives each maker its own 50th, 90th and 99th percentile figures.

### 5.9 Resend and logs

- On a resend (43 = Y), the signature proxy adds the same tags as on the first copy. It never signs a message two times.
- The signature proxy writes JSON lines to standard error. Keep these logs for certification.

### 5.10 Messages between the signature proxy and CRX

The FIX engine never sends or reads Username (553), RawDataLength (95), RawData (96) or CrxSignature (20007). The signature proxy adds these fields to the messages to CRX. It removes 95 and 96 from the messages to the FIX engine. It sets ApplicationSystemVersion (1604) on the Logon. A firm that signs without the signature proxy sends and reads the messages in this form.

- Each example comes from the test kit run of [Raw examples](#12-raw-examples), on the connection between the signature proxy and CRX. Section 12 shows the same messages at the FIX engine.
- The keys are test keys with no funds. The EIP-712 domain uses the verifyingContract of the local service.

Logon (A), signature proxy to CRX ([`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix)):

```text
8=FIX.4.4|9=289|35=A|34=1|49=TKR1|52=20261026-09:33:15.393|56=CRX-TRD|98=0|108=30|141=Y|1603=QuickFIX/J 2.3.3|1605=quickfixj.org|553=0xf683c26739271eeb6501552c68ed37597df8d90b|95=88|96=98Nu4OdZNuPBj2nYfJ10q1GV3s21Olvdu5UqW5hojaBJ9EHqIfxROoBp6BFsZ/UCq6XPk7JwniuvSbPZr4Mt8Bw=|1604=crx-signature-proxy/0.1.0|10=034|
```

- 553 Username: the address that signs the Logon, the seat or a login key. 42 characters (`0x` + 40 lowercase hex).
- 95 RawDataLength: `88`, the number of characters in 96.
- 96 RawData: the Logon signature, base64 of 65 bytes. 88 characters. See [Logon signature](#411-logon-signature).
- 1604 ApplicationSystemVersion: the version of the signature proxy, `crx-signature-proxy/<version>`, with `+<commit>` when the build has one. It replaces a value from the FIX engine.

The FIX engine sends this Logon as [`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix).

Test vector of the [Logon signature](#411-logon-signature). Key: the public Anvil and Hardhat test account 0. It holds no funds. The seat signs.

| Item | Value |
|---|---|
| Seat address and Username (553) | `0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266` |
| SendingTime (52) | `20261020-14:30:00.000` |
| `Chain` line | `Chain: 1` |
| `Timestamp` line | `1792506600000` |
| RawDataLength (95) | `88` |
| RawData (96) | `JKdpNNytR43t65PVUy6LVUDbyqbP0OzqOSzMp2/Qv1YNDEOh/RfhNm1PWyiDWibTxDYNUFFPgyvF5MUYDzBqBRw=` |
| The same 65 bytes in hex | `0x24a76934dcad478dedeb93d5532e8b5540dbcaa6cfd0ecea392ccca76fd0bf560d0c43a1fd17e1366d4f5b28835a26d3c4360d50514f832bc5e4c5180f306a051c` |

QuoteRequest (R), CRX to the maker's signature proxy ([`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix)):

```text
8=FIX.4.4|9=359|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:33:16.016|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|62=20261026-09:42:45.000|126=20261026-09:33:20.781|60=20261026-09:33:15.781|95=88|96=TTiOCgP1HDhRlYk+T9oTWzT8z426sVdMO86OAu/d5avkCDsmFBqdCwinfMJ31nS52oVJvxMLbFIIVE1wvDc3Rw==|10=242|
```

- 95 RawDataLength: `88`, the number of characters in 96.
- 96 RawData: the signature data of the `Quote`, base64 of 64 bytes (takerRef and seed). 88 characters. See [Maker quote signature](#53-maker-quote-signature).

Each copy of the R carries the same RawData (96). A resend and an R that CRX keeps until the next Logon carry the same RawData (96). The signature proxy removes 95 and 96. The FIX engine receives [`50a-quote-request-to-engine.fix`](examples/50a-quote-request-to-engine.fix).

Quote (S), the maker's signature proxy to CRX ([`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix)):

```text
8=FIX.4.4|9=330|35=S|34=2|49=MKR1|52=20261026-09:33:16.044|56=CRX-TRD|15=USD|38=1000000|54=1|55=USD/MXN|62=20261026-09:42:45.000|64=20261127|117=Q-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|20007=0fTVsTaYLViaVBwNzUclzYxecAfNBRjwSgwKt2Nnz88PRb/E0OjQaU0AFLu+zrHwxZY4RGLRMp5PlNs4HsPdUBw=|10=137|
```

- 20007 CrxSignature: the EIP-712 `Quote` signature, base64 of 65 bytes. 88 characters. See [Maker quote signature](#53-maker-quote-signature).

The FIX engine sends this Quote as [`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix).

Quote (S), CRX to the taker's signature proxy ([`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix)):

```text
8=FIX.4.4|9=413|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:33:21.054|131=RFQ-000201|117=959bbc1a-7496-82e8-af14-38c826bae7c3|537=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|133=18.4753|62=20261026-09:35:15.781|60=20261026-09:33:21.048|95=140|96=opnqaSDcEq+6Fgi01vYVUS4RqH8D3qco+BAKbpBcuYmVZHBnJlHZ6xy1DOpTB8Ufx/cFRnziATEAAAAAat8glQAAAaF3jqsJjQuNri/MHi4UFVM+IA0Cy1ccPxvpq4tM6Rfe9CkmJmA=|10=233|
```

- 95 RawDataLength: `140`, the number of characters in 96.
- 96 RawData: the signature data of the `Trade`, base64 of 104 bytes (pairC, ownLegId, ownNonce and ownSalt). 140 characters. See [Taker accept signature](#54-taker-accept-signature).

The signature proxy removes 95 and 96. The FIX engine receives [`22a-quote-to-engine.fix`](examples/22a-quote-to-engine.fix).

QuoteResponse (AJ), the taker's signature proxy to CRX ([`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix)):

```text
8=FIX.4.4|9=338|35=AJ|34=4|49=TKR1|52=20261026-09:33:21.065|56=CRX-TRD|11=ORD-000201|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:33:21.065|64=20261127|117=959bbc1a-7496-82e8-af14-38c826bae7c3|167=FXNDF|541=20261127|693=QR-000201|694=1|1079=18:00:00Z|20007=qkLfhj7/MD7qVi349vO0LP4zn70FCyXxFP0sad06SNAl+zxxUrXfGVFvDw7x4/WjUS78kNoM6UtlsHdWBb/1ABw=|10=230|
```

- 20007 CrxSignature: the EIP-712 `Trade` signature, base64 of 65 bytes. 88 characters. See [Taker accept signature](#54-taker-accept-signature).

The FIX engine sends this accept as [`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix).

An accept and a quote that the signature proxy did not sign, signature proxy to CRX ([`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix), [`63-quote-unsigned.fix`](examples/63-quote-unsigned.fix)):

```text
8=FIX.4.4|9=307|35=AJ|34=4|49=TKR1|52=20261026-09:36:47.809|56=CRX-TRD|11=ORD-001001|38=1000000|44=18.4850|54=1|55=USD/MXN|60=20261026-09:36:47.809|64=20261127|117=11003a68-99ab-84fc-bbc4-fafb643da005|167=FXNDF|541=20261127|693=QR-001001|694=1|1079=18:00:00Z|58=TERMS_MISMATCH: The signature proxy did not sign the accept.|10=213|
8=FIX.4.4|9=298|35=S|34=3|49=MKR1|52=20261026-09:40:25.189|56=CRX-TRD|15=USD|38=2000000|54=1|55=USD/MXN|62=20261026-09:49:54.000|64=20261127|117=Q-002101|131=f453ed43-281e-8723-947e-b8517cdfc1e7|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|58=TERMS_MISMATCH: The signature proxy did not sign the quote.|10=104|
```

- No CrxSignature (20007).
- 58 Text: the code and the sentence of the signature proxy, for example `TERMS_MISMATCH: The signature proxy did not sign the accept.` See [Unsigned messages](#56-unsigned-messages).

CRX answers with [`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix) and [`64-quote-status-unsigned.fix`](examples/64-quote-status-unsigned.fix).

## 6. Message flows

### 6.1 Steps

Taker:

1. Request: send QuoteRequest (R). CRX answers at once with QuoteStatusReport (AI) 297 = 10 (Pending).
2. Quote: CRX collects maker quotes. Then it sends one Quote (S), the best one, or QuoteRequestReject (AG). No second S follows when the S expires. The answer comes 5 s to 20 s after the R. A BusinessMessageReject (j) with code `RATE_LIMITED` or `SERVICE_UNAVAILABLE` also ends the R.
3. Accept or pass: before ValidUntilTime (62), send QuoteResponse (AJ). 694 = 1 accepts. 694 = 6 passes.
4. Confirm: CRX sends ExecutionReport (8) 150 = A (Pending New) within 100 ms of the accept. Then it sends 150 = 0 (New) when it takes the accept.
5. Fill: CRX sends 8 150 = F when the trade opens on Ethereum. It sends 8 150 = 8 when the trade does not open.
6. Cancel after the fill: until the settlement time, CRX can send 8 150 = H. The trade then does not stand.

- On the local test service, the time from AJ to 8 150 = F is 2.6 s at p50 and 2.9 s at p99. On Ethereum, 150 = F waits for the block of the trade.
- CRX support calls the firm about an order at 39 = A for more than 10 minutes.

Maker:

1. Request: CRX sends QuoteRequest (R) to each maker for each RFQ. Side (54) is the taker's side. A maker seat of the taker's firm gets no R.
2. Quote: before ExpireTime (126), send Quote (S) with the terms of the R. CRX answers with AI 297 = 0, or AI 297 = 5. To decline, send QuoteRequestReject (AG).
3. Accept or pass: the taker decides. Before an accept, the maker can cancel its quote with QuoteCancel (Z).
4. Confirm: when a taker accepts the quote, CRX sends 8 150 = 0 (New). The quote stays binding.
5. Fill: CRX sends 8 150 = F when the quote wins and the trade opens on Ethereum. Otherwise CRX sends AI 297 = 7 at the quote end.
6. Cancel after the fill: until the settlement time, CRX can send 8 150 = H. The trade then does not stand.

### 6.2 RFQ and quote

```text
Taker                          CRX                              Maker
  | 1. R QuoteRequest -------->  |                                  |
  | <---- 2. AI 297=10 (Pending) |                                  |
  |                              | 3. R QuoteRequest -------------> |
  |                              | <---- 4. S Quote, signed (< 5 s) |
  |                              | 5. AI 297=0 -------------------> |
  | <----- 6. S Quote (best one) |                                  |
```

- A maker does not learn the taker on R. A taker does not learn the maker on S or AI.
- Each side can read the other seat from the trade on Ethereum (527) after the fill.

### 6.3 Accept

```text
Taker                          CRX                              Maker
  | 1. AJ 694=1, signed ------>  |                                  |
  | <----- 2. 8 150=A (< 100 ms) |                                  |
  | <----------- 3. 8 150=0      | 4. 8 150=0 --------------------> |
  |                              |   (trade opens on Ethereum)      |
  | <-- 5. 8 150=F, TrdMatchID X | 6. 8 150=F, TrdMatchID X ------> |
  |                              | 7. AI 297=7 to other makers ---> |
```

### 6.4 Pass

A pass ends the RFQ for the taker. The maker quotes stay binding until the quote end.

```text
Taker                          CRX                              Maker
  | 1. AJ 694=6 -------------->  |                                  |
  | <----------- 2. AI 297=11    |                                  |
  |                              | 3. AI 297=7 at the quote end --> |
```

### 6.5 Expiry

```text
Taker                          CRX                              Maker
  | (no AJ before 62)            |                                  |
  | <- 1. AI 297=7 QUOTE_EXPIRED | 2. AI 297=7 at the quote end --> |
  | 3. AJ 694=1 after 62 ----->  |                                  |
  | <- 4. 8 150=8, QUOTE_EXPIRED |                                  |
```

### 6.6 No quote and decline

```text
Taker                          CRX                              Maker
  | 1. R QuoteRequest -------->  |                                  |
  | <---- 2. AI 297=10 (Pending) | 3. R QuoteRequest -------------> |
  |                              | <----- 4. AG decline (optional)  |
  | <------ 5. AG 658=8 NO_QUOTE |                                  |
```

When every live maker declines and no quote arrives, the RFQ ends before the 5 s window ends.

### 6.7 Cancel

```text
Maker                          CRX
  | 1. Z QuoteCancel --------->  |
  | <----------- 2. AI 297=1     |   (no accept before the cancel)
  | <- 2. j 380=0 QUOTE_ACCEPTED |   (a taker accepted first)
  | <- 2. j 380=0 QUOTE_NOT_LIVE |   (the quote has ended)
```

### 6.8 States

| Message | State | Meaning | Final | Next action |
|---|---|---|---|---|
| AI 297 = 10 to the taker | Pending | CRX took the R and asks the makers. | No | Wait for S, AG, or j with code `RATE_LIMITED` or `SERVICE_UNAVAILABLE`. Each ends the R. |
| S to the taker | Quoted | One binding quote, valid until ValidUntilTime (62). | No | Send AJ 694 = 1 or 694 = 6. |
| AG to the taker | Rejected or no quote | No quote for this request. | Yes | Correct the cause. Send a new R with a new QuoteReqID. |
| AI 297 = 7 to the taker | Expired | The quote expired with no accept. | Yes | Send a new R. |
| AI 297 = 11 | Passed | The taker passed. | Yes | None. |
| 8 150 = A, 39 = A | Pending New | CRX received the accept and checks it. The order stays here while its outcome is not clear. | No | Wait for 150 = F or 150 = 8. |
| 8 150 = 0, 39 = 0 | New | CRX took the accept, or a taker accepted the maker's quote. The trade is not final. | No | Wait for the fill. |
| 8 150 = F, 39 = 2 | Filled | The trade is open on Ethereum. Until the settlement time, 150 = H can follow. | Yes | Book the trade with TrdMatchID (880). |
| 8 150 = 8, 39 = 8 | Rejected | No trade. CRX holds no collateral for it. | Yes | Read the code in Text (58). Send a new R when the code allows a retry. |
| 8 150 = H, 39 = 4 | Trade Cancel | The trade does not stand. CRX sends it after 150 = F, up to the settlement time of the trade. The collateral that the trade held is free again. | Yes | Remove the trade from the books. |
| AI 297 = 0 to the maker | Quote live | CRX took the signed quote. It binds the maker. | No | Wait. |
| AI 297 = 5 | Quote rejected | CRX rejected the quote. | Yes | Read the code in Text (58). |
| AI 297 = 1 | Canceled for Symbol | CRX confirmed the quote withdrawal. | Yes | None. |
| AI 297 = 6 | Quote replaced | A newer Quote (S) of the maker on the same R and leg replaced this quote. | Yes, unless CRX names this quote as the winner. Then 8 150 = 0 and 150 = F follow. See [Quote (S), maker to CRX](#714-quote-s-maker-to-crx). | None. |
| AI 297 = 7 to the maker | Quote expired | The quote expired with no trade. | Yes | None. |
| AI 297 = 9 | Not found | CRX has no quote with this QuoteID for the seat. | Yes | Check the QuoteID. |

### 6.9 Races

| Race | Result |
|---|---|
| AJ reaches CRX after ValidUntilTime (62) | 8 150 = 8, 103 = 4, code `QUOTE_EXPIRED`. No trade. |
| AJ reaches CRX just before ValidUntilTime (62) | CRX checks the price, then compares its own clock with 62. An AJ received before 62 can still get `QUOTE_EXPIRED`. Keep the host clock on NTP. |
| Taker disconnects after it sends AJ | The accept stays valid if it reached CRX. After the Logon, resend or H gives the state. |
| Maker disconnects after it quotes | The quote stays binding. The trade can fill. The maker gets 8 150 = F after its next Logon. |
| Taker AJ 694 = 6 after its accept on the same quote | j 380 = 0, code `QUOTE_ACCEPTED`. The trade stays valid. |
| CRX refuses or retracts a trade after the fill | 8 150 = H (Trade Cancel), 39 = 4, code `TRADE_CANCELLED`, up to the settlement time. The collateral that the trade held is free again. |
| CRX refuses a trade before the fill | 8 150 = 8, 39 = 8. CRX holds no collateral for it. |
| CRX retracts a trade before the fill | No report. The order waits for the trade. |
| Maker Z while CRX posts the quote | CRX waits for the result of the quote, then answers the Z. |
| Taker AJ 694 = 6 after 62 | j 380 = 0, code `QUOTE_NOT_LIVE`. |
| Maker Z and taker AJ on one quote | The first to reach CRX wins. AJ first: trade, and Z gets j 380 = 0 with code `QUOTE_ACCEPTED`. Z first: AJ gets 8 150 = 8 with code `QUOTE_NOT_LIVE`. |
| Second AJ, same QuoteRespID and ClOrdID | A repeat. CRX sends the stored answer with PossResend (97) = Y. No second trade. |
| Second AJ on one quote, new ClOrdID | 8 150 = 8, 103 = 6, code `DUPLICATE`. No second trade. |
| The signature data of the quote changes before the accept | 8 150 = 8, 103 = 99, code `TRADE_STALE`. No trade. The terms stand. CRX then sends a new Quote (S) with a new QuoteID. Accept that S with a new QuoteRespID and ClOrdID. The OrderID stays the same. Accept one RFQ at a time. An accept on an older RFQ after a newer RFQ's quote arrives gets `TRADE_STALE`. |
| Maker S after ExpireTime (126) | AI 297 = 5, 300 = 4, code `QUOTE_WINDOW_CLOSED`. |
| AJ in the last seconds before the daily reset | The answer goes out after the Logon at 17:00:30. Send OrderStatusRequest (H) after the Logon. |
| CRX has no clear outcome for an accept | The order stays at 150 = A, 39 = A. 150 = F or 150 = 8 follows when CRX has the outcome. H answers 39 = A until then. |
| No ExecutionReport 5 s after an AJ | The state is unknown. Send OrderStatusRequest (H). Do not send a new AJ with a new ClOrdID for the same quote. |

## 7. Messages

Each subsection opens with the sender, the purpose and the answer of the message.

In each table:

- The table shows the message as the FIX engine sends or receives it. The signature proxy adds and removes the fields in [Tags the signature proxy adds and removes](#52-tags-the-signature-proxy-adds-and-removes). [Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx) shows these fields.
- Req is Y (required), N (optional) or C (required on the condition in the notes).
- Type is the FIX data type in FIX44-CRX.xml. String(n) gives the maximum length in characters. The message size of 8,192 bytes limits an inbound String with no (n).
- The mark `→` shows a field in the NoRelatedSym (146) group. The other fields are body fields.
- Send the group fields in the order of the table. The [dictionary](#13-dictionary) gives the same order. A group field out of this order gets Reject (3) 373 = 15.
- In the group, MaturityTime (1079) directly follows MaturityDate (541). UpfrontPriceType (1741) and UpfrontPrice (1742) are the last fields. On S, AJ and 8, these fields are body fields.
- MaturityDate (541) and SettlDate (64) hold the same date.

In the text, `AI 297 = 7` is a QuoteStatusReport (AI) with QuoteStatus (297) = 7. A tag number alone names a field of the message in that subsection.

### 7.1 Header and trailer

Both ways. Each message starts with the header and ends with the trailer.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 8 | BeginString | Y | String | `FIX.4.4` |
| 9 | BodyLength | Y | Length | |
| 35 | MsgType | Y | String | |
| 49 | SenderCompID | Y | String(64) | The firm CompID inbound. `CRX-TRD` or `CRX-DC` outbound. |
| 56 | TargetCompID | Y | String(64) | `CRX-TRD` or `CRX-DC` inbound. The firm CompID outbound. |
| 34 | MsgSeqNum | Y | SeqNum | |
| 43 | PossDupFlag | C | Boolean | `Y` on a message sent again under its first MsgSeqNum |
| 97 | PossResend | C | Boolean | `Y` on a stored answer sent again under a new MsgSeqNum. Also `Y` on a message whose send the session end cut, and on a report held over a CRX restart. |
| 52 | SendingTime | Y | UTCTimestamp | UTC, milliseconds |
| 50 | SenderSubID | N | String(64) | Inbound only. 1 to 64 characters, 0x21 to 0x7E. CRX returns it in TargetSubID (57) on each answer to the message. CRX ignores any other value. |
| 57 | TargetSubID | C | String(64) | Outbound only. The SenderSubID (50) of the message that CRX answers. |
| 122 | OrigSendingTime | C | UTCTimestamp | Required when 43 = Y. Not later than 52. See [Session Reject values](#93-session-reject-values). |
| 10 | CheckSum | Y | String | Trailer |

- Send BeginString (8), BodyLength (9) and MsgType (35) as the first three fields, in this order. Send CheckSum (10) as the last field. CRX drops a message with another order and sends no answer.
- CRX sends the header tags in this order: 8, 9, 35, 49, 56, 34, 43, 97, 52, 122, 57.

### 7.2 Logon (A)

Both ways. The firm opens the session. CRX answers with a Logon, or with a Logout that gives the code. See [Logout codes](#96-logout-codes).

Firm to CRX:

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 98 | EncryptMethod | Y | int | 0 = None |
| 108 | HeartBtInt | Y | int | 5 to 60. Use 30. Use 30 or more with a custodian back end. |
| 141 | ResetSeqNumFlag | N | Boolean | `Y`: both sides start at 1, and MsgSeqNum must be 1. `N`: the default. |
| 1603 | ApplicationSystemName | N | String(64) | The name and version of the FIX engine. 1 to 64 printable ASCII characters. |
| 1604 | ApplicationSystemVersion | N | String(64) | Signature proxy field. The signature proxy sets its own version in place of a value from the FIX engine: `crx-signature-proxy/<version>`, with `+<commit>` when the build has one. For example `crx-signature-proxy/0.1.0`. |
| 1605 | ApplicationSystemVendor | N | String(64) | The vendor of the FIX engine. 1 to 64 printable ASCII characters. |

- The signature proxy sets Username (553) and adds RawDataLength (95) and RawData (96). See [Logon signature](#411-logon-signature) and [Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx).
- CRX logs 1603, 1604 and 1605 with the SenderCompID. These tags do not change the Logon result.

CRX to firm:

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 98 | EncryptMethod | Y | int | `0` |
| 108 | HeartBtInt | Y | int | The firm's value |
| 141 | ResetSeqNumFlag | C | Boolean | `Y` when the firm sent `Y` |
| 383 | MaxMessageSize | Y | Length | `8192`: the largest message CRX takes, in bytes |

Samples: [`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix), [`03-logon-answer.fix`](examples/03-logon-answer.fix), [`04-logon-rejected.fix`](examples/04-logon-rejected.fix). See [Raw examples](#12-raw-examples). Signature proxy to CRX: [`02-logon-to-crx.fix`](examples/02-logon-to-crx.fix).

### 7.3 Logout (5)

Both ways. Either side ends the session with a Logout. The other side answers with a Logout. See [Logout](#47-logout).

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 58 | Text | C | String(256) | Always on a CRX Logout. It starts with the code. See [Text format](#92-text-format) and [Logout codes](#96-logout-codes). |

Samples: [`11-logout-renewal.fix`](examples/11-logout-renewal.fix), [`12-logout-daily.fix`](examples/12-logout-daily.fix).

### 7.4 Heartbeat (0), TestRequest (1), ResendRequest (2), SequenceReset (4)

Both ways. These messages keep the session alive and fill sequence gaps. See [Heartbeat and TestRequest](#43-heartbeat-and-testrequest) and [Resend](#45-resend).

| Message | Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|---|
| Heartbeat (0) | 112 | TestReqID | C | String | In the answer to a TestRequest. |
| TestRequest (1) | 112 | TestReqID | Y | String | Any text |
| ResendRequest (2) | 7 | BeginSeqNo | Y | SeqNum | 1 or more. A value above the last MsgSeqNum that CRX sent gets Reject (3) 373 = 5. |
| ResendRequest (2) | 16 | EndSeqNo | Y | SeqNum | `0`: up to the last message sent. CRX sends the range in runs of 1,000 messages. |
| SequenceReset (4) | 123 | GapFillFlag | N | Boolean | Y = GapFill mode. N = Reset mode, the default. |
| SequenceReset (4) | 36 | NewSeqNo | Y | SeqNum | |

Samples: [`05-heartbeat.fix`](examples/05-heartbeat.fix), [`06-test-request.fix`](examples/06-test-request.fix), [`07-heartbeat-answer.fix`](examples/07-heartbeat-answer.fix), [`08-resend-request.fix`](examples/08-resend-request.fix), [`09-gap-fill.fix`](examples/09-gap-fill.fix).

### 7.5 Reject (3)

CRX to firm. CRX rejects a message that fails a session check. The session continues, except where [Session Reject values](#93-session-reject-values) gives a Logout.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 45 | RefSeqNum | Y | SeqNum | MsgSeqNum of the rejected message |
| 371 | RefTagID | C | int | The tag at fault, when there is one |
| 372 | RefMsgType | C | String | MsgType of the rejected message, when the message has a MsgType |
| 373 | SessionRejectReason | Y | int | `1`, `4`, `5`, `6`, `9`, `10`, `15` or `16`. See [Session Reject values](#93-session-reject-values). |
| 58 | Text | Y | String(256) | Coded Text |

CRX sends a Reject (3) at once. It does not wait behind the reports that CRX holds for a Logon.

Sample: [`10-session-reject.fix`](examples/10-session-reject.fix).

### 7.6 QuoteRequest (R), taker to CRX

The taker asks for a quote. CRX answers with AI 297 = 10 at once. Then one Quote (S), one QuoteRequestReject (AG) or one BusinessMessageReject (j) ends the request. A j carries code `RATE_LIMITED` or `SERVICE_UNAVAILABLE`. A request that fails a field check gets AG at once.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 131 | QuoteReqID | Y | String(128) | A firm ID. See [IDs and repeats](#410-ids-and-repeats). Unique for each seat. Another value gets Reject (3) 373 = 5. |
| 146 | NoRelatedSym | Y | NumInGroup | `1`. Another value gets AG with code `INVALID_REQUEST`. A count other than the number of group entries gets Reject (3) 373 = 16. |
| →55 | Symbol | Y | String(7) | `USD/MXN`, `USD/BRL` or `USD/PHP`. First field of the group. |
| →167 | SecurityType | Y | String | `FXNDF`. Absent: AG with code `MISSING_FIELD`. Another value: AG with code `INVALID_FIELD`. |
| →541 | MaturityDate | Y | LocalMktDate | The UTC date of the settlement time, `YYYYMMDD`. See [Settlement time](#103-settlement-time). |
| →1079 | MaturityTime | Y | TZTimeOnly | The UTC time of day of the settlement time: `HH:MM:SSZ`. Fractional seconds, a missing `Z` or another offset get AG with code `INVALID_FIELD`. |
| →303 | QuoteRequestType | N | int | 1 = Manual. 2 = Automatic gets AG with code `INVALID_REQUEST`. |
| →537 | QuoteType | N | int | 1 = Tradeable. Another value gets AG with code `INVALID_REQUEST`. |
| →54 | Side | Y | char | The taker's side in USD. 1 = Buy USD. 2 = Sell USD. |
| →38 | OrderQty | Y | Qty | Notional in USD. At least 100. At most 6 decimal places. |
| →64 | SettlDate | N | LocalMktDate | Same as 541. Another date gets AG with code `MATURITY_MISMATCH`. |
| →15 | Currency | N | Currency | `USD`, the base currency of 55. Another value gets AG with code `CURRENCY_NOT_BASE`. |
| →1 | Account | N | String(42) | When present, the seat address. Another value gets AG 658 = 6 with code `ACCOUNT_MISMATCH`. |
| →60 | TransactTime | N | UTCTimestamp | |
| →1741 | UpfrontPriceType | N | int | 1 = Percentage of the notional. Another value gets AG with code `INVALID_FIELD`. |
| →1742 | UpfrontPrice | N | Price | The upfront premium in percent of the notional: −100.00 to 100.00, at most 2 decimal places. Positive: the taker pays. Negative: the maker pays. Absent: 0. |

Sample: [`20-quote-request.fix`](examples/20-quote-request.fix).

### 7.7 QuoteStatusReport (AI), CRX to taker

CRX gives the state of an RFQ or of a quote. It sends the report at the request, at a pass and at the quote end. It also answers QuoteStatusRequest (a).

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 649 | QuoteStatusReqID | C | String(128) | In an answer to QuoteStatusRequest (a), when the request had it |
| 131 | QuoteReqID | C | String(128) | The firm's QuoteReqID. Absent on 297 = 9. |
| 117 | QuoteID | Y | String(128) | The CRX quote ID. 297 = 10: the QuoteReqID. 297 = 9: the QuoteID of the a or the AJ. In an answer to an a that names a QuoteReqID: that QuoteReqID. |
| 693 | QuoteRespID | C | String(128) | On 297 = 11, and on 297 = 9 to a pass: the QuoteRespID of the AJ |
| 55 | Symbol | Y | String | On 297 = 9: the Symbol of the AJ, or `N/A` |
| 60 | TransactTime | Y | UTCTimestamp | The time CRX sends the message |
| 297 | QuoteStatus | Y | int | 10 = Pending: CRX took the R. 11 = Pass: CRX took the pass. 7 = Expired: the quote reached its end. 9 = Quote not found: a pass on an unknown QuoteID. In an answer to a: 0 = Accepted: the quote is live, or the taker accepted it (also after 62). 5 = Rejected: the R got AG. 9 = Quote not found. |
| 58 | Text | C | String(256) | On 297 = 9, and on 297 = 7 at the quote end |

Samples: [`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix), [`31-quote-status-pass.fix`](examples/31-quote-status-pass.fix), [`32-quote-status-expired.fix`](examples/32-quote-status-expired.fix).

### 7.8 Quote (S), CRX to taker

CRX gives the taker the best quote for its RFQ. Accept it with QuoteResponse (AJ) 694 = 1 before ValidUntilTime (62), or pass with 694 = 6.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 131 | QuoteReqID | Y | String(128) | The firm's QuoteReqID |
| 117 | QuoteID | Y | String(36) | The CRX quote ID, a UUID. Use it in AJ. A new S after code `TRADE_STALE` has a new QuoteID. |
| 537 | QuoteType | Y | int | 1 = Tradeable |
| 55 | Symbol | Y | String | |
| 167 | SecurityType | Y | String | `FXNDF` |
| 541 | MaturityDate | Y | LocalMktDate | Same as the R |
| 1079 | MaturityTime | Y | TZTimeOnly | Same as the R |
| 54 | Side | Y | char | Same as the R |
| 38 | OrderQty | Y | Qty | Same as the R |
| 64 | SettlDate | Y | LocalMktDate | Same as 541 |
| 15 | Currency | Y | Currency | `USD`, the base currency of 55 |
| 133 | OfferPx | C | Price | The rate when the taker buys (54 = 1) |
| 132 | BidPx | C | Price | The rate when the taker sells (54 = 2) |
| 190 | OfferSpotRate | C | Price | When the taker buys and CRX has a price breakdown for the quote |
| 191 | OfferForwardPoints | C | PriceOffset | Same condition as 190. OfferPx = OfferSpotRate + OfferForwardPoints. |
| 188 | BidSpotRate | C | Price | When the taker sells and CRX has a price breakdown for the quote |
| 189 | BidForwardPoints | C | PriceOffset | Same condition as 188. BidPx = BidSpotRate + BidForwardPoints. |
| 631 | MidPx | C | Price | The forward mid rate, when CRX has one |
| 62 | ValidUntilTime | Y | UTCTimestamp | Accept deadline: the quote end. See [Terms](#24-terms). |
| 60 | TransactTime | Y | UTCTimestamp | |
| 1741 | UpfrontPriceType | C | int | `1`, with 1742 |
| 1742 | UpfrontPrice | C | Price | Same as the R, when the premium is not 0 |

- Spot and forward points come from the quote that CRX supplies. Absent values remain absent. Forward points use rate units and can be negative.
- CRX sends one S for each RFQ. No other S follows when it expires.
- After an accept gets code `TRADE_STALE`, CRX sends one new S with the same terms and a new QuoteID. Accept the new S.
- When CRX cannot present a quote for the RFQ, it sends AG 658 = 99, code `SERVICE_UNAVAILABLE`.
- From CRX to the signature proxy, the S carries RawDataLength (95) and RawData (96) in addition: the signature data of the `Trade`. The signature proxy removes both. See [Taker accept signature](#54-taker-accept-signature).

Sample: [`22a-quote-to-engine.fix`](examples/22a-quote-to-engine.fix). CRX to the signature proxy: [`22-quote-to-taker.fix`](examples/22-quote-to-taker.fix).

### 7.9 QuoteRequestReject (AG), CRX to taker

CRX rejects the RFQ, or ends it with no quote. The RFQ ends. Send a new QuoteRequest (R) for a new quote.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 131 | QuoteReqID | Y | String(128) | |
| 658 | QuoteRequestRejectReason | Y | int | 1 = Unknown symbol. 2 = Exchange closed. 3 = Quote request exceeds limit. 4 = Too late to enter. 6 = Not authorized to request quote. 8 = No market for instrument. 99 = Other. Text (58) gives the code. See [Business reject codes](#94-business-reject-codes). |
| 146 | NoRelatedSym | Y | NumInGroup | `1` |
| →55 | Symbol | Y | String | The Symbol of the R. `N/A` when the R has none. |
| 58 | Text | Y | String(256) | Coded Text |

Sample: [`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix).

### 7.10 QuoteResponse (AJ), taker to CRX

The taker accepts the quote (694 = 1) or passes (694 = 6). CRX answers an accept with ExecutionReport (8): 150 = A, then 150 = 0 and 150 = F, or 150 = 8. CRX answers a pass with AI 297 = 11.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 693 | QuoteRespID | Y | String(128) | A firm ID. See [IDs and repeats](#410-ids-and-repeats). Unique for each seat. Another value gets Reject (3) 373 = 5. |
| 117 | QuoteID | Y | String(36) | The QuoteID of the S |
| 694 | QuoteRespType | Y | int | 1 = Hit/Lift: accept. 6 = Pass. Another value gets Reject (3) 373 = 5. |
| 11 | ClOrdID | C | String(128) | Required when 694 = 1. A firm ID. See [IDs and repeats](#410-ids-and-repeats). Unique for each seat. Another value gets Reject (3) 373 = 5. |
| 55 | Symbol | Y | String(7) | Same as the S |
| 167 | SecurityType | C | String | Required when 694 = 1: `FXNDF`. Absent: 8 150 = 8 with code `MISSING_FIELD`. Another value: 8 150 = 8 with code `INVALID_FIELD`. |
| 541 | MaturityDate | N | LocalMktDate | Same as the S |
| 1079 | MaturityTime | N | TZTimeOnly | Same as the S |
| 54 | Side | Y | char | Same as the S |
| 38 | OrderQty | Y | Qty | Same as the S. The full amount only. |
| 64 | SettlDate | N | LocalMktDate | Same as the S |
| 15 | Currency | N | Currency | `USD`, the base currency of 55. Another value gets 8 150 = 8 with code `CURRENCY_NOT_BASE`. |
| 44 | Price | Y | Price | The quoted rate |
| 60 | TransactTime | N | UTCTimestamp | CRX does not read it. |
| 1 | Account | N | String(42) | When present, the seat address. Another value gets 8 150 = 8, 103 = 15, code `ACCOUNT_MISMATCH`. |

- The signature proxy adds CrxSignature (20007) to an accept, 694 = 1. It sets Text (58) to the reason when it does not sign. See [Taker accept signature](#54-taker-accept-signature) and [Unsigned messages](#56-unsigned-messages).
- A value that differs from the S gets 8 150 = 8 with code `QUOTE_MISMATCH`. A 541, 64 or 1079 that differs from the S gets code `MATURITY_MISMATCH`. No trade.
- An AJ on a quote that another session of the seat holds: 694 = 6 gets j 380 = 0, code `QUOTE_OTHER_SESSION`. 694 = 1 gets 8 150 = 8, code `UNKNOWN_QUOTE`.
- 694 = 6 gets AI 297 = 11. A pass on a quote past 62, passed or expired gets j 380 = 0, code `QUOTE_NOT_LIVE`.
- NewOrderSingle (D) is not an accept. CRX answers it with j 380 = 3, code `UNSUPPORTED_MESSAGE`.

Samples: [`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix), [`30-quote-response-pass.fix`](examples/30-quote-response-pass.fix). Signature proxy to CRX: [`25-quote-response-to-crx.fix`](examples/25-quote-response-to-crx.fix), [`37-quote-response-unsigned.fix`](examples/37-quote-response-unsigned.fix).

### 7.11 ExecutionReport (8), CRX to firm

CRX gives the taker the state of its accept. It gives the maker the state of a quote that a taker accepted. CRX answers OrderStatusRequest (H) with 150 = I.

A fill is a report with 150 = F, or with 150 = I and 39 = 2. A known order is an accept or a quote that CRX holds.

- Book a trade on 150 = F, one time for each TrdMatchID (880).
- 150 = I repeats the fill fields for status only. Do not book it.
- SecondaryExecID (527) gives the hash of the trade on Ethereum.
- The trade on Ethereum, hash in 527, is the record. A missed or late ExecutionReport (8) does not change it. Use OrderStatusRequest (H) to read its state.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 37 | OrderID | Y | String(36) | The CRX order ID, a UUID for the RFQ and the seat. One OrderID covers every accept of the seat on one RFQ, and ClOrdID (11) names each accept. A new accept after code `TRADE_STALE` keeps the OrderID under a new ClOrdID. It is `NONE` only on an accept that CRX refuses before 150 = A, and on the status of an unknown order. |
| 527 | SecondaryExecID | C | String(66) | On a fill. The hash of the trade on Ethereum, `0x` and 64 lowercase hex characters. |
| 11 | ClOrdID | C | String(128) | Taker: the AJ ClOrdID. Maker: the maker's QuoteID. Absent when the AJ had none. |
| 693 | QuoteRespID | C | String(128) | Taker: the QuoteRespID of the AJ |
| 790 | OrdStatusReqID | C | String(128) | In an answer to H, when the request had it |
| 17 | ExecID | Y | String(36) | A UUID in lowercase. A fill (150 = F) has the same ExecID on each session of the seat, order entry and drop copy. A Trade Cancel (150 = H) does too. Every other report has its own ExecID, unique across sessions, days and CRX restarts. A report that CRX sends again keeps its ExecID. |
| 19 | ExecRefID | C | String(36) | On 150 = H: the ExecID of the fill that CRX takes back |
| 150 | ExecType | Y | char | A = Pending New. 0 = New. F = Trade. 8 = Rejected. H = Trade Cancel. I = Order Status. |
| 39 | OrdStatus | Y | char | A = Pending New. 0 = New. 2 = Filled. 4 = Canceled. 8 = Rejected. C = Expired. |
| 103 | OrdRejReason | C | int | On 150 = 8, and on 150 = I for an unknown order. 1 = Unknown symbol. 2 = Exchange closed. 3 = Order exceeds limit. 4 = Too late to enter. 5 = Unknown order. 6 = Duplicate order. 13 = Incorrect quantity. 15 = Unknown account. 99 = Other. |
| 64 | SettlDate | C | LocalMktDate | For a known order. Same as 541. |
| 55 | Symbol | Y | String | `N/A` when CRX does not know it |
| 167 | SecurityType | Y | String | `FXNDF` |
| 541 | MaturityDate | C | LocalMktDate | For a known order |
| 1079 | MaturityTime | C | TZTimeOnly | With 541 |
| 54 | Side | Y | char | The receiver's own side |
| 38 | OrderQty | Y | Qty | `0` for an unknown order |
| 15 | Currency | Y | Currency | `USD`, the base currency of 55 |
| 32 | LastQty | C | Qty | On a fill |
| 31 | LastPx | C | Price | On a fill. The rate. |
| 1056 | CalculatedCcyLastQty | C | Qty | On a fill. LastQty × LastPx in the second currency of 55. CRX rounds it half away from zero to the minor units of that currency (ISO 4217): 2 for MXN, BRL and PHP. |
| 194 | LastSpotRate | C | Price | On a fill, when CRX has a price breakdown |
| 195 | LastForwardPoints | C | PriceOffset | With 194. LastPx = LastSpotRate + LastForwardPoints. |
| 151 | LeavesQty | Y | Qty | OrderQty while 39 = A or 0. `0` in other states. |
| 14 | CumQty | Y | Qty | OrderQty on a fill. `0` in other reports. |
| 6 | AvgPx | Y | Price | The rate on a fill. `0` in other reports. |
| 75 | TradeDate | C | LocalMktDate | On a fill. The UTC date of the trade time. The date changes at 00:00:00 UTC. |
| 60 | TransactTime | Y | UTCTimestamp | The time CRX sends the message |
| 120 | SettlCurrency | C | Currency | With 541. `USD`. |
| 851 | LastLiquidityInd | C | int | On 150 = F, when CRX has the role of the seat in the trade. Not on 150 = I. 1 = Added liquidity: maker. 2 = Removed liquidity: taker. A drop-copy fill can omit it. |
| 58 | Text | C | String(256) | With 103, on 150 = H, and with code `QUOTE_LIVE` on the status of a live maker quote |
| 117 | QuoteID | C | String(128) | Taker: the CRX quote ID. Maker: the maker's QuoteID. Absent when CRX does not know the quote. |
| 880 | TrdMatchID | C | String(36) | On a fill. The CRX trade ID, a UUID. The same value for the taker and the maker. |
| 1741 | UpfrontPriceType | C | int | `1`, with 1742 |
| 1742 | UpfrontPrice | C | Price | With 541, when the premium is not 0 |

| Report | Fields in addition to the Y fields |
|---|---|
| 150 = A or 0 | 64, 541, 1079, 120. 1741 and 1742 when the premium is not 0. 151 = 38. |
| 150 = F | 64, 541, 1079, 120, 851, 32, 31, 1056, 75, 880 and 527. 1741 and 1742 when the premium is not 0. 194 and 195 when CRX has a price breakdown. 151 = 0. |
| 150 = 8 | 103 and 58. Also 64, 541, 1079 and 120 for a known order, with 1741 and 1742 when the premium is not 0. |
| 150 = H | 19, 58, 880, 64, 541, 1079 and 120. 1741 and 1742 when the premium is not 0. 151 = 0, 14 = 0, 6 = 0. |
| 150 = I | The fields of the current state. An unknown order: 37 = `NONE`, 39 = 8, 103 = 5 and 58, with no dates. |

Each taker report on an accept also has 693.

| 150 ExecType | 39 OrdStatus | When | Final |
|---|---|---|---|
| `A` Pending New | `A` Pending New | CRX received the accept. Within 100 ms. Taker only. The order stays at `A` while its outcome is not clear. | No |
| `0` New | `0` New | Taker: CRX took the accept. Maker: a taker accepted the quote. | No |
| `F` Trade | `2` Filled | The trade is final on Ethereum. | Yes. A 150 = H can follow until the settlement time. |
| `8` Rejected | `8` Rejected | CRX rejected the accept, or the trade did not open. | Yes |
| `H` Trade Cancel | `4` Canceled | A correction by CRX only. It is not part of normal operation. Code `TRADE_CANCELLED`. | Yes |
| `I` Order Status | The current state. For a maker quote, see [OrderStatusRequest](#712-orderstatusrequest-h-firm-to-crx). | Answer to OrderStatusRequest (H) | As the state |

- A fill (150 = F) stands. Until the settlement time of the trade, CRX can send 150 = H for the fill to correct an error. 150 = H is not part of normal operation.
- After 150 = H, the trade does not stand. It does not settle, and it holds no collateral of the seat. Remove it from the books.
- After 150 = 8, there is no trade. The accept moves no collateral.
- CRX sends each fill one time, to the session that sent the accept or the quote.
- A drop-copy session receives the same 150 = F report for each trade of its seat.

Samples: [`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix), [`27-exec-new.fix`](examples/27-exec-new.fix), [`28-exec-fill.fix`](examples/28-exec-fill.fix), [`29-exec-rejected.fix`](examples/29-exec-rejected.fix), [`34-exec-status.fix`](examples/34-exec-status.fix), [`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix), [`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix).

### 7.12 OrderStatusRequest (H), firm to CRX

The firm asks for the state of an accept or of a maker quote. CRX answers with ExecutionReport (8) 150 = I.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 790 | OrdStatusReqID | N | String(128) | A firm ID. See [IDs and repeats](#410-ids-and-repeats). CRX copies it into the answer. |
| 11 | ClOrdID | Y | String(128) | Taker: the AJ ClOrdID. Maker: the own QuoteID. Another form than a firm ID gets Reject (3) 373 = 5. |
| 55 | Symbol | Y | String | |
| 54 | Side | Y | char | |

Answer: 8 150 = I with the current state, from the records of the seat. An unknown ClOrdID gets 8 150 = I, 39 = 8, 103 = 5, code `UNKNOWN_ORDER`, with ClOrdID and 790.

A maker sends H with ClOrdID = its QuoteID. The answer gives the state of the quote:

| 39 OrdStatus | State of the quote |
|---|---|
| `A` | Live. No taker accepted it. Text (58) has code `QUOTE_LIVE`. Also while CRX has no answer to the posting of the quote. |
| `0` | A taker accepted it. CRX waits for the fill. |
| `2` | Filled |
| `C` | The quote ended with no trade |
| `4` | Canceled, or replaced by a later Quote (S) on the same R. See [Quote (S), maker to CRX](#714-quote-s-maker-to-crx). |
| `8` | CRX rejected the quote, or the trade failed |

Samples: [`33-order-status-request.fix`](examples/33-order-status-request.fix), [`34-exec-status.fix`](examples/34-exec-status.fix).

### 7.13 QuoteRequest (R), CRX to maker

CRX asks the maker for a quote. Answer with a Quote (S) before ExpireTime (126), or decline with QuoteRequestReject (AG).

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 131 | QuoteReqID | Y | String(36) | The CRX RFQ ID for the maker seat, a UUID |
| 146 | NoRelatedSym | Y | NumInGroup | `1` |
| →55 | Symbol | Y | String | |
| →167 | SecurityType | Y | String | `FXNDF` |
| →541 | MaturityDate | Y | LocalMktDate | |
| →1079 | MaturityTime | Y | TZTimeOnly | |
| →54 | Side | Y | char | The taker's side. 1 = the taker buys USD: send OfferPx. 2 = the taker sells USD: send BidPx. |
| →38 | OrderQty | Y | Qty | Notional in USD |
| →64 | SettlDate | Y | LocalMktDate | Same as 541 |
| →15 | Currency | Y | Currency | `USD`, the base currency of 55 |
| →62 | ValidUntilTime | Y | UTCTimestamp | The end of the validity of the signed quote: the latest time that its trade can open on Ethereum. UTC, whole seconds. Copy it into ValidUntilTime (62) of the Quote. |
| →126 | ExpireTime | Y | UTCTimestamp | The quote deadline: TransactTime (60) + 5 s, or + half the time from 60 to the RFQ end when that is shorter. A test request uses the RFQ end. CRX can close collection sooner. |
| →60 | TransactTime | Y | UTCTimestamp | RFQ open time |
| →1741 | UpfrontPriceType | C | int | `1`, with 1742 |
| →1742 | UpfrontPrice | C | Price | When the premium is not 0 |
| 58 | Text | C | String(256) | On a maker test request: `TEST_REQUEST: A CRX test request. A signed quote binds as on any request.` |

The quote has two end times:

- The quote binds until the quote end: the earlier of the RFQ end and ValidUntilTime (62). CRX takes an accept of the quote only until the quote end. See [Terms](#24-terms).
- ValidUntilTime (62) ends the validity of the signature. The signature proxy signs the quote with this time.

From CRX to the signature proxy, the R carries RawDataLength (95) and RawData (96) in addition: the signature data of the `Quote`. The signature proxy removes both. See [Maker quote signature](#53-maker-quote-signature).

Sample: [`50a-quote-request-to-engine.fix`](examples/50a-quote-request-to-engine.fix). CRX to the signature proxy: [`50-quote-request-to-maker.fix`](examples/50-quote-request-to-maker.fix).

### 7.14 Quote (S), maker to CRX

The maker quotes the RFQ. CRX answers with AI 297 = 0 when the quote is live, or with AI 297 = 5 and the code.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 131 | QuoteReqID | Y | String(36) | From the R |
| 117 | QuoteID | Y | String(128) | A firm ID. See [IDs and repeats](#410-ids-and-repeats). Unique for each seat. Another value gets Reject (3) 373 = 5. |
| 537 | QuoteType | N | int | 1 = Tradeable. Another value gets AI 297 = 5 with code `QUOTE_NOT_TRADEABLE` or `INVALID_FIELD`. |
| 55 | Symbol | Y | String(7) | Same as the R |
| 167 | SecurityType | N | String | Same as the R: `FXNDF` |
| 541 | MaturityDate | Y | LocalMktDate | Same as the R |
| 1079 | MaturityTime | Y | TZTimeOnly | Same as the R |
| 54 | Side | Y | char | Same as the R: the taker's side |
| 38 | OrderQty | Y | Qty | Same as the R. The full amount only. |
| 64 | SettlDate | N | LocalMktDate | Same as 541 |
| 15 | Currency | Y | Currency | Same as the R: `USD`, the base currency of 55 |
| 1 | Account | N | String(42) | When present, the seat address. Another value gets AI 297 = 5, 300 = 99, code `ACCOUNT_MISMATCH`. |
| 132 | BidPx | C | Price | The rate when Side (54) of the R is 2 |
| 133 | OfferPx | C | Price | The rate when Side (54) of the R is 1 |
| 62 | ValidUntilTime | Y | UTCTimestamp | The end of the validity of the signed quote. Not earlier than ValidUntilTime (62) of the R. |
| 1741 | UpfrontPriceType | C | int | When the R has 1741. Same as the R. |
| 1742 | UpfrontPrice | C | Price | When the R has 1742. Same as the R. |

- Copy Side (54), OrderQty (38), Currency (15), MaturityDate (541), MaturityTime (1079), UpfrontPriceType (1741) and UpfrontPrice (1742) from the R. Set ValidUntilTime (62) to 62 of the R.
- The signature proxy signs these fields and adds CrxSignature (20007). It sets Text (58) to the reason when it does not sign. See [Maker quote signature](#53-maker-quote-signature) and [Unsigned messages](#56-unsigned-messages).
- A field that differs from the R gets AI 297 = 5, 300 = 99, code `QUOTE_TERMS_MISMATCH`. So does a 62 earlier than 62 of the R, and a SettlDate (64) other than 541.
- Send exactly one of BidPx (132) and OfferPx (133).
- A price on the other side gets AI 297 = 5, 300 = 99, code `WRONG_SIDE`.
- A later Quote (S) on the same R replaces the earlier quote of the seat. The signature proxy signs it on the same leg ID. A Quote (S) on a new leg ID ends no quote.
- A second Quote (S) on the same leg waits for the answer to the first. When the later quote is live, CRX ends the earlier quote with AI 297 = 6 (Removed from market). The earlier QuoteID then reads 297 = 6 on QuoteStatusRequest (a) and 39 = 4 on OrderStatusRequest (H).
- A later S on another session of the seat ends the quote with AI 297 = 1.
- A quote with no known outcome stays open until the trade record settles it.
- A quote with AI 297 = 6 can still win. When CRX names it as the winner, it gets 8 150 = 0 and 150 = F.
- A QuoteCancel (Z) on a quote with AI 297 = 6 drops the maker's quote on that leg. The Z gets AI 297 = 1. A live later quote on that leg also ends with AI 297 = 1.
- When CRX rejects a later Quote on one RFQ, it sends AI 297 = 5. The code in Text (58) gives the cause. The earlier quote does not change.
- A Quote on a QuoteID that CRX still holds, with other terms, gets j 380 = 0, code `DUPLICATE`. The first quote does not change.

Sample: [`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix). Answers to a quote that the signature proxy did not sign: [`64-quote-status-unsigned.fix`](examples/64-quote-status-unsigned.fix), [`65-quote-status-life.fix`](examples/65-quote-status-life.fix). Signature proxy to CRX: [`52-quote-to-crx.fix`](examples/52-quote-to-crx.fix), [`63-quote-unsigned.fix`](examples/63-quote-unsigned.fix).

### 7.15 QuoteRequestReject (AG), maker to CRX

The maker declines an RFQ. CRX sends no answer when it takes the decline. A rejected decline gets j with the code.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 131 | QuoteReqID | Y | String(36) | The CRX RFQ ID |
| 658 | QuoteRequestRejectReason | Y | int | 10 = Pass: the maker declines. 2 = Exchange closed. 3 = Quote request exceeds limit: size not offered. 8 = No market for instrument: no price. 99 = Other: with Text `TENOR`, tenor not offered. Other values: no reason. |
| 146 | NoRelatedSym | N | NumInGroup | `1` |
| →55 | Symbol | N | String | |
| 58 | Text | N | String | |

- Decline only before ExpireTime (126). A maker that declines sends no quote on that RFQ.

Sample: [`59-maker-decline.fix`](examples/59-maker-decline.fix).

### 7.16 QuoteStatusReport (AI), CRX to maker

CRX gives the state of a maker quote. It sends the report at the quote and at its end. It also answers QuoteStatusRequest (a).

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 649 | QuoteStatusReqID | C | String(128) | In an answer to QuoteStatusRequest (a), when the request had it |
| 131 | QuoteReqID | C | String(36) | The CRX RFQ ID. On 297 = 9: the QuoteReqID of the Z, when it had one. |
| 117 | QuoteID | Y | String(128) | The maker's QuoteID |
| 55 | Symbol | Y | String | `N/A` on 297 = 9 |
| 60 | TransactTime | Y | UTCTimestamp | The time CRX sends the message |
| 297 | QuoteStatus | Y | int | 0 = Accepted: the quote is live. 1 = Canceled for Symbol: CRX canceled the quote. 5 = Rejected. 6 = Removed from market: a later Quote (S) on the same R replaced it. 7 = Expired. 9 = Quote not found. In an answer to a: 0 = live, won or filled. 5 = rejected, or the trade failed or CRX cancelled it. 6 = replaced. 10 = Pending, while CRX checks the quote. Send H for the trade state. See [OrderStatusRequest](#712-orderstatusrequest-h-firm-to-crx). |
| 58 | Text | C | String(256) | On 297 = 9, on 297 = 7 at the quote end, and on 297 = 5 outside an answer to a |
| 300 | QuoteRejectReason | C | int | On 297 = 5, outside an answer to a. 1 = Unknown symbol. 2 = Exchange closed. 3 = Quote exceeds limit. 4 = Too late to enter. 6 = Duplicate quote. 8 = Invalid price. 9 = Not authorized to quote security. 99 = Other. |

Samples: [`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix), [`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix), [`57-quote-status-canceled.fix`](examples/57-quote-status-canceled.fix), [`58-quote-status-expired.fix`](examples/58-quote-status-expired.fix), [`61-quote-status-answer.fix`](examples/61-quote-status-answer.fix).

A confirmed withdrawal through REST, WebSocket or an account control also sends AI 297 = 1 for each affected FIX quote. A repeated withdrawal sends no second report. A quote that a taker accepted keeps its trade state.

### 7.17 QuoteCancel (Z), maker to CRX

The maker cancels a live quote. The answer depends on the state of the quote.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 117 | QuoteID | Y | String(128) | The maker's QuoteID. A firm ID. See [IDs and repeats](#410-ids-and-repeats). Another value gets Reject (3) 373 = 5. |
| 298 | QuoteCancelType | Y | int | 5 = Cancel the quote in QuoteID. Another value gets Reject (3) 373 = 5. |
| 131 | QuoteReqID | N | String(36) | The CRX RFQ ID |

Answers:

| Case | Answer |
|---|---|
| The quote is live | AI 297 = 1 |
| A taker accepted the quote | j 380 = 0, code `QUOTE_ACCEPTED`. 379 holds the QuoteID. The quote binds and the trade stays valid. |
| The quote got AI 297 = 6, and no cancel answer went out | AI 297 = 1. The Z drops the maker's quote on that leg. See [Quote (S), maker to CRX](#714-quote-s-maker-to-crx). |
| The quote has ended | j 380 = 0, code `QUOTE_NOT_LIVE`. 379 holds the QuoteID. |
| Another session of the seat holds the quote | j 380 = 0, code `QUOTE_OTHER_SESSION`. Text names the SenderCompID that holds it. |
| CRX has no quote with this QuoteID | AI 297 = 9, code `UNKNOWN_QUOTE` |
| QuoteCancelType (298) is not 5 | Reject (3), 373 = 5 |
| CRX posts the quote, or the outcome of the posting is not clear | CRX waits for the outcome. Then it cancels the quote, or answers with its real state as above. The wait continues across a reconnect. CRX answers the Z one time. |

Samples: [`56-quote-cancel.fix`](examples/56-quote-cancel.fix), [`57-quote-status-canceled.fix`](examples/57-quote-status-canceled.fix).

### 7.18 QuoteStatusRequest (a), firm to CRX

The firm asks for the state of a quote. CRX answers with QuoteStatusReport (AI).

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 649 | QuoteStatusReqID | N | String(128) | A firm ID. See [IDs and repeats](#410-ids-and-repeats). Another value gets Reject (3) 373 = 5. CRX copies it into the AI. |
| 117 | QuoteID | Y | String(128) | A CRX quote ID (taker) or the maker's QuoteID. Another form than a firm ID gets Reject (3) 373 = 5. |
| 55 | Symbol | Y | String | |

Answer: AI with the current state, from the records of the seat. An unknown QuoteID gets AI 297 = 9, code `UNKNOWN_QUOTE`.

Samples: [`60-quote-status-request.fix`](examples/60-quote-status-request.fix), [`61-quote-status-answer.fix`](examples/61-quote-status-answer.fix).

### 7.19 SecurityListRequest (x) and SecurityList (y)

The firm asks for the list of markets. CRX answers with SecurityList (y).

SecurityListRequest (x), firm to CRX:

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 320 | SecurityReqID | Y | String(128) | A firm ID. See [IDs and repeats](#410-ids-and-repeats). Another value gets Reject (3) 373 = 5. CRX copies it into the y. |
| 559 | SecurityListRequestType | Y | int | 4 = All securities. 0 = Symbol: the Symbol in 55 only. |
| 55 | Symbol | C | String(7) | With 559 = 0 |

SecurityList (y), CRX to firm:

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 320 | SecurityReqID | Y | String(128) | From the x |
| 322 | SecurityResponseID | Y | String | The trace ID of the answer |
| 560 | SecurityRequestResult | Y | int | 0 = Valid request |
| 146 | NoRelatedSym | Y | NumInGroup | Number of markets |
| →55 | Symbol | Y | String | A live market. A paused market is not in the list. |
| →167 | SecurityType | Y | String | `FXNDF` |
| →15 | Currency | Y | Currency | `USD`, the base currency |
| →562 | MinTradeVol | C | Qty | Minimum notional in USD: `100`. When CRX sets a minimum. |
| →969 | MinPriceIncrement | Y | Float | `0.000001`: the smallest rate step. A rate with more than 6 decimal places gets code `INVALID_PRICE`. |

- One y holds all markets.
- Rates have at most 6 decimal places. See [Message format](#42-message-format).
- When CRX cannot read the markets, it answers with j. 379 holds the SecurityReqID.

Samples: [`39-security-list-request.fix`](examples/39-security-list-request.fix), [`40-security-list.fix`](examples/40-security-list.fix).

### 7.20 BusinessMessageReject (j), CRX to firm

CRX rejects an application message that it cannot process, or a request over a limit. The session continues.

| Tag | Name | Req | Type | Values and notes |
|---|---|---|---|---|
| 45 | RefSeqNum | C | SeqNum | MsgSeqNum of the rejected message. Absent when CRX rejects a request after it started to process it. |
| 372 | RefMsgType | Y | String | |
| 379 | BusinessRejectRefID | C | String | The ID of the rejected request, when CRX knows it. For example QuoteReqID, QuoteID, QuoteRespID, ClOrdID or SecurityReqID. Absent on `UNSUPPORTED_MESSAGE`. |
| 380 | BusinessRejectReason | Y | int | 0 = Other. 1 = Unknown ID. 3 = Unsupported message type. 4 = Application not available. 6 = Not authorized. See [BusinessMessageReject codes](#95-businessmessagereject-codes). |
| 58 | Text | Y | String(256) | Coded Text |

Samples: [`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix), [`36-rate-limited.fix`](examples/36-rate-limited.fix), [`62-business-reject.fix`](examples/62-business-reject.fix).

## 8. Custom tags

CRX keeps tags 20001 to 20099 for its own use. It uses one tag of this range: CrxSignature (20007). The FIX engine sends and receives no custom tag. The signature proxy adds 20007 on the way to CRX.

| Tag | Name | Type | Req | Messages | Value | REST field |
|---|---|---|---|---|---|---|
| 20007 | CrxSignature | String(88) | Y on S from a maker. C on AJ: required when 694 = 1. | S from a maker, AJ | The EIP-712 signature of the seat in canonical base64: `Quote` on the S, `Trade` on the AJ | `sig`, as `0x` and 130 hex |

FIX44-CRX.xml declares the fields and values below in addition to FIX 4.4. A FIX.4.4 session can carry FIX Latest fields and values (EP270). The Origin column gives the extension pack (EP) that added each one, when known. Extension: no FIX version has the field on that message.

FIX44-CRX.xml declares MaturityTime (1079), UpfrontPriceType (1741) and UpfrontPrice (1742) inside NoRelatedSym (146) on R. A stock FIX 4.4 dictionary does not declare them. With that dictionary, QuickFIX C++, QuickFIX/n and QuickFIX/Go end the group at 1079. The engine then reads Side (54) and OrderQty (38) as body fields. Load FIX44-CRX.xml. See [Engine settings](#34-engine-settings) and [Dictionary](#13-dictionary).

| Tag | Name | Type | Req | Origin | Messages | Value | REST field |
|---|---|---|---|---|---|---|---|
| 1079 | MaturityTime | TZTimeOnly | Y on R and S. C on 8. N on AJ. | FIX Latest, EP21. Instrument component. | R (in NoRelatedSym), S, AJ, 8 | The UTC time of day of the settlement time, `HH:MM:SSZ` | `expiry` (Unix ms), with 541 |
| 1741 | UpfrontPriceType | int | N on R from a taker. C on the other messages: with 1742. | FIX Latest, EP119, on 8. Extension on R and S. | R (in NoRelatedSym), S, 8. Not on AJ. | `1` = Percentage of the notional | — |
| 1742 | UpfrontPrice | Price | N on R from a taker. C on the other messages: when the premium is not 0. | FIX Latest, EP119, on 8. Extension on R and S. | R (in NoRelatedSym), S, 8. Not on AJ. | The upfront premium in percent of the notional, for example `0.25` for 25 basis points | `premium_bps` = 1742 × 100 |
| 95, 96 | RawDataLength, RawData | Length, data | Y on R to a maker and on S to a taker | Extension. FIX 4.4 has them on the Logon. | R to a maker, S to a taker | The signature data, base64. The signature proxy removes both. | — |
| 167 | SecurityType | String | Y on R, S to a taker, 8 and y. C on AJ: when 694 = 1. N on S from a maker. | FIX Latest, EP82. FIX 4.4 has the value `FOR` only. | R, S, AJ, 8, y | `FXNDF` = NDF | — |
| 298 | QuoteCancelType | int | Y | FIX Latest, EP21. FIX 4.4 has the values 1 to 4. | Z | `5` = Cancel the quote in QuoteID | — |
| 300 | QuoteRejectReason | int | C: on 297 = 5 | FIX Latest, from FIX 5.0. FIX 4.4 does not have it on AI. | AI to a maker | See [Business reject codes](#94-business-reject-codes). | — |
| 117 | QuoteID | String(128) | C | Extension | 8 | Taker: the CRX quote ID. Maker: the maker's QuoteID. | — |
| 880 | TrdMatchID | String(36) | C: on a fill | FIX Latest, from FIX 5.0. FIX 4.4 does not have it on 8. | 8 | The CRX trade ID, a UUID | — |
| 1056 | CalculatedCcyLastQty | Qty | C: on a fill | FIX Latest, from FIX 5.0. FIX 4.4 does not have the field. | 8 | LastQty × LastPx in the second currency of 55, at its ISO 4217 minor units | — |
| 1603, 1604, 1605 | ApplicationSystemName, ApplicationSystemVersion, ApplicationSystemVendor | String(64) | N | FIX Latest, EP113 | Logon (A) from the firm | 1603 and 1605: the FIX engine. 1604: the version of the signature proxy. | — |
| 969 | MinPriceIncrement | Float | Y | FIX Latest | y (in NoRelatedSym) | `0.000001` | — |

## 9. Rejects and codes

### 9.1 Which message rejects

| Problem | Answer |
|---|---|
| A bad session field, a malformed message | Reject (3) with SessionRejectReason (373) |
| An unsupported MsgType, a rate limit, or CRX cannot answer | BusinessMessageReject (j) with BusinessRejectReason (380) |
| A rejected QuoteRequest (R) | QuoteRequestReject (AG) with QuoteRequestRejectReason (658) |
| A rejected maker Quote (S) | QuoteStatusReport (AI) 297 = 5 with QuoteRejectReason (300) |
| A rejected QuoteCancel (Z) | See [QuoteCancel](#717-quotecancel-z-maker-to-crx): AI 297 = 9, j or Reject (3) |
| A rejected accept, AJ 694 = 1 | ExecutionReport (8) 150 = 8 with OrdRejReason (103) |
| A rejected Logon, a session end | Logout (5) |

CRX checks an inbound message in the order below. The first check that fails gives the answer.

| Step | Check | Answer when the check fails |
|---|---|---|
| 1 | Size, BeginString (8) and MsgSeqNum (34) | A Logout with code `MESSAGE_TOO_LARGE`, `BEGIN_STRING` or `SEQ_INVALID` |
| 2 | SenderCompID (49) and TargetCompID (56) | Reject (3) 373 = 9, then Logout with code `COMP_ID_PROBLEM` |
| 3 | MsgSeqNum (34) against the expected number | Too low: Logout with code `SEQ_NUM_TOO_LOW`. Too high: ResendRequest (2). |
| 4 | A tag with no value | Reject (3) 373 = 4 |
| 5 | SendingTime (52) and OrigSendingTime (122) | Reject (3) 373 = 1, 6 or 10. After 373 = 10, Logout with code `SENDING_TIME_ACCURACY`. |
| 6 | Each value is UTF-8 | Reject (3) 373 = 6 |
| 7 | No application message on a drop-copy session | j 380 = 3, code `UNSUPPORTED_MESSAGE` |
| 8 | Account (1) on R, S and AJ. CRX ignores Account (1) on the other messages. | AG, AI or 8 with code `ACCOUNT_MISMATCH` |
| 9 | The firm IDs, QuoteRespType (694) and QuoteCancelType (298) | Reject (3) 373 = 5 |
| 10 | The order and the count of the NoRelatedSym (146) group | Reject (3) 373 = 15 or 16 |
| 11 | The fields of the message | AG, AI or 8 with the code |
| 12 | The trading rules of CRX | AG, AI, 8 or j with the code |

### 9.2 Text format

Each Text (58) from CRX has this form:

```text
<CODE>: <sentence> (trace <id>)
```

- `<CODE>` is the reject code, in `UPPER_SNAKE` case. It is the text before the first `:`. CRX always writes `<CODE>: `. On a Reject (3), the code names the SessionRejectReason.
- `<sentence>` is a sentence from the row of the code in this section.
- `<id>` is the trace ID.
- Text (58) from CRX has at most 256 characters.
- CRX uses a closed set of codes. It sends only the codes of this section.
- Each code has one sentence without values. Some codes also have sentences with values. A name in braces, for example `{min}`, is a value. Text carries the first sentence with values whose every value CRX knows, else the sentence without values.
- A session check gives one sentence for each cause. The tables of [Session Reject values](#93-session-reject-values) and [Logout codes](#96-logout-codes) give them.
- `TEST_REQUEST` is the one code outside a reject or a report. It is in Text (58) of the R of a CRX test request, with no trace ID.
- A refusal of the CRX trading service with no code in this section goes out as `SERVICE_UNAVAILABLE`. At the Logon, it goes out as `UNAUTHORIZED`.
- Use the code in the logic of the FIX engine. Do not parse the sentence. Show Text to operators.
- Text never names internal components.
- Text (58) from the signature proxy has the same form, with no trace ID.
- For CRX support, give the trace ID, the CompIDs, and the MsgSeqNum, MsgType and SendingTime (52) of the message.

### 9.3 Session Reject values

A rejected message uses its MsgSeqNum. CRX does not ask for it again. CRX sends only the values of 373 in this table.

| 373 | Name | Code in Text | Cause | Text sentence | Then | Retry |
|---|---|---|---|---|---|---|
| 1 | Required tag missing | `REQUIRED_TAG_MISSING` | A required tag is absent. | `Required tag {tag} is missing.` For a header field: `{Name} missing.` | The session continues. | After a correction |
| 4 | Tag specified without a value | `TAG_WITHOUT_VALUE` | A tag has an empty value. | `Tag {tag} has no value.` | The session continues. | After a correction |
| 5 | Value is incorrect | `VALUE_INCORRECT` | A firm ID breaks the firm ID rule of [IDs and repeats](#410-ids-and-repeats). Or QuoteRespType (694) is not 1 or 6, or QuoteCancelType (298) is not 5. Or NewSeqNo (36) is not above MsgSeqNum. Or BeginSeqNo (7) is above the last MsgSeqNum that CRX sent. | For a firm ID, 694 or 298: `A value is not valid.` For 36: `NewSeqNo must exceed MsgSeqNum.` For 7: `BeginSeqNo {n} is above the last MsgSeqNum sent, {last}.` | The session continues. | After a correction |
| 6 | Incorrect data format | `INCORRECT_DATA_FORMAT` | A time, number or flag has a bad format, or a value is not UTF-8. | `Tag {tag} has a value in the wrong format.` For a header field: `{Name} format invalid.` | The session continues. | After a correction |
| 9 | CompID problem | `COMP_ID_PROBLEM` | 49 or 56 is not the CompID of the session. | `CompID problem.` | Logout | After a correction |
| 10 | SendingTime accuracy problem | `SENDING_TIME_ACCURACY` | 52 is more than 120 s from CRX time, or 122 is later than 52. | `SendingTime accuracy problem.` Or: `OrigSendingTime later than SendingTime.` | Logout | After a clock correction |
| 15 | Repeating group fields out of order | `GROUP_ORDER` | A group field is out of order. | `Tag {tag} is out of order in its repeating group.` | The session continues. | After a correction |
| 16 | Incorrect NumInGroup count | `INCORRECT_NUM_IN_GROUP` | A group count does not match the group. | `Tag {tag} has an incorrect NumInGroup count.` | The session continues. | After a correction |

- PossDupFlag (43) = Y with OrigSendingTime (122) later than SendingTime (52) gets Reject 373 = 10, then Logout `SENDING_TIME_ACCURACY`.
- 43 = Y without 122 gets Reject 373 = 1.

### 9.4 Business reject codes

Retry column:

- Yes: send a new request with a new ID, after the wait in Text.
- No: correct the cause first.
- Never: the result is final.

| Code | Cause | AG 658 | AI 300 | 8 103 | Retry | Sentence without values | Sentences with values | Correction |
|---|---|---|---|---|---|---|---|---|
| `NO_QUOTE` | No maker quoted in the window. | 8 | — | — | Yes | `No dealer quoted this request.` | — | Send a new R later, or with other terms. |
| `MISSING_FIELD` | A required field is absent. | 99 | 99 | 99 | No | `A required field is absent.` | `{field} is required.` | Add the field. See [Messages](#7-messages). |
| `INVALID_FIELD` | A field has a value that CRX does not take. This includes a CrxSignature (20007) that is not 88 characters of canonical base64. | 99 | 99 | 99 | No | `A field has a value that CRX does not take.` | `{field} has a value that CRX does not take.` | Correct the field. See [Messages](#7-messages). |
| `INVALID_REQUEST` | NoRelatedSym (146) is not 1, QuoteRequestType (303) is 2, or QuoteType (537) is not 1. | 99 | — | — | No | `The request has a form that CRX does not take.` | `{field} sets a request form that CRX does not take.` | Send one instrument, 303 = 1 or no 303, and 537 = 1. |
| `INVALID_QUANTITY` | OrderQty is not positive or has more than 6 decimal places. | 99 | — | — | No | `OrderQty is not positive or has more than 6 decimal places.` | — | Correct OrderQty. |
| `INVALID_PRICE` | A quote has no rate, two rates, or more than 6 decimal places. | — | 8 | — | No | `The quote does not carry exactly one rate with at most 6 decimal places.` | — | Send exactly one rate. |
| `UNKNOWN_SYMBOL` | CRX does not list the Symbol, or it does not have the form `USD/MXN`. | 1 | 1 | 1 | No | `The Symbol is not a CRX market. Use a Symbol from SecurityList (y).` | — | Use a Symbol from SecurityList (y). |
| `BAD_REQUEST` | The settlement time is outside 1 hour to 90 days. | 3 | 3 | 3 | No | `A field is not valid.` | `The settlement time is {t} from now, outside {min} to {max}.`<br>`The settlement time is outside {min} to {max}.` | Use a time in the range that Text gives. |
| `BAD_REQUEST` | Another field is not valid. | 99 | 99 | 99 | No | `A field is not valid.` | — | Correct the field. |
| `MATURITY_MISMATCH` | SettlDate (64) is not MaturityDate (541). Or on an accept, 541, 64 or 1079 differs from the S. | 99 | — | 99 | No | `SettlDate (64), MaturityDate (541) or the accept terms do not match.` | `{field} does not match the settlement time.` | Send 64 equal to 541. On an accept, copy 541 and 1079 from the S. |
| `CURRENCY_NOT_BASE` | Currency (15) is not the base currency of Symbol (55). | 99 | — | 99 | No | `Currency (15) is not the base currency of the Symbol.` | — | Send the base currency, for example `USD` for `USD/MXN`. Or omit 15. |
| `PLATFORM_PAUSED` | CRX paused trading. | 2 | 2 | 2 | Yes | `CRX paused trading. Send again after the pause.` | — | Send again after the pause. |
| `MARKET_PAUSED` | CRX paused the market. | 2 | 2 | 2 | Yes | `CRX paused the market. Send again after the pause.` | `CRX paused the market {pair}. Send again after the pause.` | Send again after the pause. |
| `NOTIONAL_BELOW_MINIMUM` | OrderQty is below 100 USD. | 3 | 3 | 3 | No | `OrderQty is below the minimum trade size.` | `OrderQty is below the minimum of {min} {ccy}.` | Increase OrderQty. |
| `NOTIONAL_ABOVE_MAXIMUM` | OrderQty is above the maximum. | 3 | 3 | 3 | No | `OrderQty is above the maximum trade size.` | `OrderQty is above the maximum of {max} {ccy}.` | Decrease OrderQty. |
| `EXPIRY_OUTSIDE_HOURS` | The settlement time falls in a market closure, or in the first 15 minutes after a reopen. | 3 | 3 | 3 | No | `The settlement time falls in a market closure.` | `The settlement time falls in a market closure. The earliest time is {t}.`<br>`The settlement time falls outside the market hours {open} to {close} {zone}.` | Use the earliest time in Text or later. |
| `EXPIRY_PAST_FENCE` | The settlement time is after the latest date that CRX takes. | 3 | 3 | 3 | No | `The settlement time is after the latest time that CRX takes.` | `The settlement time is after {t}, the latest time that CRX takes.` | Use an earlier time. |
| `EXPIRY_AFTER_DELIST` | The settlement time is after the last trading time of the market. | 3 | 3 | 3 | No | `The settlement time is after the last trading time of the market.` | `The settlement time is after {t}, the last trading time of the market.` | Use an earlier time. |
| `QUOTE_WINDOW_CLOSED` | The maker quote reached CRX after ExpireTime (126). | 4 | 4 | 4 | Never | `The quote reached CRX after ExpireTime (126) of the request.` | — | Quote the next RFQ sooner. |
| `QUOTE_EXPIRED` | The accept reached CRX after ValidUntilTime (62). | 4 | 4 | 4 | Yes | `The quote ended before an accept reached CRX.` | — | Send a new R. |
| `RFQ_EXPIRED` | The RFQ ended. | 4 | 4 | 4 | Yes | `The RFQ ended. Send a new QuoteRequest (R).` | — | Send a new R. |
| `ACCOUNT_PAUSED` | CRX paused trading for the account. | 6 | 9 | 99 | No | `Trading is paused for the account. Contact CRX support.` | — | Contact CRX support. |
| `ELIGIBILITY_EXPIRED` | The account eligibility representation expired. | 6 | 9 | 99 | No | `The eligibility representation of the account expired. Renew it through CRX.` | — | Renew the representation through CRX. |
| `NOT_WHITELISTED` | CRX did not approve the seat for this action. | 6 | 9 | 99 | No | `CRX did not approve the seat for this action. Contact CRX support.` | — | Contact CRX support. |
| `SEAT_CANNOT_SIGN` | The seat is a contract wallet. | 6 | 9 | 99 | No | `The seat is a contract wallet. Use an EOA or MPC seat.` | — | Use an EOA or MPC seat. |
| `UNAUTHORIZED` | CRX rejected the API session of the seat. | 6 | 9 | 99 | No | `CRX did not accept the credentials of the seat. Log on again with a new signature.` | — | Log on again. |
| `ACCOUNT_MISMATCH` | Account (1) is not the seat address. | 6 | 99 | 15 | No | `Account (1) is not the seat address.` | — | Send the seat address, or omit Account. |
| `WRONG_SIDE` | The maker priced the other side. | — | 99 | — | No | `The quote prices the other side of the request.` | — | Send OfferPx when 54 = 1 and BidPx when 54 = 2. |
| `QUOTE_TERMS_MISMATCH` | A maker Quote field differs from the R: 55, 167, 541, 1079, 54, 38, 64, 15, 1741 or 1742. Or ValidUntilTime (62) is earlier than 62 of the R. | — | 99 | — | No | `A Quote field differs from the QuoteRequest (R).` | `{field} must be {value}, as on the QuoteRequest (R).` | Copy the fields and 62 from the R. |
| `QUOTE_NOT_TRADEABLE` | The maker Quote has a QuoteType (537) other than `1`. | — | 99 | — | No | `QuoteType (537) is not 1.` | — | Send 537 = 1, or omit 537. |
| `QUOTE_MISMATCH` | An accept field differs from the S. 103 = 13 when OrderQty differs. | — | — | 99 | No | `An accept field differs from the Quote (S).` | `{field} must be {value}, as on the Quote (S).`<br>`{field} differs from the Quote (S).` | Copy the fields from the S. |
| `INVALID_SIGNATURE`, `SIGNATURE_INVALID` | The signature does not match the seat. Or its 88 characters do not decode to 65 bytes with v 27 or 28. | 99 | 99 | 99 | No | `The signature does not match the seat.` | — | Check the signature proxy domain and key. |
| `SIGNATURE_MISSING` | The message has no CrxSignature (20007) and no signature proxy code in Text (58). | — | 99 | 99 | No | `The message carries no signature.` | — | Send the message through the signature proxy. |
| A signature proxy code | The signature proxy did not sign. See [Unsigned messages](#56-unsigned-messages). | — | 99 | 99 | No | `The signature proxy did not sign the message.` | — | Read the signature proxy log. |
| `QUOTE_FORMAT_OUTDATED` | The quote uses a previous signature format. | — | 99 | — | No | `The quote uses a previous signature format. Update the signature proxy.` | — | Update the signature proxy. |
| `NONCE_COLLISION` | The maker used a QuoteID or a nonce again. | — | 6 | — | No | `The QuoteID or the nonce is in use. Send the quote under a new QuoteID.` | — | Use a new QuoteID. |
| `LEG_ID_TAKEN` | The maker used a leg ID again. | — | 6 | — | No | `The leg ID is in use. Send a new Quote (S) through the signature proxy.` | — | Let the signature proxy make a new leg ID. |
| `DUPLICATE` | The quote already has an accept under another ClOrdID. Or CRX already holds this request with other content. | 99 | 6 | 6 | No | `The ID is in use with other terms. Send the request under a new ID.` | `{field} is in use with other terms. Send the request under a new ID.` | Send a new R. |
| `INSUFFICIENT_COLLATERAL` | The seat has not enough free collateral. | 99 | 99 | 99 | No | `The seat has not enough free collateral.` | `Free collateral is {available} USD; the trade needs {required} USD.` | Deposit USDC or reduce OrderQty. |
| `RATE_OUT_OF_BAND` | The quote is too far from the market price. | — | — | 99 | Yes | `The rate is too far from the market price.` | `The rate {rate} is more than {band} bps from the market price {mark}.` | Send a new R. |
| `UNKNOWN_RFQ` | The QuoteReqID is not an RFQ that CRX sent to this session. CRX sends a maker no RFQ of its own firm, so a quote on such an RFQ gets this code. | — | 99 | — | No | `QuoteReqID is not an RFQ that CRX sent to this session.` | — | Copy QuoteReqID from the R. |
| `UNKNOWN_QUOTE` | CRX has no quote with this QuoteID for the seat. On a Z or an a: AI 297 = 9 with no 300. | — | — | 99 | No | `CRX has no quote with this QuoteID for the seat.` | — | Check the QuoteID. |
| `UNKNOWN_ORDER` | CRX has no accept with this ClOrdID for the seat. | — | — | 5 | No | `CRX has no accept with this ClOrdID for the seat.` | — | Check the ClOrdID. |
| `QUOTE_NOT_LIVE` | The maker canceled the quote, or the quote expired. | — | — | 99 | Yes | `The quote is no longer live.` | — | Send a new R. |
| `QUOTE_PASSED` | The taker passed this quote. | — | — | 99 | Yes | `The taker passed this quote.` | — | Send a new R. |
| `REFUSED` | The trade did not open. | — | — | 99 | Yes | `The trade did not open. Send a new QuoteRequest (R).` | — | Send a new R. |
| `TRADE_STALE` | The signature data of the quote changed before the accept. The terms stand. An accept on an older RFQ after the quote of a newer RFQ arrives gets this code. | — | — | 99 | Yes, on the new S | `The signature data of the quote changed before the accept. Accept the new Quote (S).` | — | Accept the new Quote (S) that CRX sends next, with its new QuoteID. Accept one RFQ at a time. |
| `SERVICE_UNAVAILABLE` | CRX cannot present a quote for the request, or cannot take a quote or an accept now. | 99 | 99 | 99 | Yes | `The service is not available.` | — | Send the request again later. After an AJ, send H before any new accept. |
| `CONFLICT` | The request conflicts with a CRX rule. | 99 | 99 | 99 | No | `The request conflicts with a CRX rule.` | — | Give the trace ID to CRX support. |
| `RATE_LIMITED` | The request is over a limit. See [Rate limits](#105-rate-limits). | 3 | 99 | 99 | Yes | `The request limit is reached.` | See [BusinessMessageReject codes](#95-businessmessagereject-codes). | Wait the time in Text. |

Status and report codes:

| Code | Message | Cause | Retry | Sentence |
|---|---|---|---|---|
| `QUOTE_LIVE` | 8 150 = I to a maker | The quote is live. No taker accepted it. | — | `The quote can still trade: no taker accepted it.` |
| `QUOTE_EXPIRED` | AI 297 = 7 | The quote reached its end with no accept or no trade. A maker quote that did not win gets this code at the quote end. | Never | `The quote ended before an accept reached CRX.` |
| `QUOTE_LOST` | AI 297 = 7 to a maker | Another quote of the same seat won the RFQ. Each other live quote of the seat on that RFQ ends with this code. | Never | `Another quote won the request.` |
| `TEST_REQUEST` | R to a maker | The R is a CRX test request. Text has no trace ID. | — | `A CRX test request. A signed quote binds as on any request.` |
| `TRADE_CANCELLED` | 8 150 = H | CRX refused or took back the trade after the fill, before the settlement time. | Never | `The trade was refused after its fill. It does not stand.` |

AI 297 = 6 ends a quote that a later Quote (S) of the seat replaced. It has no Text.

### 9.5 BusinessMessageReject codes

| Code | 380 | Cause | Retry | Sentence without values | Sentences with values | Correction |
|---|---|---|---|---|---|---|
| `RATE_LIMITED` | 0 | The request is over a rate limit. 379 holds the request ID. | Yes | `The request limit is reached.` | See the table below. | Wait the time in Text. |
| `QUOTE_ACCEPTED` | 0 | A Z on a quote that a taker accepted, or a pass on a quote that the taker accepted. 45 and 379 name the message and its QuoteID or QuoteRespID. A Z answered after a wait has no 45. | Never | `The quote was accepted and binds.` | — | None. The trade stays valid. |
| `QUOTE_OTHER_SESSION` | 0 | A Z or a pass on a quote that another session of the seat holds. Text names that SenderCompID. | No | `Another session of the seat holds the quote.` | `SenderCompID {comp_id} of the seat holds the quote. Send the message on that session.` | Send the message on that session. |
| `QUOTE_NOT_LIVE` | 0 | A Z on a quote that has ended, or a pass on a quote past 62, passed or expired. 45 and 379 name the message and the ID. A Z answered after a wait has no 45. | Never | `The quote is no longer live.` | — | None. |
| `DUPLICATE` | 0 | An ID is in use with other terms: QuoteReqID, QuoteID, QuoteRespID or ClOrdID. 45 and 379 name the message and the ID. The first request and its state do not change. | No | `The ID is in use with other terms. Send the request under a new ID.` | `{field} is in use with other terms. Send the request under a new ID.` | Send the request under a new ID. |
| `UNKNOWN_RFQ` | 1 | A decline (AG) on an RFQ that CRX did not send to the session. 379 holds the QuoteReqID. | No | `QuoteReqID is not an RFQ that CRX sent to this session.` | — | Decline only an R that the session received. |
| A code of a refused decline | 0, 1 or 6 | CRX refused the decline, for example with `QUOTE_WINDOW_CLOSED`. 380 = 6 when the seat is not authorized. | No | See [Business reject codes](#94-business-reject-codes). | See [Business reject codes](#94-business-reject-codes). | Read Text. |
| `UNSUPPORTED_MESSAGE` | 3 | CRX does not take this MsgType, for example NewOrderSingle (D). Or a drop-copy session sent an application message. | No | `CRX does not take this MsgType.` | — | Accept a quote with QuoteResponse (AJ). Send no application message on a drop-copy session. |
| `SERVICE_UNAVAILABLE` | 4 | CRX cannot answer now, or it cannot record the answer to H or a. The session stays up. | Yes | `The service is not available.` | — | Check the state with a, H or the REST API. Then send again. After an AJ, send H before any new accept. |

`RATE_LIMITED` Text names the limit. The sentences with values, first to last:

| Limit | Sentence with values |
|---|---|
| Accepted trades that await confirmation, for each firm | `The firm holds {held} accepted trades that await confirmation; the limit is {held_max}. Wait {wait} s.` |
| Failed trades in one clock hour, for each firm | `The firm has {failed} failed trades this hour; the limit is {failed_max}. Wait {wait} s.` |
| Notional of the live RFQs, for each firm | `The firm's live RFQs hold {rfq_usd} USD; the limit is {rfq_max} USD. Wait {wait} s.` |
| Request rate of the seat. See [Rate limits](#105-rate-limits). | `The limit is {per_min} requests a minute. Wait {wait} s.` |
| A limit that CRX does not name | `The request limit is reached. Wait {wait} s.` |

An AJ with 694 = 1 gets `RATE_LIMITED` and `SERVICE_UNAVAILABLE` in 8 150 = 8, 103 = 99. It gets no j for these codes. The exception: an AJ that CRX cannot record gets j 380 = 4, code `SERVICE_UNAVAILABLE`. CRX makes no trade, and H answers `UNKNOWN_ORDER`.

### 9.6 Logout codes

Sequence numbers column:

- No change: CRX refused the Logon. The Logout has MsgSeqNum 1. CRX stores nothing for it, and the sequence numbers of both sides do not change.
- Continue: at the next Logon, both sides continue from their last MsgSeqNum.
- Start at 1: at the next Logon, both sides start at 1.

`SEQ_NUM_TOO_LOW` is the one exception. Its Logout has the next MsgSeqNum of CRX, and the MsgSeqNum that CRX expects from the firm does not change. Before the Logon, a BodyLength (9) above 8,192 closes the connection with no Logout.

| Code | Cause | Text sentence | Retry | Sequence numbers |
|---|---|---|---|---|
| `LOGON_BEGIN_STRING` | BeginString (8) is not `FIX.4.4`. | `BeginString must be FIX.4.4.` | After a correction | No change |
| `LOGON_COMP_ID_UNKNOWN` | CRX has no record of the SenderCompID, or TargetCompID is wrong for the role. | `SenderCompID or TargetCompID is not on record for CRX.` With values: `TargetCompID (56) must be {target} for this SenderCompID.` Or: `TargetCompID is not a CompID of this acceptor.` | After a correction | No change |
| `LOGON_ADDRESS_INVALID` | Username (553) is absent, or it is not `0x` and 40 hex characters. | `Username (553) must be the signing address: 0x and 40 hex digits.` | After a correction | No change |
| `LOGON_SIGNATURE_INVALID` | RawDataLength (95) is not 88. Or RawData (96) is not canonical base64 of 88 characters. Or it does not decode to 65 bytes with v 27 or 28. Or the signature does not match Username (553). | `The signature does not recover to the signing address.` | After a correction | No change |
| `LOGON_TIME_INVALID` | SendingTime (52) is not valid. | `SendingTime (52) is not valid.` Or: `SendingTime is missing or not valid.` | After a correction | No change |
| `LOGON_TIME_AHEAD` | SendingTime (52) is more than 5 s ahead of CRX time. | `SendingTime (52) is more than 5 s ahead of CRX time.` | After a clock correction | No change |
| `LOGON_IP_NOT_ALLOWED` | The source address is not on the allowlist of this SenderCompID. | `The source address is not on the allow list of this SenderCompID.` | After a correction | No change |
| `LOGON_SESSION_ACTIVE` | The SenderCompID has a live session. | `The session is logged on from another connection.` | After the other session ends | No change |
| `LOGON_HEART_BT_INT` | HeartBtInt (108) is outside 5 to 60. | `HeartBtInt must be 5 to 60 seconds.` | After a correction | No change |
| `LOGON_ENCRYPT_METHOD` | EncryptMethod (98) is not `0`. | `EncryptMethod must be 0.` | After a correction | No change |
| `LOGON_RESET_SEQ_NUM` | ResetSeqNumFlag (141) = Y with MsgSeqNum other than 1, or 141 is not Y or N. | `MsgSeqNum must be 1 with ResetSeqNumFlag Y.` Or: `ResetSeqNumFlag must be Y or N.` | After a correction | No change |
| `SENDING_TIME_ACCURACY` | SendingTime (52) is more than 120 s from CRX time. | At the Logon: `SendingTime differs from CRX time by more than 120 s.` In a session: the Reject (3) sentence. | After a clock correction | At the Logon: no change. In a session: continue. |
| `LOGON_SEQ_INVALID` | The Logon MsgSeqNum (34) is absent or not a valid number. | `MsgSeqNum is missing or not valid.` | After a correction | No change |
| `LOGON_RESET_WINDOW` | The Logon arrived during the daily reset. | `The daily reset is in progress. Log on from {t}.` | From the time in Text | No change |
| `SEQ_NUM_TOO_LOW` | MsgSeqNum is lower than expected, with no PossDupFlag. | `MsgSeqNum too low, expecting {n} but received {m}.` | After a correction | See the exception above |
| `SEQ_INVALID` | A message after the Logon has no valid MsgSeqNum (34). | `MsgSeqNum is missing or not valid.` | After a correction | Continue |
| `BEGIN_STRING` | A message after the Logon has a BeginString (8) other than `FIX.4.4`. | `BeginString must be FIX.4.4.` | After a correction | Continue |
| `MESSAGE_TOO_LARGE` | A message is longer than 8,192 bytes, or its BodyLength (9) gives more after the Logon. | `Message size exceeds the limit of 8192 bytes.` | After a correction | At the Logon: no change. In a session: continue. |
| `UNAUTHORIZED` | CRX rejected the Logon signature. The address that signs is not the seat or a login key on record for the seat. Or the timestamp is out of range, or CRX took the signature before. A refusal of the Logon with no code in this table also gets this code. | `CRX did not accept the credentials of the seat. Log on again with a new signature.` | Yes, with a new signature | No change |
| `ACCOUNT_PAUSED` | CRX paused trading for the account. | `Trading is paused for the account. Contact CRX support.` | After CRX support confirms access | No change |
| `ELIGIBILITY_EXPIRED` | The account eligibility representation expired. | `The eligibility representation of the account expired. Renew it through CRX.` | After renewal through CRX | No change |
| `NOT_WHITELISTED` | CRX did not approve the seat. | `CRX did not approve the seat for this action. Contact CRX support.` | No. Contact CRX support. | No change |
| `SEAT_CANNOT_SIGN` | The seat is a contract wallet. | `The seat is a contract wallet. Use an EOA or MPC seat.` | No | No change |
| `LOGON_SIGNATURE_MISSING` | The Logon has no RawData (96): the signature proxy did not sign it. The signature proxy log gives the reason. | `The Logon carries no signature.` | After a correction | No change |
| `LOGON_RATE` | More than 5 accepted Logons in 60 s for the SenderCompID. Text gives no wait time. | `More than 5 accepted Logons in 60 s for this SenderCompID. Wait before the next Logon.` | After 60 s | No change |
| `RATE_LIMITED` | The seat is over a request limit at the Logon. | See [BusinessMessageReject codes](#95-businessmessagereject-codes). | After the wait in Text | No change |
| `SERVICE_UNAVAILABLE` | CRX cannot check the Logon now. | `The service is not available.` Or: `The session is not available. Log on again.` | Yes, with the reconnect wait | No change |
| `HEARTBEAT_TIMEOUT` | No message after a TestRequest. | `No message arrived within the heartbeat interval. Log on again.` | Yes | Continue |
| `GAP_QUEUE_FULL` | More than 10,000 messages wait above a gap. | `Too many messages are held above a sequence gap. Log on again.` | Yes, then fill the gap | Continue |
| `LOGON_ON_LIVE_SESSION` | A Logon arrived on a live session. | `A Logon arrived on a logged-on session.` | Yes | Continue |
| `COMP_ID_PROBLEM` | A message had a wrong CompID. | `SenderCompID or TargetCompID does not match the session.` | After a correction | Continue |
| `ERROR_RATE` | More than 50 rejects in 60 s. | `More than 50 rejects in 60 s. Log on again.` | After a correction | Continue |
| `LOGOUT_ACK` | The answer to a firm Logout. | `Logout acknowledged.` | Yes | Continue |
| `DAILY_RESET` | Daily reset at 17:00 New York time. | `The session ends for the daily reset. Log on from {t}.` | Yes, from 17:00:30 with MsgSeqNum 1 | Start at 1 |
| `SESSION_RENEWAL` | The API session of the seat ends in 10 minutes. | `The session ends for signature renewal. Log on again.` | Yes, after 5 s | Continue |
| `SESSION_EXPIRED` | The API session of the seat ended early, or the FIX session has none, for example after a CRX restart. | `The session ended. Log on again.` | Yes, after 5 s | Continue |
| `GATEWAY_STOP` | CRX stops the FIX service. | `The gateway is stopping. Log on again.` | Yes, with the reconnect wait | Continue |

Examples of Text:

```text
NO_QUOTE: No dealer quoted this request. (trace <id>)
QUOTE_EXPIRED: The quote ended before an accept reached CRX. (trace <id>)
NOTIONAL_ABOVE_MAXIMUM: OrderQty is above the maximum of 100000000 USD. (trace <id>)
UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace <id>)
QUOTE_WINDOW_CLOSED: The quote reached CRX after ExpireTime (126) of the request. (trace <id>)
SEQ_NUM_TOO_LOW: MsgSeqNum too low, expecting 20 but received 17. (trace <id>)
```

## 10. Trading rules

### 10.1 Markets

- USD/MXN, USD/BRL and USD/PHP. SecurityList (y) gives the live markets.
- CRX rejects a request for any other Symbol.
- A paused market is not in SecurityList. A request for it gets AG 658 = 2.
- A rate has at most 6 decimal places. SecurityList (y) gives MinPriceIncrement (969) = 0.000001 for each market.

### 10.2 Quotes

- Every maker receives every RFQ, with two exceptions. A maker does not receive RFQs from its own firm, or RFQs that its free collateral cannot cover.
- A maker cannot read an RFQ of its own firm. A Quote on such an RFQ gets AI 297 = 5. The signature proxy gives code `UNKNOWN_QUOTE_REQUEST`. A Quote signed without the signature proxy gets code `UNKNOWN_RFQ`.
- CRX sends no R after its ExpireTime (126).
- The R tells the maker the taker's side. The maker prices that side only.
- Submit by ExpireTime (126). CRX decides whether collection is still open. A late quote gets AI 297 = 5, code `QUOTE_WINDOW_CLOSED`. See [Timing](#58-timing).
- A later Quote (S) on the same R replaces the earlier quote of the maker. See [Quote (S), maker to CRX](#714-quote-s-maker-to-crx).
- The taker receives one quote: the best rate for its side. When two rates are equal, the earlier quote wins.
- CRX sends no other quote when the first one expires.
- A maker quote that does not win ends with AI 297 = 7, code `QUOTE_EXPIRED`, at the quote end. CRX does not tell a maker which quote won.
- CRX does not select a quote that is too far from the market price.
- A quote binds until the quote end. There is no last look. The signed quote of the maker is its signature on the trade. When the taker accepts, the trade opens. The maker cannot decline it.
- A maker can cancel a quote with QuoteCancel (Z) only before a taker accepts it.
- A quote is for the full OrderQty. A trade fills all of it or none of it.

### 10.3 Settlement time

| Item | Rule |
|---|---|
| Earliest | 1 hour after the request |
| Latest | 90 days after the request |
| Market closures | CRX takes a time in a market closure only when it can price that time. It rejects a time in the first 15 minutes after a reopen. `GET /markets?chain=ethereum` names the next rejected period for each market. |
| Fixing | At the settlement time in MaturityDate (541) and MaturityTime (1079). The taker sets this time. |
| Settlement date | MaturityDate (541). SettlDate (64) holds the same date. |

Fixing source:

| Market | Fixing source |
|---|---|
| USD/MXN | The Pyth Network spot price for USD/MXN |
| USD/BRL | The Pyth Network spot price for USD/BRL |
| USD/PHP | The Pyth Network spot price for USD/PHP |

- Each trade settles on the first spot price that Pyth Network publishes in the hour after its settlement time.
- With no Pyth price in that hour, CRX proposes a manual price. The manual price is public for 2 hours before it is final.
- The fixing source is not an EMTA Annex A rate source. CRX sends no RateSource fields.
- CRX sends no FIX message at the fixing or at settlement. Each side reads the fixing price and the settlement amount of each trade through the REST or WebSocket API. A manual price shows there too.

### 10.4 Size and collateral

- Minimum notional: 100 USD. A maximum can apply. Text gives it.
- Collateral: Circle USDC on the seat, on Ethereum (chain 1).
- CRX checks the free collateral of the taker at the request and at the accept.
- An accept that gets 150 = 8 moves no collateral. A trade that gets 150 = H does not settle and holds no collateral.
- The margin rules of the REST API apply to each trade.

### 10.5 Rate limits

The limits apply to each seat. FIX, REST and WebSocket share them. Rejected requests count.

| Group | FIX messages | Burst | Per minute |
|---|---|---|---|
| RFQ open | QuoteRequest (R) | 10 | 20. Also 120 across all seats. |
| Quote and accept | Quote (S), QuoteCancel (Z), QuoteResponse (AJ) 694 = 1, maker QuoteRequestReject (AG) | 120 | 600 |
| Trade feed and market list | SecurityListRequest (x), and the trade feed reads that CRX makes for the seat | 60 | 300 |
| No limit | QuoteStatusRequest (a), OrderStatusRequest (H), QuoteResponse (AJ) 694 = 6, session messages | — | — |

- When the seat has a live session, CRX reads the trade feed of the seat one time each second. These 60 reads each minute come from the trade feed budget.
- A request over a limit gets j 380 = 0, code `RATE_LIMITED`. BusinessRejectRefID (379) holds the request ID. Text names the limit, its number and the wait.
- An AJ over a limit gets 8 150 = 8, 103 = 99, code `RATE_LIMITED`.
- A QuoteCancel (Z) over a limit gets j 380 = 0, code `RATE_LIMITED`. The quote stays live, and a taker can accept it. Keep each Z inside the quote budget.
- CRX does not queue a request over a limit.
- CRX answers a and H from the records of the seat, across its sessions. They use no limit.
- More than 50 rejects in 60 s end the session. See [Logout](#47-logout).

Limits for each firm, across its seats:

| Limit | Value | Answer over the limit |
|---|---|---|
| Accepted trades that await confirmation on Ethereum | 5 | 8 150 = 8, 103 = 99, code `RATE_LIMITED`. Text gives the wait. |
| Trades that did not open on Ethereum, in one clock hour | 3 | 8 150 = 8, 103 = 99, code `RATE_LIMITED`. CRX takes accepts again from the next clock hour. |
| Notional of the live RFQs | Text gives it. | j 380 = 0, code `RATE_LIMITED` |

## 11. Onboarding and certification

### 11.1 Onboarding

1. Send the seat address to CRX. For an allowlist, add the source IP addresses. CRX asks for no other credential.
2. CRX approves the seat. It sends the SenderCompID for each role, the host and port, the CRX contract address and the status page address.
3. Install the signature proxy and set its back end.
4. Run the certification cases on production at 100 USD. Use the CRX test RFQ for the maker cases. Until CRX signs the report, trade only the certification cases.
5. CRX reviews the logs and signs the report.
6. Go live.

### 11.2 Certification rules

- Finish the firm's own tests before certification.
- Run the session cases before the taker and maker cases.
- For each case, keep the FIX engine log and the signature proxy log.
- CRX signs one report for each firm and each software version. The report names the FIX engine version and the signature proxy version. CRX reads them from ApplicationSystemName (1603) and ApplicationSystemVersion (1604) of the Logon.
- The signature proxy logs its version at start. It sends the version on each Logon in 1604: `crx-signature-proxy/<version>`, with `+<commit>` when the build has one.
- A maker's first production quote is the off-market quote of case M02. CRX does not select it, and it expires.
- A firm with a signed report gets 3 months' notice before a breaking change. See [Document control](#1-document-control).

Certify again when:

- The FIX engine or the signature proxy version changes.
- The back end changes, for example from a local key to a custodian.
- The firm adds a role: taker, maker or drop copy.
- CRX issues a breaking change.
- In production, the session does not behave as this document states.
- The seat has no Logon for 90 days.
- The firm starts to use a message or a case that it did not certify.

CRX disables the SenderCompID while a recertification is open.

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
| S17 | M | CRX MsgSeqNum too high | T17 | C | SettlDate differs |
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
| P01 | M | Wrong signature domain | M09 | C | Quote status |
| P02 | M | Proxy resend | M10 | C | Wrong side |
| P03 | M | CRX not available | M11 | C | Decline |
| D01 | C | Drop-copy fill | D02 | C | Drop-copy send |
| M12 | C | Quote terms differ from the R | M13 | C | Second quote on one R |

### 11.4 Session cases

Precondition for all cases: the FIX engine connects through the signature proxy.

CRX releases a FIX service version only after the session cases and the end-to-end proof pass on that version.

| ID | Steps | Expected from CRX |
|---|---|---|
| S01 | 1. Send A with 108 = 30. | A with 98 = 0 and 108 = 30. |
| S02 | 1. In the signature proxy, set the seat address to an address that is not the seat of the SenderCompID. Set the login key address to the address of the key. 2. Send A. | 5 with code `LOGON_SIGNATURE_INVALID`. The connection closes. |
| S03 | 1. Send A with 108 = 90. | 5 with code `LOGON_HEART_BT_INT`. |
| S04 | 1. Send A with 52 three minutes behind CRX time. | 5 with code `SENDING_TIME_ACCURACY`. |
| S05 | 1. Log on. 2. Log on again from a second connection with the same CompID. 3. Send 1 on the first session. | Step 2: 5 with code `LOGON_SESSION_ACTIVE`. Step 3: 0 with the same 112. |
| S06 | 1. Log on. 2. Send nothing but Heartbeats for 3 × HeartBtInt. | 0 each HeartBtInt. |
| S07 | 1. Send 1 with 112 = `T1`. | 0 with 112 = `T1`. |
| S08 | 1. Stop all messages for 1.2 × HeartBtInt. 2. Answer the TestRequest. | 1 with 112. The session continues. |
| S09 | 1. Stop all messages. Do not answer the TestRequest. | 1, then 5 with code `HEARTBEAT_TIMEOUT`. |
| S10 | 1. Send 2 with 7 = N and 16 = N for one application message. | The message again with 43 = Y and 122. |
| S11 | 1. Send 2 for a range of 5 messages. | Application messages with 43 = Y. Session messages as 4 with 123 = Y. |
| S12 | 1. Send 2 with 16 = 0. | All messages from 7 to the last one sent. |
| S13 | 1. Send 2 for a range that holds only session messages. | One 4 with 123 = Y and 36 = the end of the range + 1. |
| S14 | 1. Send an application message with 34 = expected + 5. 2. Answer the ResendRequest. | 2 with 7 = the expected number and 16 = 0. Then CRX processes the held message. |
| S15 | 1. Send a message with 34 = expected − 1, without 43. | 5 with code `SEQ_NUM_TOO_LOW`. Text gives both numbers. |
| S16 | 1. Send a message with 34 = expected − 1 and 43 = Y. | No answer. The session continues. |
| S17 | 1. Log out. 2. Set the expected inbound number of the engine 3 below the correct value. 3. Log on. | The engine sends 2. CRX sends again or gap-fills. |
| S18 | 1. Log out. 2. Set the expected inbound number of the engine 3 above the correct value. 3. Log on. | The engine finds a CRX message too low without 43 and sends 5. |
| S19 | 1. Send 4 with 123 = Y and 36 below its 34. | 3 with 373 = 5. |
| S20 | 1. Send 4 with 123 = N and 36 below the expected number. | 3 with 373 = 5. |
| S21 | 1. Send 5. | 5 with code `LOGOUT_ACK`. The connection closes. |
| S22 | 1. Ask CRX support for a renewal Logout. 2. Reconnect after 5 s. | 5 with code `SESSION_RENEWAL`. A after the reconnect. Sequence numbers continue. |
| S23 | 1. Close the TCP connection. 2. Reconnect after 5 s with 141 = N. | A. Each gap fills with 2 and the resend. |
| S24 | 1. Stay logged on through 17:00 New York time. 2. At 17:00:30, log on with 34 = 1 and 141 = Y. | 5 with code `DAILY_RESET`. A with 34 = 1 and 141 = Y. |
| S25 | 1. Ask CRX support for a sequence reset. 2. Send A with 141 = Y and 34 = 1. | A with 141 = Y and 34 = 1. |
| S26 | 1. Send R without 52. | 3 with 373 = 1 and 371 = 52. |
| S27 | 1. Send R with an empty 131. | 3 with 373 = 4. |
| S28 | 1. Send 51 R messages without 52 in 60 s. | 3 for each. After the 51st: 5 with code `ERROR_RATE`. |

### 11.5 Taker cases

Precondition: the seat has the taker role and at least 100 USD of free collateral. Each R, and each AJ with 694 = 1, carries 167 = `FXNDF`.

| ID | Steps | Expected from CRX |
|---|---|---|
| T01 | 1. Send x with 559 = 4. | y with USD/MXN, USD/BRL and USD/PHP. Each has 167 = FXNDF, 15 = USD, 562 = 100 and 969 = 0.000001. |
| T02 | 1. Send R: USD/MXN, 54 = 1, 38 = 100, 541 and 1079 = one day ahead. | AI 297 = 10 at once. 5 s to 20 s later: S with 537 = 1 and 62, or AG with code `NO_QUOTE`. |
| T03 | 1. Do T02. 2. Send AJ with 694 = 1 before 62. | 8 150 = A within 100 ms. Then 8 150 = 0. Then 8 150 = F with 880, 527, 75, 541, 1079, 64, 120 and 151 = 0. |
| T04 | 1. Do T02. 2. Send AJ with 694 = 6. | AI 297 = 11. |
| T05 | 1. Do T02. 2. Wait past 62. 3. Send AJ with 694 = 1. | 8 150 = 8, 103 = 4, code `QUOTE_EXPIRED`. |
| T06 | 1. Send R with 38 = 99. | AG 658 = 3, code `NOTIONAL_BELOW_MINIMUM`. |
| T07 | 1. Send R with 541 and 1079 = 30 minutes ahead. | AG 658 = 3, code `BAD_REQUEST`. Text gives the earliest time. |
| T08 | 1. Send R with 55 = `USD/XYZ`. | AG 658 = 1. |
| T09 | 1. Send R without 38. | AG with code `MISSING_FIELD`. |
| T10 | 1. Do T02. 2. Send AJ with 38 = 200. | 8 150 = 8, code `QUOTE_MISMATCH`. No trade. |
| T11 | 1. Do T03. 2. Send the same AJ again with 43 = Y. | The stored answer. No second trade. |
| T12 | 1. Do T03. 2. Send H for the ClOrdID. 3. Send a for the QuoteID. | 8 150 = I with the current state. AI with the current state. |
| T13 | 1. Send D. | j 380 = 3, code `UNSUPPORTED_MESSAGE`. |
| T14 | 1. Send 11 R messages in one second. | The 11th gets j 380 = 0, code `RATE_LIMITED`. |
| T15 | 1. Do T02. 2. Send AJ. 3. Close the TCP connection at once. 4. Reconnect. 5. Send H. | 8 150 = A, 0 and F, by resend or after the Logon. 8 150 = I. |
| T16 | 1. Send R with 38 = 100.1234567. | AG with code `INVALID_QUANTITY`. |
| T17 | 1. Send R with 64 one day after 541. | AG with code `MATURITY_MISMATCH`. |
| T18 | 1. Ask CRX support to remove the approval of the seat. 2. Send R. 3. Ask CRX support to restore it. | AG 658 = 6, code `NOT_WHITELISTED`. |
| T19 | 1. Send R. 2. Ask CRX support to restart the CRX FIX service before the S. 3. Reconnect. 4. When no S or AG arrives by resend, send a or H. | After the Logon: the S or AG by resend, or the state by a. No second RFQ. |
| T20 | 1. Do T02. 2. Do not answer the S. | At 62: AI 297 = 7, code `QUOTE_EXPIRED`. |

### 11.6 Maker cases

Precondition: the seat has the maker role. CRX sends the CRX test RFQ at 100 USD.

| ID | Steps | Expected from CRX |
|---|---|---|
| M01 | 1. Log on. 2. Wait for the CRX test RFQ. | R with 131 = a UUID and 54 = the taker's side. A maker test request carries Text (58) with code `TEST_REQUEST`, and 126 = the RFQ end. An ordinary RFQ carries 126 = 60 + 5 s, or 60 + half the RFQ life when that is shorter. 62 is the signature end. The R reaches the FIX engine with no 95 and no 96. |
| M02 | 1. Answer the test RFQ before 126 with a rate far from the market. | AI 297 = 0. At the quote end: AI 297 = 7 with code `QUOTE_EXPIRED`. No trade. |
| M03 | 1. Answer the next test RFQ before 126 at the market rate. | AI 297 = 0. Then 8 150 = F with 880 and 527. |
| M04 | 1. Answer a test RFQ after 126. | AI 297 = 5, 300 = 4, code `QUOTE_WINDOW_CLOSED`. |
| M05 | 1. Answer a test RFQ. 2. Send Z for the QuoteID before an accept. | AI 297 = 1. |
| M06 | 1. Answer a test RFQ. 2. Ask CRX support to accept it. 3. Send Z. | j 380 = 0, code `QUOTE_ACCEPTED`. Then 8 150 = F. |
| M07 | 1. Answer a test RFQ. 2. Log out. 3. CRX support accepts the quote. 4. Log on. | The trade fills. 8 150 = F after the Logon. |
| M08 | 1. With a custodian back end, answer 50 test RFQs. | The signature proxy log shows a 99th percentile time below 4.5 s, from TransactTime (60) to the S sent. |
| M09 | 1. Send a for an own QuoteID. | AI with the current state. |
| M10 | 1. Answer a test RFQ with 54 = 1 by BidPx. | AI 297 = 5, 300 = 99, code `WRONG_SIDE`. |
| M11 | 1. Answer a test RFQ with AG 658 = 8. | No answer. No quote from this maker on the RFQ. |
| M12 | 1. Answer a test RFQ with 38 = 200. | The signature proxy sends the S unsigned, with code `TERMS_MISMATCH` in Text (58). CRX answers AI 297 = 5, 300 = 99, code `TERMS_MISMATCH`. |
| M13 | 1. Answer a test RFQ. 2. Before 126, send a second S on the same R with a new QuoteID. | AI 297 = 0 for each S. AI 297 = 6 for the first QuoteID. a on the first QuoteID gets 297 = 6. |

### 11.7 Proxy and drop-copy cases

| ID | Steps | Expected |
|---|---|---|
| P01 | 1. Set a wrong verifyingContract in the signature proxy. 2. Do T02. 3. Send AJ. | The signature proxy signs with the wrong domain. CRX answers 8 150 = 8, 103 = 99, code `INVALID_SIGNATURE`. No trade. |
| P02 | 1. Do T03. 2. Send the AJ again with 43 = Y. | The signature proxy log shows one signature only for the AJ. |
| P03 | 1. Ask CRX support to stop the trading service. 2. Send R. | j 380 = 4, code `SERVICE_UNAVAILABLE`. The session stays up. |
| D01 | 1. Log on the drop-copy CompID with 56 = `CRX-DC`. 2. Trade on FIX or REST. | 8 150 = F for the trade. For a trade on FIX, its ExecID (17) is the ExecID of the fill on the trading session. |
| D02 | 1. Send R on the drop-copy session. | j 380 = 3, code `UNSUPPORTED_MESSAGE`. |

### 11.8 Support

| Phase | Contact |
|---|---|
| Onboarding and certification | CRX onboarding team. Onboarding gives the mailbox and the phone number. |
| Production | CRX support. Onboarding gives the mailbox, the phone number and the hours. |

Send these items with each support request:

1. SenderCompID (49) and TargetCompID (56).
2. MsgType (35), MsgSeqNum (34) and SendingTime (52) of each message in question.
3. The trace ID from Text (58), when there is one.
4. The FIX engine log and the signature proxy log for the period.

## 12. Raw examples

Each sample shows a message as the FIX engine sends or receives it. The samples show `|` for SOH (0x01). BodyLength (9) and CheckSum (10) are correct. Each sample is a file, named in its caption.

- The sample trade is a 1,000,000 USD USD/MXN NDF. The taker buys USD. The settlement time is 2026-11-27 18:00:00 UTC: one month after the trade date, moved to the next business day. The fixing and the settlement are on this date, so SettlDate (64) is equal to MaturityDate (541). See [Settlement time](#103-settlement-time).
- The IDs that the FIX engine sets are examples: ClOrdID `ORD-…`, QuoteReqID `RFQ-…`, QuoteRespID `QR-…` and QuoteID `Q-…`. The IDs that CRX sets are UUIDs. See [IDs and repeats](#410-ids-and-repeats).
- The samples come from one run of the CRX test kit against a local CRX service. The CompIDs are `MKR1` (maker) and `TKR1` (taker).
- Each scenario of the run has its own session. MsgSeqNum (34) starts again in each scenario. The scenarios run one after the other, on one clock. The samples that the table below does not name come from the main trade.
- Samples 11 and 12 come from a test kit that moves the session renewal and the daily reset into the run, so their times differ from [Schedule](#48-schedule).
- [Messages between the signature proxy and CRX](#510-messages-between-the-signature-proxy-and-crx) shows the Logon, R, S and AJ on the connection between the signature proxy and CRX.

| Scenario | Samples |
|---|---|
| Session tests | 04, 06, 07, 08, 09, 10 |
| A taker session of the run | 05 |
| Session renewal | 11 |
| Daily reset | 12 |
| Unknown Symbol | 23 |
| Late accept | 29, 32 |
| Pass | 30, 31 |
| NewOrderSingle | 35 |
| Rate limit | 36 |
| Accept at a price that differs from the quote | 37, 38, 58 |
| Late quote | 54 |
| Cancel | 56, 57 |
| Decline | 59 |
| CRX not available | 62 |
| Quote terms that differ from the R | 63, 64 |
| Quote with an early ValidUntilTime | 65 |

### 12.1 Session

First Logon of the session day, from the FIX engine ([`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix)):

```text
8=FIX.4.4|9=113|35=A|34=1|49=TKR1|52=20261026-09:33:15.393|56=CRX-TRD|98=0|108=30|141=Y|1603=QuickFIX/J 2.3.3|1605=quickfixj.org|10=076|
```

Answer to the first Logon of the session day ([`03-logon-answer.fix`](examples/03-logon-answer.fix)):

```text
8=FIX.4.4|9=81|35=A|49=CRX-TRD|56=TKR1|34=1|52=20261026-09:33:15.503|98=0|108=30|141=Y|383=8192|10=002|
```

Rejected Logon ([`04-logon-rejected.fix`](examples/04-logon-rejected.fix)):

```text
8=FIX.4.4|9=130|35=5|49=CRX-TRD|56=TKR1|34=1|52=20261026-09:47:00.015|58=LOGON_BEGIN_STRING: BeginString must be FIX.4.4. (trace 1a1779b2a2c0023)|10=036|
```

Heartbeat and TestRequest ([`05-heartbeat.fix`](examples/05-heartbeat.fix), [`06-test-request.fix`](examples/06-test-request.fix), [`07-heartbeat-answer.fix`](examples/07-heartbeat-answer.fix)):

```text
8=FIX.4.4|9=54|35=0|34=4|49=TKR1|52=20261026-09:35:00.626|56=CRX-TRD|10=000|
8=FIX.4.4|9=63|35=1|49=TKR1|56=CRX-TRD|34=3|52=20261026-09:47:14.112|112=TR-1|10=212|
8=FIX.4.4|9=64|35=0|49=CRX-TRD|56=TKR1|34=27|52=20261026-09:47:14.126|112=TR-1|10=015|
```

ResendRequest from the firm, and a GapFill from the firm ([`08-resend-request.fix`](examples/08-resend-request.fix), [`09-gap-fill.fix`](examples/09-gap-fill.fix)):

```text
8=FIX.4.4|9=65|35=2|49=TKR1|56=CRX-TRD|34=6|52=20261026-09:47:14.233|7=28|16=28|10=246|
8=FIX.4.4|9=97|35=4|49=TKR1|56=CRX-TRD|34=9|43=Y|52=20261026-09:47:14.270|122=20261026-09:47:14.270|123=Y|36=12|10=079|
```

Session Reject ([`10-session-reject.fix`](examples/10-session-reject.fix)):

```text
8=FIX.4.4|9=149|35=3|49=CRX-TRD|56=TKR1|34=33|52=20261026-09:47:14.343|45=19|371=112|372=1|373=4|58=TAG_WITHOUT_VALUE: Tag 112 has no value. (trace 1a1779b621c0025)|10=025|
```

Renewal and daily reset ([`11-logout-renewal.fix`](examples/11-logout-renewal.fix), [`12-logout-daily.fix`](examples/12-logout-daily.fix)):

```text
8=FIX.4.4|9=152|35=5|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:47:41.701|58=SESSION_RENEWAL: The session ends for signature renewal. Log on again. (trace 1a1779bcc660026)|10=090|
8=FIX.4.4|9=158|35=5|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:48:14.116|58=DAILY_RESET: The session ends for the daily reset. Log on from 09:48:44 UTC. (trace 1a1779c4b930000)|10=086|
```

### 12.2 Taker

QuoteRequest and Pending ([`20-quote-request.fix`](examples/20-quote-request.fix), [`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix)):

```text
8=FIX.4.4|9=190|35=R|34=3|49=TKR1|52=20261026-09:33:15.511|56=CRX-TRD|131=RFQ-000201|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|537=1|54=1|38=1000000|64=20261127|15=USD|60=20261026-09:33:15.510|10=094|
8=FIX.4.4|9=128|35=AI|49=CRX-TRD|56=TKR1|34=2|52=20261026-09:33:15.634|131=RFQ-000201|117=RFQ-000201|55=USD/MXN|60=20261026-09:33:15.520|297=10|10=114|
```

Quote to the taker ([`22a-quote-to-engine.fix`](examples/22a-quote-to-engine.fix)):

```text
8=FIX.4.4|9=262|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:33:21.054|131=RFQ-000201|117=959bbc1a-7496-82e8-af14-38c826bae7c3|537=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|133=18.4753|62=20261026-09:35:15.781|60=20261026-09:33:21.048|10=209|
```

Rejected request, unknown Symbol ([`23-quote-request-reject.fix`](examples/23-quote-request-reject.fix)):

```text
8=FIX.4.4|9=204|35=AG|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:39:41.676|131=RFQ-001901|658=1|146=1|55=USD/XXX|58=UNKNOWN_SYMBOL: The Symbol is not a CRX market. Use a Symbol from SecurityList (y). (trace 1a1779479cb03d3)|10=077|
```

Accept ([`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix)):

```text
8=FIX.4.4|9=243|35=AJ|34=4|49=TKR1|52=20261026-09:33:21.065|56=CRX-TRD|11=ORD-000201|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:33:21.065|64=20261127|117=959bbc1a-7496-82e8-af14-38c826bae7c3|167=FXNDF|541=20261127|693=QR-000201|694=1|1079=18:00:00Z|10=011|
```

Pending New, New and fill ([`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix), [`27-exec-new.fix`](examples/27-exec-new.fix), [`28-exec-fill.fix`](examples/28-exec-fill.fix)):

```text
8=FIX.4.4|9=352|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261026-09:33:21.078|37=63a7bccb-65ac-82d6-9262-ab701a9894be|11=ORD-000201|693=QR-000201|17=84ba6d7a-c139-8227-a8de-55fc822163ad|150=A|39=A|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=1000000|14=0|6=0|60=20261026-09:33:21.074|120=USD|117=959bbc1a-7496-82e8-af14-38c826bae7c3|10=242|
8=FIX.4.4|9=352|35=8|49=CRX-TRD|56=TKR1|34=6|52=20261026-09:33:21.163|37=63a7bccb-65ac-82d6-9262-ab701a9894be|11=ORD-000201|693=QR-000201|17=2fa513dc-2397-82f3-aa48-05e80c9ceb23|150=0|39=0|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=1000000|14=0|6=0|60=20261026-09:33:21.159|120=USD|117=959bbc1a-7496-82e8-af14-38c826bae7c3|10=200|
8=FIX.4.4|9=527|35=8|49=CRX-TRD|56=TKR1|34=7|52=20261026-09:33:23.466|37=63a7bccb-65ac-82d6-9262-ab701a9894be|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=ORD-000201|693=QR-000201|17=70fda49c-379a-8ff5-b9fc-92f96e6c3ff8|150=F|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.452|120=USD|851=2|117=959bbc1a-7496-82e8-af14-38c826bae7c3|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=187|
```

Late accept ([`29-exec-rejected.fix`](examples/29-exec-rejected.fix)):

```text
8=FIX.4.4|9=408|35=8|49=CRX-TRD|56=TKR1|34=9|52=20261026-09:36:32.982|37=NONE|11=ORD-000801|693=QR-000801|17=8a44db94-d3b9-83df-84f0-fdf1e54fec1b|150=8|39=8|103=4|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=0|14=0|6=0|60=20261026-09:36:32.915|120=USD|58=QUOTE_EXPIRED: The quote ended before an accept reached CRX. (trace 1a177919884021d)|117=11116d0c-113b-804e-aafd-07cd8906ab57|10=239|
```

Pass ([`30-quote-response-pass.fix`](examples/30-quote-response-pass.fix), [`31-quote-status-pass.fix`](examples/31-quote-status-pass.fix)):

```text
8=FIX.4.4|9=229|35=AJ|34=4|49=TKR1|52=20261026-09:37:22.662|56=CRX-TRD|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:37:22.661|64=20261127|117=33f11981-b69b-89bd-b4f5-d00376157037|167=FXNDF|541=20261127|693=QR-001401|694=6|1079=18:00:00Z|10=135|
8=FIX.4.4|9=168|35=AI|49=CRX-TRD|56=TKR1|34=5|52=20261026-09:37:22.685|131=RFQ-001401|117=33f11981-b69b-89bd-b4f5-d00376157037|693=QR-001401|55=USD/MXN|60=20261026-09:37:22.668|297=11|10=235|
```

Quote expires with no accept ([`32-quote-status-expired.fix`](examples/32-quote-status-expired.fix)):

```text
8=FIX.4.4|9=241|35=AI|49=CRX-TRD|56=TKR1|34=8|52=20261026-09:36:30.253|131=RFQ-000801|117=11116d0c-113b-804e-aafd-07cd8906ab57|55=USD/MXN|60=20261026-09:36:30.120|297=7|58=QUOTE_EXPIRED: The quote ended before an accept reached CRX. (trace 1a177918da80218)|10=115|
```

Order status ([`33-order-status-request.fix`](examples/33-order-status-request.fix), [`34-exec-status.fix`](examples/34-exec-status.fix)):

```text
8=FIX.4.4|9=84|35=H|34=5|49=TKR1|52=20261026-09:33:23.478|56=CRX-TRD|11=ORD-000201|54=1|55=USD/MXN|10=135|
8=FIX.4.4|9=521|35=8|49=CRX-TRD|56=TKR1|34=8|52=20261026-09:33:23.489|37=63a7bccb-65ac-82d6-9262-ab701a9894be|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=ORD-000201|693=QR-000201|17=6d7b0ed0-501a-8a3e-a532-b5cfd7770681|150=I|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.489|120=USD|117=959bbc1a-7496-82e8-af14-38c826bae7c3|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=249|
```

NewOrderSingle rejected, and a rate limit ([`35-new-order-single-rejected.fix`](examples/35-new-order-single-rejected.fix), [`36-rate-limited.fix`](examples/36-rate-limited.fix)):

```text
8=FIX.4.4|9=151|35=j|49=CRX-TRD|56=TKR1|34=2|52=20261026-09:40:59.581|45=2|372=D|380=3|58=UNSUPPORTED_MESSAGE: CRX does not take this MsgType. (trace 1a17795aa39047a)|10=139|
8=FIX.4.4|9=168|35=j|49=CRX-TRD|56=TKR1|34=15|52=20261026-09:45:57.685|372=R|379=RFQ-003611|380=0|58=RATE_LIMITED: The limit is 20 requests a minute. Wait 2 s. (trace 1a1779a304f07eb)|10=220|
```

Answer to an accept that the signature proxy did not sign ([`38-exec-sign-refusal.fix`](examples/38-exec-sign-refusal.fix)):

```text
8=FIX.4.4|9=410|35=8|49=CRX-TRD|56=TKR1|34=5|52=20261026-09:36:48.454|37=NONE|11=ORD-001001|693=QR-001001|17=388c1ad9-e594-84c9-a94b-f3ccb89da994|150=8|39=8|103=99|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|151=0|14=0|6=0|60=20261026-09:36:48.411|120=USD|58=TERMS_MISMATCH: The signature proxy did not sign the message. (trace 1a17791d50f023a)|117=11003a68-99ab-84fc-bbc4-fafb643da005|10=100|
```

Security list ([`39-security-list-request.fix`](examples/39-security-list-request.fix), [`40-security-list.fix`](examples/40-security-list.fix)):

```text
8=FIX.4.4|9=74|35=x|34=2|49=TKR1|52=20261026-09:33:15.509|56=CRX-TRD|320=SL-000201|559=4|10=035|
8=FIX.4.4|9=247|35=y|49=CRX-TRD|56=TKR1|34=3|52=20261026-09:33:15.778|320=SL-000201|322=1a1778e9579000a|560=0|146=3|55=USD/BRL|167=FXNDF|15=USD|562=100|969=0.000001|55=USD/MXN|167=FXNDF|15=USD|562=100|969=0.000001|55=USD/PHP|167=FXNDF|15=USD|562=100|969=0.000001|10=238|
```

### 12.3 Maker

QuoteRequest to the maker ([`50a-quote-request-to-engine.fix`](examples/50a-quote-request-to-engine.fix)):

```text
8=FIX.4.4|9=261|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:33:16.016|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|62=20261026-09:42:45.000|126=20261026-09:33:20.781|60=20261026-09:33:15.781|10=104|
```

Quote from the maker ([`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix)):

```text
8=FIX.4.4|9=235|35=S|34=2|49=MKR1|52=20261026-09:33:16.044|56=CRX-TRD|15=USD|38=1000000|54=1|55=USD/MXN|62=20261026-09:42:45.000|64=20261127|117=Q-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|10=064|
```

Quote live and late quote ([`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix), [`54-quote-status-rejected.fix`](examples/54-quote-status-rejected.fix)):

```text
8=FIX.4.4|9=151|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261026-09:33:16.088|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|117=Q-000101|55=USD/MXN|60=20261026-09:33:16.079|297=0|10=232|
8=FIX.4.4|9=266|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261026-09:34:23.485|131=9acfe992-a282-87aa-842a-bdd79da947c4|117=Q-000501|55=USD/MXN|60=20261026-09:34:23.479|297=5|58=QUOTE_WINDOW_CLOSED: The quote reached CRX after ExpireTime (126) of the request. (trace 1a1778f9edc0119)|300=4|10=097|
```

Answers to a quote that the signature proxy did not sign: terms that differ from the R, and an early ValidUntilTime ([`64-quote-status-unsigned.fix`](examples/64-quote-status-unsigned.fix), [`65-quote-status-life.fix`](examples/65-quote-status-life.fix)):

```text
8=FIX.4.4|9=247|35=AI|49=CRX-TRD|56=MKR1|34=4|52=20261026-09:40:25.928|131=f453ed43-281e-8723-947e-b8517cdfc1e7|117=Q-002101|55=USD/MXN|60=20261026-09:40:25.734|297=5|58=TERMS_MISMATCH: The signature proxy did not sign the message. (trace 1a1779525fb0435)|300=99|10=051|
8=FIX.4.4|9=252|35=AI|49=CRX-TRD|56=MKR1|34=3|52=20261026-09:40:38.870|131=a9b01548-5d05-8200-b679-3a00abefd2b3|117=Q-002301|55=USD/MXN|60=20261026-09:40:38.739|297=5|58=QUOTE_LIFE_TOO_LONG: The signature proxy did not sign the message. (trace 1a1779558990451)|300=99|10=108|
```

Maker fill ([`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix)):

```text
8=FIX.4.4|9=483|35=8|49=CRX-TRD|56=MKR1|34=6|52=20261026-09:33:23.509|37=c44357af-4326-8aed-8b7a-17b97a682a2a|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=Q-000101|17=dfd3631e-f4f4-8776-8258-f5b0c38de807|150=F|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=2|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.489|120=USD|851=1|117=Q-000101|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=115|
```

Cancel ([`56-quote-cancel.fix`](examples/56-quote-cancel.fix), [`57-quote-status-canceled.fix`](examples/57-quote-status-canceled.fix)):

```text
8=FIX.4.4|9=114|35=Z|34=4|49=MKR1|52=20261026-09:40:52.670|56=CRX-TRD|117=Q-002501|131=a587521c-74a9-8a94-9007-1c00527ffe6b|298=5|10=162|
8=FIX.4.4|9=151|35=AI|49=CRX-TRD|56=MKR1|34=5|52=20261026-09:40:52.947|131=a587521c-74a9-8a94-9007-1c00527ffe6b|117=Q-002501|55=USD/MXN|60=20261026-09:40:52.893|297=1|10=106|
```

Quote expires ([`58-quote-status-expired.fix`](examples/58-quote-status-expired.fix)):

```text
8=FIX.4.4|9=239|35=AI|49=CRX-TRD|56=MKR1|34=7|52=20261026-09:38:43.179|131=61572424-d7d5-822d-b409-1cc399522b7e|117=Q-000901|55=USD/MXN|60=20261026-09:38:43.171|297=7|58=QUOTE_EXPIRED: The quote ended before an accept reached CRX. (trace 1a17793955e034a)|10=082|
```

Decline ([`59-maker-decline.fix`](examples/59-maker-decline.fix)):

```text
8=FIX.4.4|9=120|35=AG|34=2|49=MKR1|52=20261026-09:39:24.771|56=CRX-TRD|131=d1c06943-8600-840e-a57d-3be7373552be|658=10|146=1|55=USD/MXN|10=060|
```

Quote status ([`60-quote-status-request.fix`](examples/60-quote-status-request.fix), [`61-quote-status-answer.fix`](examples/61-quote-status-answer.fix)):

```text
8=FIX.4.4|9=92|35=a|34=3|49=MKR1|52=20261026-09:33:16.130|56=CRX-TRD|55=USD/MXN|117=Q-000101|649=QS-000101|10=039|
8=FIX.4.4|9=165|35=AI|49=CRX-TRD|56=MKR1|34=4|52=20261026-09:33:16.140|649=QS-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|117=Q-000101|55=USD/MXN|60=20261026-09:33:16.140|297=0|10=172|
```

CRX not available ([`62-business-reject.fix`](examples/62-business-reject.fix)):

```text
8=FIX.4.4|9=157|35=j|49=CRX-TRD|56=MKR1|34=3|52=20261026-09:48:30.964|372=S|379=Q-003901|380=4|58=SERVICE_UNAVAILABLE: The service is not available. (trace 1a1779c8d3b0013)|10=193|
```

## 13. Dictionary

- CRX publishes the QuickFIX data dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) with this document. It also publishes a dated copy, `FIX44-CRX-<issue date>.xml`, with the same bytes. Dated copies of earlier issues stay published.
- Line 2 of the file gives the RoE version and issue date, the git commit and the body MD5.
- The dictionary holds every field, type and enum value of the QuickFIX/J 2.3.3 FIX 4.4 dictionary. It adds the fields and values of [section 8](#8-custom-tags). It makes Side (54), OrderQty (38), Currency (15) and ValidUntilTime (62) required on Quote (S).
- It declares CrxSignature (20007) on S and AJ, for a firm that signs without the signature proxy. A FIX engine behind the signature proxy never sends or receives 20007.
- Load it in the FIX engine with `UseDataDictionary=Y`.
- The dictionary gives the field order in each message and group. When this document and the dictionary differ, report it to CRX support.

## 14. Legal notice

- This document gives information only. It is not an offer and not advice.
- CRX gives no warranty on this document or on the samples, test vectors and dictionary that come with it.
- CRX can change this document. [Document control](#1-document-control) records each change and its notice period.
