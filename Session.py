import robin_stocks


class Session:
    username = None
    password = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    ####################################################
    #                     Session                      #
    ####################################################

    def login(self):
        robin_stocks.login(self.username, self.password)

    def logout(self):
        robin_stocks.logout()

    ####################################################
    #                 Custom API Funcs                 #
    ####################################################

    def getShareData(self, symbol):
        holdings = self.masterFormat(robin_stocks.build_holdings(), "holding")
        stock = None
        for holding in holdings:
            if robin_stocks.get_name_by_symbol(symbol) == holding.get("name"):
                stock = holding
        stock["sell_val"] = str(round(float(stock.get("average_buy_price")) - (float(stock.get("average_buy_price")) * 0.07), 2))
        return stock

    def masterFormat(self, data, formatType: str):
        formats = ["dividend", "profile", "holding", "mover", "price", "search"]
        results = []
        for item in formats:
            if item == formatType.lower():
                results = self.formatHandler(data, item)
        return results

    def formatHandler(self, data, formatType):
        result = []
        if formatType == "dividend":
            result = self.formatDividends(data)
        elif formatType == "profile":
            result = self.formatProfile(data)
        elif formatType == "holding":
            result = self.formatHoldings(data)
        elif formatType == "mover":
            result = self.formatMovers(data)
        elif formatType == "price":
            result = self.formatPrice(data)
        elif formatType == "search":
            result = self.formatSearch(data)
        return result

    def formatProfile(self, profile):
        equity = profile.get("equity")
        cash = profile.get("cash")
        return {"equity": equity, "cash": cash}

    def formatDividends(self, a):
        x = []
        for b in a:
            b = self.formatDividend(b)
            x.append(b)
        return x

    def formatDividend(self, dividend):
        data = ["state", "amount", "paid_at", "rate"]
        formatted = {}
        for item in data:
            formatted[item] = dividend.get(item)
        formatted["shares"] = str(round(float(formatted["amount"])/float(formatted["rate"])))
        return formatted

    def formatHolding(self, holding):
        data = ["name", "price", "quantity", "equity", "percentage", "average_buy_price"]
        formatted = {}
        for item in data:
            formatted[item] = holding.get(item)
        return formatted

    def formatHoldings(self, a):
        x = []
        for b in a:
            y = self.formatHolding(a[b])
            x.append(y)
        return x

    def formatMover(self, mover):
        symbol = mover.get("symbol")
        movement = mover.get("price_movement")["market_hours_last_movement_pct"]
        return {"symbol": symbol, "movement": movement}

    def formatMovers(self, a):
        x = []
        for b in a:
            y = self.formatMover(b)
            x.append(y)
        return x

    def formatPrice(self, price):
        return round(float(price[0]), 2)

    def formatSearch(self, result):
        data = ["open", "high", "low", "high_52_weeks", "low_52_weeks", "dividend_yield", "description", "industry"]
        search = {}
        for item in data:
            search[item] = result[0].get(item)
        return search

    ####################################################
    #                     Profile                      #
    ####################################################

    def getProfile(self):
        return self.masterFormat(robin_stocks.build_user_profile(), "profile")

    ####################################################
    #                    Dividends                     #
    ####################################################

    def getDividends(self):
        return self.masterFormat(robin_stocks.get_dividends(), "dividend")

    ####################################################
    #                     Holdings                     #
    ####################################################

    def getHoldings(self):
        return self.masterFormat(robin_stocks.build_holdings(), "holding")

    def buildHolding(self, name):
        holdings = self.getHoldings()
        for holding in holdings:
            if holding.get("name") == name:
                return holding

    def getSharesHeld(self, name: str):
        holdings = self.getHoldings()
        for holding in holdings:
            if holding.get("name") == name:
                return holding.get("quantity")

    ####################################################
    #                    Top Movers                    #
    ####################################################

    def getMovers(self, moveType: str):
        return self.masterFormat(robin_stocks.get_top_movers(moveType), "mover")

    ####################################################
    #                   Place Orders                   #
    ####################################################

    def placeSellOrder(self, stock: dict):
        preSaleCard = self.buildPreSaleCard(stock.get("symbol"))
        sell_val = self.getSellVal(preSaleCard)
        if stock.get("price") == sell_val:
            print("Sell")  # Replace with actual sell order later

    def buildPreSaleCard(self, symbol):
        stockName = self.getSymbolName(symbol)
        latest_price = self.getLatestPrice(symbol)
        holding = self.buildHolding(stockName)
        average_buy_price = holding.get("average_buy_price")
        investment_percentage_gain = round(((float(latest_price) - float(average_buy_price)) / float(average_buy_price) * 100), 2)
        return {"name": stockName, "latest_price": latest_price, "average_buy_price": average_buy_price,
                "investment_percentage_gain": investment_percentage_gain, "quantity": holding.get("quantity")}


    def getSellVal(self, preSaleCard):
        purchase_price = preSaleCard.get("average_buy_price")
        sell_at = round((float(purchase_price) - (float(purchase_price) * 0.07)), 2)
        return sell_at

    ####################################################
    #                      Watch                       #
    ####################################################

    def watchStocks(self, *args):
        watchlist = self.buildWatchList(args)
        while True:
            if len(watchlist) == 0:
                break
            updatedWatchlist = self.buildWatchList(args)
            for stock in watchlist:
                i = watchlist.index(stock)
                if updatedWatchlist[i] == watchlist[i]:
                    watchlist[i].update({"price": updatedWatchlist[i].get("price")})
                    if watchlist[i].get("sell_val") >= watchlist[i].get("price"):
                        if watchlist[i].get("amount") <= 1:
                            self.placeSellOrder(watchlist[i])
                    else:
                        self.placeSellOrder(watchlist[i])
                        print("Hold")

    def buildWatchList(self, args: tuple):
        stocks = []
        for arg in args:
            price = self.getLatestPrice(arg)
            amount = self.getSharesHeld(self.getSymbolName(arg))
            if amount is None:
                amount = 0
            sell_val = self.getSellVal(self.buildPreSaleCard(arg))
            stocks.append({"symbol": arg, "amount": amount, "price": price, "sell_val": sell_val})
        return stocks

    ####################################################
    #                      Price                       #
    ####################################################

    def getLatestPrice(self, symbol):
        return self.masterFormat(robin_stocks.get_latest_price(symbol), "price")

    ####################################################
    #                      Search                      #
    ####################################################

    def searchSymbol(self, symbol):
        return self.masterFormat(robin_stocks.get_fundamentals(symbol), "search")

    def getSymbolName(self, symbol):
        return robin_stocks.get_name_by_symbol(symbol)

    def searchSymbols(self, *args):
        results = []
        for arg in args:
            searchResults = self.searchSymbol(arg)
            results.append(searchResults)
        return results
