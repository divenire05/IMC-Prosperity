#!/usr/bin/env python
# coding: utf-8

# In[17]:


from datamodel import OrderDepth, TradingState, Order, ConversionObservation
from typing import List

class Trader:

    CSI = 65                                  # Critical Sunlight Index
    POSITION_LIMIT = 75                       # Max macarons we’ll hold
    DAILY_STORAGE_COST = 0.1                  # per macaron, per day
    PROFIT_BUFFER = 50                        # take profit only if > all‐in cost + buffer
    ORDER_SIZE = 5                            # buy 5 units at once when sun drops

    def run(self, state: TradingState):
        orders = {}
        conversions = 0

        # --- 1) Rehydrate our small state from the last run ---
        try:
            st = json.loads(state.traderData)
        except Exception:
            st = {
                "in_position": False,      # are we currently long?
                "avg_cost": 0.0,           # our all‐in cost per unit 
                "days_held": 0,            # how many “runs” since our purchase
                "qty": 0                   # how many units we hold
            }

        # --- 2) Pull the macaron observation (for fees, sugar, sunlight) ---
        conv = state.observations.conversionObservations.get("MAGNIFICENT_MACARONS")
        if conv is None:
            print("❌ no macaron conversion obs")
            return {}, 0, json.dumps(st)

        sun = conv.sunlightIndex
        transport = conv.transportFees
        imp_tariff = conv.importTariff
        exp_tariff = conv.exportTariff

        # --- 3) Best bid/ask from the order book ---
        od: OrderDepth = state.order_depths.get("MAGNIFICENT_MACARONS")
        if od is None:
            print("❌ no macaron book")
            return {}, 0, json.dumps(st)

        best_bid, bid_vol = self.get_best_bid(od)
        best_ask, ask_vol = self.get_best_ask(od)

        # --- 4) Decision logic ---
        if not st["in_position"]:
            # if sunlight drops below CSI → BUY up to ORDER_SIZE
            if sun < self.CSI and best_ask is not None and ask_vol >= self.ORDER_SIZE:
                buy_size = min(self.ORDER_SIZE, self.POSITION_LIMIT)
                all_in_price = best_ask + transport + imp_tariff
                st.update({
                    "in_position": True,
                    "avg_cost": all_in_price,
                    "days_held": 0,
                    "qty": buy_size
                })
                print(f"🔴 SUN {sun:.1f}<CSI → BUY {buy_size}@{best_ask:.1f} all‑in {all_in_price:.1f}")
                orders["MAGNIFICENT_MACARONS"] = [Order("MAGNIFICENT_MACARONS", best_ask,  buy_size)]
            else:
                print(f"☀️ no entry (sun={sun:.1f}, in_position=False)")
        else:
            # we are long: increment storage days
            st["days_held"] += 1
            # compute our break‑even + buffer: cost + storage + export fees + transport
            storage_cost = st["days_held"] * self.DAILY_STORAGE_COST
            break_even = st["avg_cost"] + storage_cost + exp_tariff + transport + self.PROFIT_BUFFER

            # if sun recovers AND price > break_even → SELL all
            if sun >= self.CSI and best_bid is not None and best_bid > break_even:
                qty = st["qty"]
                print(f"🟢 SUN {sun:.1f}≥CSI & bid {best_bid:.1f}>BE {break_even:.1f} → SELL {qty}@{best_bid:.1f}")
                orders["MAGNIFICENT_MACARONS"] = [
                    Order("MAGNIFICENT_MACARONS", best_bid, -qty)
                ]
                # reset state
                st.update({"in_position": False, "days_held": 0, "qty": 0})
            else:
                print(f"⏳ HOLDING {st['qty']} macaron(s), sun={sun:.1f}, "
                      f"best_bid={best_bid}, BE+buf={break_even:.1f}")

        # --- 5) Persist updated state ---
        traderData = json.dumps(st)
        return orders, conversions, traderData


    def get_best_bid(self, od: OrderDepth):
        if od.buy_orders:
            price = max(od.buy_orders)
            return price, abs(od.buy_orders[price])
        return None, 0

    def get_best_ask(self, od: OrderDepth):
        if od.sell_orders:
            price = min(od.sell_orders)
            return price, abs(od.sell_orders[price])
        return None, 0


# In[ ]:




