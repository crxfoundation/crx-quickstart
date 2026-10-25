---
title: "API Quickstart"
navTitle: "API Quickstart"
description: "Request quotes, trade and read your book on CRX."
order: 7
group: "Quotes"
mode: tutorial
---

```crx-walkthrough
getting-started
```

```crx-copy-script
```

To complete your first trade easily in a few minutes, install the SDK, replace /path/to/wallet.key with the path to your key file, and copy and paste the full Quickstart script. The script will deposit 100 USDC to the CRX Margin account, request a quote, accept it, and withdraw remaining collateral. For step-by-step instructions, see below.

## Set up

Install the SDK on Python 3.10 or later, then create a client.

```bash
pip install "git+https://github.com/crxfoundation/crx-python@v0.3.17"
```

```bash
echo 'CRX_WALLET_PK_FILE=/path/to/wallet.key' >> .env
chmod 600 /path/to/wallet.key
```

```python
import crx
from datetime import datetime, timedelta, timezone

# Reads CRX_WALLET_PK_FILE (or CRX_WALLET_PK).
# crx.Client(network="mainnet", allow_mainnet=True)
c = crx.Client(network="mainnet", allow_mainnet=True)
```

```crx-step-done
Client ready.
[Deposit](#deposit)
```

## Deposit

Deposit USDC from the account wallet as collateral; it counts in free collateral once CRX validates it.

```python
# c.deposit(amount)
d = c.deposit(100)  # returns once CRX validates the deposit
print("Validated" if d.counted else d.status, c.balance().free)
```

```output
Validated 100.000000
```

```crx-step-done
Deposit validated.
[Request a quote](#request-a-quote)
```

## Request a quote

Request a quote by setting the trade parameters: pair, side, notional and settlement date.

```python
# c.quote(pair="USD/MXN" | "USD/BRL" | "USD/PHP", side="buy" | "sell", notional=100 to 10_000_000, settles=aware datetime | "YYYY-MM-DDTHH:MMZ" | Unix seconds)
settles = datetime.now(timezone.utc) + timedelta(hours=2)
q = c.quote("USD/MXN", "buy", 100, settles=settles)
print(q.pair, q.side, q.notional, q.rate, q.settles_at, q.closes_at)
```

```crx-step-done
Quote received.
[Accept or reject](#accept-or-reject)
```

## Accept or reject

Accept the quote if the rate suits you, else reject it; rejecting is optional, as a quote with no answer ends at `q.closes_at`.

```python
# c.accept(quote) · c.reject(quote)
if q.rate <= 19.5:  # the most MXN you pay for 1 USD
    t = c.accept(q)  # returns once the trade is open or refused
    print(t.status)
else:
    c.reject(q)
```

```crx-step-done
Quote answered.
[View positions](#view-positions)
```

## View positions

Read each open position with its entry price, its settlement time and its unrealized profit and loss in USDC.

```python
# c.positions()
for p in c.positions():
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
# c.withdraw(amount=None)
w = c.withdraw(50)  # c.withdraw() withdraws all free collateral
print(w.amount, w.status)
```

```crx-trade-complete
[Deposit](#deposit)
[Withdraw excess collateral](#withdraw)
[Request and accept a trade](#request-a-quote)
[View positions](#view-positions)
```
