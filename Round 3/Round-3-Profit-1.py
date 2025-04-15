#!/usr/bin/env python
# coding: utf-8

# In[1]:


from typing import Dict, List
from datamodel import Order, OrderDepth, TradingState, Trade
import json
import math

class Trader:
    def __init__(self):
        self.mid_prices = {
            "CROISSANTS": [],
            "JAMS": [],
            "DJEMBES": [],
            "PICNIC_BASKET1": []
        }

    POSITION_LIMITS = {
        "CROISSANTS": 250,
        "JAMS": 350,
        "PICNIC_BASKET2": 100
    }
    
    def run(self, state: TradingState):
        orders = {}
        conversions = 0
        traderData = "pb2_arbitrage_v2"
        
        # Instrument list with correct naming.
        instruments = ["CROISSANTS", "JAMS", "PICNIC_BASKET2"]
        mid_prices = {}
        
        # Compute mid prices for each instrument.
        for inst in instruments:
            if inst not in state.order_depths:
                print(f"{inst}: No order depth data.")
                continue
            mid = self.get_mid_price(state.order_depths[inst])
            mid_prices[inst] = mid
            print(f"{inst}: mid price = {mid}")
        
        # Proceed only if we have mid prices for all instruments.
        if any(mid is None for mid in mid_prices.values()):
            print("Missing mid price for one or more instruments; skipping trade.")
            return {}, conversions, traderData
        
        croissants_mid = mid_prices["CROISSANTS"]
        jams_mid = mid_prices["JAMS"]
        pb2_mid = mid_prices["PICNIC_BASKET2"]
        
        # Compute fair value for Picnic Basket 2 based on its underlying components:
        # PICNIC_BASKET2 is defined as 4 CROISSANTS + 2 JAMS.
        fair_value = 4 * croissants_mid + 2 * jams_mid
        print(f"Fair value for PICNIC_BASKET2 = 4 * {croissants_mid:.2f} + 2 * {jams_mid:.2f} = {fair_value:.2f}")
        print(f"PB2 mid = {pb2_mid:.2f}")
        
        # Use a threshold now (e.g., 3 seashells)
        threshold = 3
        
        current_pb2_pos = state.position.get("PICNIC_BASKET2", 0)
        od_pb2 = state.order_depths["PICNIC_BASKET2"]
        
        # If PB2 is undervalued: pb2_mid + threshold < fair_value, then buy PB2.
        if pb2_mid + threshold < fair_value:
            best_ask, ask_vol = self.get_best_ask(od_pb2)
            print(f"Arbitrage BUY signal: PB2 mid ({pb2_mid:.2f}) + threshold ({threshold}) < fair_value ({fair_value:.2f}).")
            if best_ask is not None and ask_vol is not None and ask_vol >= 1:
                limit_remaining = self.POSITION_LIMITS["PICNIC_BASKET2"] - current_pb2_pos
                if limit_remaining >= 1:
                    buy_qty = 1  # fixed 1 unit per signal
                    print(f"Placing BUY order for PICNIC_BASKET2: {buy_qty} unit at best ask {best_ask} (ask_vol: {ask_vol})")
                    orders.setdefault("PICNIC_BASKET2", []).append(Order("PICNIC_BASKET2", best_ask, buy_qty))
                else:
                    print("Position limit reached for buying PB2.")
            else:
                print("No sufficient ask volume for PB2 BUY order.")
        # If PB2 is overvalued: pb2_mid - threshold > fair_value, then sell PB2.
        elif pb2_mid - threshold > fair_value:
            best_bid, bid_vol = self.get_best_bid(od_pb2)
            print(f"Arbitrage SELL signal: PB2 mid ({pb2_mid:.2f}) - threshold ({threshold}) > fair_value ({fair_value:.2f}).")
            if best_bid is not None and bid_vol is not None and bid_vol >= 1:
                if current_pb2_pos >= 1:
                    sell_qty = 1  # fixed 1 unit per signal
                    print(f"Placing SELL order for PICNIC_BASKET2: {sell_qty} unit at best bid {best_bid} (bid_vol: {bid_vol})")
                    orders.setdefault("PICNIC_BASKET2", []).append(Order("PICNIC_BASKET2", best_bid, -sell_qty))
                else:
                    print("No PB2 inventory to sell.")
            else:
                print("No sufficient bid volume for PB2 SELL order.")
        else:
            print(f"No arbitrage opportunity: PB2 mid ({pb2_mid:.2f}) is within threshold of fair value ({fair_value:.2f}).")
        
        return orders, conversions, traderData

    def get_mid_price(self, order_depth: OrderDepth):
        best_bid, _ = self.get_best_bid(order_depth)
        best_ask, _ = self.get_best_ask(order_depth)
        if best_bid is not None and best_ask is not None:
            return (best_bid + best_ask) / 2.0
        elif best_bid is not None:
            return best_bid
        elif best_ask is not None:
            return best_ask
        return None

    def get_best_bid(self, order_depth: OrderDepth):
        if order_depth.buy_orders:
            best_bid = max(order_depth.buy_orders.keys())
            return best_bid, abs(order_depth.buy_orders[best_bid])
        return None, None

    def get_best_ask(self, order_depth: OrderDepth):
        if order_depth.sell_orders:
            best_ask = min(order_depth.sell_orders.keys())
            return best_ask, abs(order_depth.sell_orders[best_ask])
        return None, None


# In[ ]:




