# CRX FIX API

Trade FX non-deliverable forwards on CRX from a FIX 4.4 engine. The engine sends and reads standard FIX fields only, with no custom tag.

The engine connects to the CRX signature proxy on the same host. The proxy signs for the seat: [set up the signature proxy on GitHub](signature-proxy.md).

## Key facts

| Item | Value |
|---|---|
| Protocol | FIX 4.4 with the CRX dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) |
| TargetCompID (56) | `CRX-TRD` for trading, `CRX-DC` for drop copy |
| SenderCompID (49), and the CRX host and port for the signature proxy | Provided at onboarding |
| Markets | USD/MXN, USD/BRL and USD/PHP non-deliverable forwards |
| Settlement | Cash, in Circle USDC on Ethereum |
| Settlement date | The fixing date. SettlDate (64) = MaturityDate (541). |
| Settlement time | 1 hour to 90 days after the request, in MaturityDate (541) and MaturityTime (1079) |
| Fixing source | Pyth Network spot price. Not an EMTA Annex A rate source. |
| Minimum notional | 100 USD |
| RFQ life | 120 s |
| Quotes | Binding. No last look. |
| Daily reset | 17:00:00 New York time |

## 1. Connect

Before the first Logon, CRX approves the seat and sends the SenderCompID, the host and the port. Deposit Circle USDC on the seat through the CRX web app or the REST API.

Load the dictionary [`FIX44-CRX.xml`](FIX44-CRX.xml) in the FIX engine. It holds MaturityTime (1079), UpfrontPriceType (1741) and UpfrontPrice (1742) inside the NoRelatedSym (146) group. A stock `FIX44.xml` does not.

QuickFIX/J sends a group in the field order of its own FIX 4.4 classes, not of the dictionary. Build the NoRelatedSym (146) group of the QuoteRequest (R) in the order of [`FIX44-CRX.xml`](FIX44-CRX.xml). Otherwise CRX answers Reject (3) `GROUP_ORDER`:

```java
Group group = new Group(146, 55, Session.lookupSession(sessionID).getDataDictionary()
    .getGroup("R", 146).getDataDictionary().getOrderedFields());
```

Session settings, in the QuickFIX/J form:

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

- SocketConnectHost and SocketConnectPort: the `listen` address of the signature proxy.
- Add `FileStorePath`, a directory kept over restarts. With ResetOnLogon=N, the sequence numbers continue after a restart.
- At 17:00:00 New York time, CRX ends the session with Logout code `DAILY_RESET`. From 17:00:30, log on with MsgSeqNum (34) = 1 and ResetSeqNumFlag (141) = Y. In QuickFIX/J, set 141 = Y in `toAdmin` on the Logon with MsgSeqNum (34) = 1.
- Keep the host clock on NTP. SendingTime (52) must be within 120 s of CRX time.

## 2. Logon

Send Logon (A). Set ApplicationSystemName (1603) to the name and version of the FIX engine, and ApplicationSystemVendor (1605) to its vendor.

The samples on this page come from a CRX test run with QuickFIX/J 2.3.3. `|` stands for SOH (0x01).

Logon ([`01-logon-from-engine.fix`](examples/01-logon-from-engine.fix)):

```text
8=FIX.4.4|9=113|35=A|34=1|49=TKR1|52=20261026-09:33:15.393|56=CRX-TRD|98=0|108=30|141=Y|1603=QuickFIX/J 2.3.3|1605=quickfixj.org|10=076|
```

Answer: Logon (A) with MaxMessageSize (383) = 8192. Send application messages only after it ([`03-logon-answer.fix`](examples/03-logon-answer.fix)):

```text
8=FIX.4.4|9=81|35=A|49=CRX-TRD|56=TKR1|34=1|52=20261026-09:33:15.503|98=0|108=30|141=Y|383=8192|10=002|
```

A rejected Logon gets Logout (5). Text (58) starts with the code, for example `LOGON_BEGIN_STRING` ([`04-logon-rejected.fix`](examples/04-logon-rejected.fix)).

## 3. Taker: first trade

The samples show one trade: a USD/MXN NDF of 1,000,000 USD, the taker buys USD. Settlement is on the fixing date, one month after the trade date and moved to the next business day, at 18:00:00 UTC: SettlDate (64) = MaturityDate (541).

### Request

Send QuoteRequest (R) with a new QuoteReqID (131). In the NoRelatedSym (146) group, send these fields in this order:

1. Symbol (55), from SecurityList (y).
2. SecurityType (167) = `FXNDF`.
3. MaturityDate (541) and MaturityTime (1079): the settlement time, UTC, 1079 as `HH:MM:SSZ`.
4. QuoteType (537) = 1, Side (54), OrderQty (38).
5. SettlDate (64) = 541.
6. Currency (15), TransactTime (60).

For the list of markets, send SecurityListRequest (x) with a new SecurityReqID (320) and SecurityListRequestType (559) = 4.

QuoteRequest ([`20-quote-request.fix`](examples/20-quote-request.fix)):

```text
8=FIX.4.4|9=190|35=R|34=3|49=TKR1|52=20261026-09:33:15.511|56=CRX-TRD|131=RFQ-000201|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|537=1|54=1|38=1000000|64=20261127|15=USD|60=20261026-09:33:15.510|10=094|
```

Answer: QuoteStatusReport (AI) 297 = 10 at once ([`21-quote-status-pending.fix`](examples/21-quote-status-pending.fix)).

Then CRX sends the best Quote (S), 5 to 20 s after the R. The rate is in OfferPx (133) when the taker buys, and in BidPx (132) when the taker sells ([`22a-quote-to-engine.fix`](examples/22a-quote-to-engine.fix)):

```text
8=FIX.4.4|9=262|35=S|49=CRX-TRD|56=TKR1|34=4|52=20261026-09:33:21.054|131=RFQ-000201|117=959bbc1a-7496-82e8-af14-38c826bae7c3|537=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|133=18.4753|62=20261026-09:35:15.781|60=20261026-09:33:21.048|10=209|
```

With no quote, CRX sends QuoteRequestReject (AG) code `NO_QUOTE`. A BusinessMessageReject (j) with code `RATE_LIMITED` or `SERVICE_UNAVAILABLE` also ends the R.

### Accept

Before ValidUntilTime (62) of the S, send QuoteResponse (AJ) with 694 = 1:

- Copy QuoteID (117), Symbol (55), Side (54) and OrderQty (38) from the S.
- Set SecurityType (167) = `FXNDF` and Price (44) = the rate.
- Set a new QuoteRespID (693) and a new ClOrdID (11).

QuoteResponse ([`24-quote-response-from-engine.fix`](examples/24-quote-response-from-engine.fix)):

```text
8=FIX.4.4|9=243|35=AJ|34=4|49=TKR1|52=20261026-09:33:21.065|56=CRX-TRD|11=ORD-000201|38=1000000|44=18.4753|54=1|55=USD/MXN|60=20261026-09:33:21.065|64=20261127|117=959bbc1a-7496-82e8-af14-38c826bae7c3|167=FXNDF|541=20261127|693=QR-000201|694=1|1079=18:00:00Z|10=011|
```

### Fill

Answer: ExecutionReport (8) 150 = A, then 150 = 0 ([`26-exec-pending-new.fix`](examples/26-exec-pending-new.fix), [`27-exec-new.fix`](examples/27-exec-new.fix)).

Then 150 = F when the trade is final, or 150 = 8 when the trade does not open. Book the trade on 150 = F, once for each TrdMatchID (880). SecondaryExecID (527) is the trade hash on Ethereum ([`28-exec-fill.fix`](examples/28-exec-fill.fix)):

```text
8=FIX.4.4|9=527|35=8|49=CRX-TRD|56=TKR1|34=7|52=20261026-09:33:23.466|37=63a7bccb-65ac-82d6-9262-ab701a9894be|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=ORD-000201|693=QR-000201|17=70fda49c-379a-8ff5-b9fc-92f96e6c3ff8|150=F|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.452|120=USD|851=2|117=959bbc1a-7496-82e8-af14-38c826bae7c3|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=187|
```

- Until the settlement time, CRX can send 8 150 = H (Trade Cancel). The trade then does not stand. Remove it from the books.
- Accept one RFQ at a time.
- With no ExecutionReport 5 s after the AJ, send OrderStatusRequest (H) with the ClOrdID (11), Symbol (55) and Side (54) of the AJ. CRX answers ExecutionReport (8) 150 = I. Do not send a second AJ.

## 4. Maker: first quote

### Request

CRX sends QuoteRequest (R). Side (54) is the taker's side. Quote before ExpireTime (126) of the R. ValidUntilTime (62) is the latest time that the trade can open ([`50a-quote-request-to-engine.fix`](examples/50a-quote-request-to-engine.fix)):

```text
8=FIX.4.4|9=261|35=R|49=CRX-TRD|56=MKR1|34=2|52=20261026-09:33:16.016|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|146=1|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=1|38=1000000|64=20261127|15=USD|62=20261026-09:42:45.000|126=20261026-09:33:20.781|60=20261026-09:33:15.781|10=104|
```

### Quote

Send Quote (S):

- Copy QuoteReqID (131), Symbol (55), Side (54), OrderQty (38), Currency (15), MaturityDate (541), MaturityTime (1079) and ValidUntilTime (62) from the R.
- Copy UpfrontPriceType (1741) and UpfrontPrice (1742) when the R has them.
- Set a new QuoteID (117).
- Send OfferPx (133) when 54 = 1 and BidPx (132) when 54 = 2.

Quote ([`51-quote-from-engine.fix`](examples/51-quote-from-engine.fix)):

```text
8=FIX.4.4|9=235|35=S|34=2|49=MKR1|52=20261026-09:33:16.044|56=CRX-TRD|15=USD|38=1000000|54=1|55=USD/MXN|62=20261026-09:42:45.000|64=20261127|117=Q-000101|131=06bd9fb2-3522-8607-9e4f-2cb03bbcd488|133=18.4753|167=FXNDF|537=1|541=20261127|1079=18:00:00Z|10=064|
```

