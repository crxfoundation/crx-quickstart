import crx

# Reads CRX_WALLET_PK_FILE (or CRX_WALLET_PK).
# crx.Client(network="mainnet", allow_mainnet=True)
maker = crx.Client(network="mainnet", allow_mainnet=True)

# maker.deposit(amount)
d = maker.deposit(100)  # returns once CRX validates the deposit
print("Validated" if d.counted else d.status, maker.balance().free)

# maker.test_request()
rfq = maker.test_request()
print(rfq.pair, rfq.side, rfq.notional, rfq.reference_rate)

# maker.send_quote(rfq, rate)
q = maker.send_quote(rfq, rfq.reference_rate)
print(q.rate)

# maker.confirm(quote)
t = maker.confirm(q)
print(t.status)

# maker.positions()
for p in maker.positions():
    print(p.pair, p.side, p.notional, p.entry_price,
          p.settles_at, p.unrealized_pnl)

# maker.withdraw(amount=None)
w = maker.withdraw(50)  # maker.withdraw() withdraws all free collateral
print(w.amount, w.status)

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
