class RetrospectiveTanFly(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2019, 12, 13)
        self.SetCash(100000) 
        
        
        # a way to 
                
        # request the equity data in minute resolution
        self.AddEquity("SPY", Resolution.Minute)

        # define a 10-period ichimoku indicator with indicator constructor
        
        # notice the constructor is empty where the "" are.
        # also notice it's called "IchimokuKinkoHyo" not " self.ICHIMOKU" . thats how its done.
        self.ichimoku30 = IchimokuKinkoHyo("", 9, 26, 26, 52, 26, 26)
        self.ichimoku4H = IchimokuKinkoHyo("", 9, 26, 26, 52, 26, 26)
        self.ichimokuDay = IchimokuKinkoHyo("", 9, 26, 26, 52, 26, 26)
        self.ichimokuWeek = IchimokuKinkoHyo("", 9, 26, 26, 52, 26, 26)
        

        # create the 30-minutes data consolidator
        self.thirtyMinuteConsolidator = TradeBarConsolidator(timedelta(minutes=30))
        self.fourHourConsolidator = TradeBarConsolidator(timedelta(minutes=240))
        self.dayConsolidator = TradeBarConsolidator(timedelta(days=1))
        self.weekConsolidator = TradeBarConsolidator(timedelta(days=5))
        


        self.thirtyMinuteConsolidator.DataConsolidated += self.thirtyMinuteBarHandler
        self.fourHourConsolidator.DataConsolidated += self.fourHourBarHandler
        self.dayConsolidator.DataConsolidated += self.dayBarHandler
        self.weekConsolidator.DataConsolidated += self.weekBarHandler
        

        self.SubscriptionManager.AddConsolidator("SPY", self.thirtyMinuteConsolidator)
        self.SubscriptionManager.AddConsolidator("SPY", self.fourHourConsolidator)
        self.SubscriptionManager.AddConsolidator("SPY", self.dayConsolidator)
        self.SubscriptionManager.AddConsolidator("SPY", self.weekConsolidator)


        # register the 30-minute consolidated bar data to automatically update the indicator
        self.RegisterIndicator("SPY", self.ichimoku30, self.thirtyMinuteConsolidator)
        self.RegisterIndicator("SPY", self.ichimoku4H, self.fourHourConsolidator)
        self.RegisterIndicator("SPY", self.ichimokuDay, self.dayConsolidator)
        self.RegisterIndicator("SPY", self.ichimokuWeek, self.dayConsolidator)
        
        self.SetWarmUp(timedelta(days= 370))

                
                

    def OnData(self, data):
        ''' OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
            
        '''
    def weekBarHandler(self, sender, bar):
        if self.IsWarmingUp: return
        
        self.Plot("plot","week", self.ichimokuWeek.Kijun.Current.Value)
        
              
    def dayBarHandler(self, sender, bar):
        if self.IsWarmingUp: return
        
        self.Plot("plot","day", self.ichimokuDay.Kijun.Current.Value)
        
    def fourHourBarHandler(self, sender, bar):
        if self.IsWarmingUp: return

        self.Plot("plot","4", self.ichimoku4H.Kijun.Current.Value)      
       
    
      
    def thirtyMinuteBarHandler(self, sender, bar):
        if self.IsWarmingUp: return

        self.Plot("plot","30", self.ichimoku30.Kijun.Current.Value)
        
      
        # Check if we're not invested and then put portfolio 100% in the SPY ETF.      
        if not self.Portfolio.Invested:
           self.SetHoldings("SPY", 1)
