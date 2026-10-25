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

Install the SDK on Python 3.10 or later; the account wallet needs 100 USDC and about 0.001 ETH for network fees.

```bash
pip install "git+https://github.com/crxfoundation/crx-python@v0.3.17"
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
[Quote it](#quote-it)
```

## Quote it

Send a firm quote at the RFQ's reference rate, `rfq.reference_rate`, which CRX accepts.

```python
# maker.send_quote(rfq, rate)
q = maker.send_quote(rfq, rfq.reference_rate)
print(q.rate)
```

```crx-step-done
Quote sent.
[Confirm the trade](#confirm-the-trade)
```

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
