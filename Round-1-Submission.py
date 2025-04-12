#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
import string

class Trader:

    def __init__(self):
        self.MAX_TRADE_AGAINST = 12
        self.EDGE = -0.2
        self.BETA = 0.75
        self.ewma_returns_1 = 0
        self.ewma_returns_3 = 0
        self.ewma_returns_50 = 0
        self.prev_swmid = 2027
        self.iteration = 0

        self.INK_wmid = []
        
    def run(self, state: TradingState):
        self.iteration += 1
        result = {}

        # SQUID_INK
        orders: List[Order] = []
        # INK_order_depth = state.order_depths["SQUID_INK"]
        # best_ask, best_ask_vol = list(INK_order_depth.sell_orders.items())[0]
        # best_bid, best_bid_vol = list(INK_order_depth.buy_orders.items())[0]
        # best_ask_vol = -best_ask_vol #make it positive
        # temp_swmid = (best_ask * (best_bid_vol**0.5) + best_bid * (best_ask_vol**0.5))/((best_bid_vol**0.5)+(best_ask_vol**0.5))
        # self.INK_wmid.append(temp_swmid)
        # print("Iteration: ", self.iteration)
        # if self.iteration > 6:
        #     mean = np.mean(self.INK_wmid[-3:])
        #     std = np.std(self.INK_wmid[-3:])
        #     z = (temp_swmid - mean) / std
        #     spread = (best_ask - best_bid) / std
        #     if "SQUID_INK" in state.position:
        #         position_ink = state.position["SQUID_INK"]
        #     else:
        #         position_ink = 0  # Default to 0 if not found
        #     if z > 1.5 + spread and position_ink > -50: # sell
        #         size = -max(0, position_ink + 50)
        #         orders.append(Order("SQUID_INK", best_bid-1, size))
        #     elif z < -1.5 - spread and position_ink < 50: # buy
        #         size = max(0, 50 - position_ink)
        #         orders.append(Order("SQUID_INK", best_ask+1, size))
        #     print("Z", z)
        #     print("swmid", temp_swmid)
        #     print("spread: ", spread+1.5)
        #     print("position", position_ink)
        result["SQUID_INK"] = orders


        
        # KELP
        orders: List[Order] = []
        result["KELP"] = orders

        #RAINFOREST_RESIN
        orders: List[Order] = []
        if "RAINFOREST_RESIN" in state.position:
            position_resin = state.position["RAINFOREST_RESIN"]
        else:
            position_resin = 0  # Default to 0 if not found
        #Buy resin at any price 999 or less
        orders.append(Order("RAINFOREST_RESIN", 9999, max(0, 50 - position_resin)))
        #Sell resin at any price 1001 or more
        orders.append(Order("RAINFOREST_RESIN", 10001, -max(0, 50 + position_resin)))
        result["RAINFOREST_RESIN"] = orders
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1
        return result, conversions, traderData


# In[ ]:




