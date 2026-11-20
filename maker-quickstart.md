---
title: "API Quickstart"
navTitle: "API Quickstart"
description: "Open a 100 USD maker test trade and read it back."
order: 7
group: "Quotes"
mode: tutorial
unlisted: true
---

```crx-walkthrough
maker-quickstart
```

```crx-copy-script
# More calls: call one after the steps.

# Free collateral in USDC; None while an open trade has no price.
def free_collateral():
    return maker.balance().free

# Entry price, mark price and unrealized P&L in USDC of each position.
def positions_pnl():
    return [(p.pair, p.entry_price, p.mark_price, p.unrealized_pnl)
            for p in maker.positions()]

# Withdraw part of the free collateral, e.g. withdraw_part(25).
def withdraw_part(usdc):
    return maker.withdraw(usdc)

# End a firm quote at once, before the taker accepts it: drop(q).
def drop(quote):
    return maker.drop_quote(quote)

# Quote live RFQs for one hour at price(rfq); None passes, e.g. on USD/BRL.
def quote_live(price):
    return maker.quote_live(price, seconds=3600)
```

To complete your first trade easily in a few minutes, install the SDK, replace /path/to/wallet.key with the path to your key file, and copy and paste the full Quickstart script. The script will deposit 100 USDC to the CRX Margin account, trigger CRX to send out a trade request, respond with a quote from your address, and withdraw remaining collateral. For step-by-step instructions, see below.

## Set up

Install the SDK on Python 3.10 or later; the account wallet needs 100 USDC and ETH for network fees.

```bash
pip install "git+https://github.com/crxfoundation/crx-python@v0.4.0"
```

```bash
echo 'CRX_WALLET_PK_FILE=/path/to/wallet.key' >> .env
chmod 600 /path/to/wallet.key
```

```python
import crx

# Reads CRX_WALLET_PK_FILE (or CRX_WALLET_PK).
# crx.Client(network="mainnet", allow_mainnet=True)
maker = crx.Client(network="mainnet", allow_mainnet=True)
```

```crx-step-done
Client ready.
[Deposit](#deposit)
```

## Deposit

Deposit USDC from the account wallet as collateral; it counts in free collateral once CRX validates it.

```python
# maker.deposit(amount)
d = maker.deposit(100)  # returns once CRX validates the deposit
print("Validated" if d.counted else d.status, maker.balance().free)
```

```output
Validated 100.000000
```

```crx-step-done
Deposit validated.
[Request a test RFQ](#request-a-test-rfq)
```

## Request a test RFQ

Request a 100 USD test RFQ in USD/MXN, one per UTC day; it opens once your deposit counts.

```python
# maker.test_request()
rfq = maker.test_request()
print(rfq.pair, rfq.side, rfq.notional, rfq.reference_rate)
```

```crx-step-done
Test RFQ received.
[Wire your own price](#wire-your-own-price)
```

## Wire your own price

`quote_live(price)` calls `price(rfq)` for each live RFQ. The `Rfq` has `pair` (`str`) and `side` (`"buy"` or `"sell"`). `side` is the maker's side in the base currency. `notional` is a `Decimal` amount in the base currency, and `expiry` is a UTC settlement `datetime`. `reference_rate` is set on test RFQs. Live RFQs do not provide it.

Return a rate in quote currency per base unit. Use at most six decimal places. Return `None` to pass. CRX must receive the quote within five seconds of `rfq.opened`. The SDK uses the RFQ's quote expiry, which must be at least 60 seconds after submission. Keep `price()` fast.

This test function applies a spread to the RFQ's current reference rate. For live RFQs, replace `mid` with a live market-data lookup.

```python
from decimal import Decimal

def price(rfq):
    if rfq.pair != "USD/MXN" or rfq.notional is None:
        return None
    mid = rfq.reference_rate
    if mid is None:
        return None
    if rfq.side == "sell":
        return mid + Decimal("0.001")
    if rfq.side == "buy":
        return mid - Decimal("0.001")
    return None

q = maker.send_quote(rfq, price(rfq))
print(q.rate)
```

```crx-step-done
Quote sent.
[Confirm the trade](#confirm-the-trade)
```

With a live price source in `price()`, quote new RFQs with `maker.quote_live(price, seconds=3600)`. For direct REST calls, send the returned rate as `rate` to `POST /rfqs/{rfq_id}/quotes`. Use the REST and WebSocket API reference supplied at onboarding. For FIX, send `OfferPx (133)` when `Side (54)` is 1 or `BidPx (132)` when it is 2. See [Maker: first quote](fix/quickstart.md#4-maker-first-quote).

## Confirm the trade

Wait for CRX to accept the quote; the call returns once the trade is open or refused.

```python
# maker.confirm(quote)
t = maker.confirm(q)
print(t.status)
```

```crx-step-done
Trade open.
[View positions](#view-positions)
```

## View positions

Read each open position with its entry price, its settlement time and its unrealized profit and loss in USDC.

```python
# maker.positions()
for p in maker.positions():
    print(p.pair, p.side, p.notional, p.entry_price,
          p.settles_at, p.unrealized_pnl)
```

```crx-step-done
Positions read.
[Withdraw](#withdraw)
```

## Withdraw

Withdraw free collateral to the account wallet; withdrawal approval time is 60 minutes.

```python
# maker.withdraw(amount=None)
w = maker.withdraw(50)  # maker.withdraw() withdraws all free collateral
print(w.amount, w.status)
```

```crx-trade-complete
[Deposit](#deposit)
[Withdraw excess collateral](#withdraw)
[Quote live RFQs](#full-script)
[View positions](#view-positions)
```