Answer: QuoteStatusReport (AI) 297 = 0 ([`53-quote-status-accepted.fix`](examples/53-quote-status-accepted.fix)). The quote binds, with no last look, until the quote end: the earlier of the RFQ end and ValidUntilTime (62) of the R.

### Fill

When a taker accepts, CRX sends ExecutionReport (8) 150 = 0, then 150 = F when the trade is final, or 150 = 8 when it does not open. Side (54) is the maker's own side: 2 when the R had 54 = 1. Taker and maker get the same TrdMatchID (880) ([`55-exec-fill-maker.fix`](examples/55-exec-fill-maker.fix)):

```text
8=FIX.4.4|9=483|35=8|49=CRX-TRD|56=MKR1|34=6|52=20261026-09:33:23.509|37=c44357af-4326-8aed-8b7a-17b97a682a2a|527=0x1462ecb95582689273ca8f76fbe539d00c2704cb9a964679e4765c94712fb95a|11=Q-000101|17=dfd3631e-f4f4-8776-8258-f5b0c38de807|150=F|39=2|64=20261127|55=USD/MXN|167=FXNDF|541=20261127|1079=18:00:00Z|54=2|38=1000000|15=USD|32=1000000|31=18.4753|151=0|14=1000000|6=18.4753|75=20261026|60=20261026-09:33:23.489|120=USD|851=1|117=Q-000101|880=978cb2c4-2835-8d0f-ba22-2ae00075fe63|1056=18475300.00|10=115|
```

- A quote that does not win gets AI 297 = 7 at the quote end.
- To cancel a quote before a taker accepts it, send QuoteCancel (Z) with QuoteID (117), QuoteReqID (131) and QuoteCancelType (298) = 5. CRX answers AI 297 = 1. After an accept, the Z gets BusinessMessageReject (j) code `QUOTE_ACCEPTED` and the trade stands.
- To decline an RFQ, send QuoteRequestReject (AG) with the QuoteReqID (131) of the R and 658 = 10 ([`59-maker-decline.fix`](examples/59-maker-decline.fix)). CRX sends no answer.

## 5. Rejects

Each reject carries Text (58) as `<CODE>: <sentence> (trace <id>)`. Act on the code. When the code is unknown, act on the FIX reason field: 373, 380, 658, 300 or 103. Give the trace ID to CRX support.

| Code | Message | Fix |
|---|---|---|
| `LOGON_COMP_ID_UNKNOWN` | Logout (5) | Use the SenderCompID from onboarding, and `CRX-TRD` or `CRX-DC`. |
| `SENDING_TIME_ACCURACY` | Logout (5) | Keep the host clock on NTP. |
| `LOGON_SESSION_ACTIVE` | Logout (5) | Log on after the other session ends. |
| `GROUP_ORDER` | Reject (3) | Send the group fields in the order of [`FIX44-CRX.xml`](FIX44-CRX.xml). |
| `MISSING_FIELD` | AG or 8 | Add the field, for example SecurityType (167) = `FXNDF`. |
| `INVALID_FIELD` | AG, AI or 8 | Correct the field. Send MaturityTime (1079) with no decimals. |
| `MATURITY_MISMATCH` | AG or 8 | Send SettlDate (64) = MaturityDate (541). On an AJ, 541 and 1079 are optional; when sent, copy them from the S. |
| `UNKNOWN_SYMBOL` | AG | Use a Symbol from SecurityList (y). |
| `NOTIONAL_BELOW_MINIMUM` | AG | Send 100 USD or more. |
| `NO_QUOTE` | AG | Send a new R later. |
| `INSUFFICIENT_COLLATERAL` | AG, AI or 8 | Deposit USDC or reduce OrderQty (38). |
| `QUOTE_EXPIRED` | 8 | Send a new R. Accept before ValidUntilTime (62). |
| `TRADE_STALE` | 8 | Accept the new Quote (S) that CRX sends next, with a new QuoteRespID (693) and ClOrdID (11). |
| `RATE_LIMITED` | j; on an AJ, 8 | Wait for the time in Text (58). |
| `QUOTE_WINDOW_CLOSED` | AI | Quote before ExpireTime (126). |
| A signature code: `LOGON_SIGNATURE_MISSING`, `UNAUTHORIZED`, `SIGNATURE_MISSING` or a signature proxy code such as `TERMS_MISMATCH` | Logout (5), AI or 8 | Read the signature proxy log. |

## 6. Files and rules

- Dictionary: [`FIX44-CRX.xml`](FIX44-CRX.xml).
- Every rule, message and code: the [Rules of Engagement](rules-of-engagement.md) on GitHub, with 51 sample messages.
- Next: certification on production at 100 USD, in [section 11](rules-of-engagement.md#11-onboarding-and-certification) of the Rules of Engagement.
