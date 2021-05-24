### <summary>
### Simple SMA Strategy intended to provide a minimal algorithm example using
### one indicator with the most basic plotting
### </summary>
from datetime import timedelta
from System.Drawing import Color

# TODO add RSI. https://tradeciety.com/the-complete-ichimoku-trading-guide-how-to-use-the-ichimoku-indicator/
class SMAAlgorithm(QCAlgorithm):
    
    # 1 - Add the FANG stocks (Facebook, Amazon, , Netflix, Google)
    # 2 - Cycle through stocks
    # 3 - Cycle through list adding each equity
    # 3 - Create an indicator dict like backtrader

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''
        
        # Set our main strategy parameters
        self.SetStartDate(2010,1,1)    # Set Start Date
        self.SetEndDate(2021,1,1)      # Set End Date
        self.SetCash(10000)            # Set Strategy Cash
        
        SMA_Period    = 14                # SMA Look back period 
        self.SMA_OB   = 75                # SMA Overbought level
        self.SMA_OS   = 50                # SMA Oversold level
        self.Allocate = 1              # Percentage of captital to allocate
        
        
        
        self.Equities = [ "SPY"]
        #self.smaDaily = SMA(symbol, 200, Resolution.Daily)
        
        self.Indicators = dict()
        # store rollingwindows
        self.SymbolData = dict()
        self.Charts = dict()
        self.Consolidators = dict()
        
        # Find more symbols here: http://quantconnect.com/data
        for Symbol in self.Equities:
            self.Consolidators[Symbol] = dict()
            
            self.AddEquity(Symbol, Resolution.Minute)
        
            # Each Equity requires its own consoilidator! See: 
            # https://www.quantconnect.com/forum/discussion/1936/multiple-consolidators/p1
            # https://www.quantconnect.com/forum/discussion/1587/multiple-symbol-indicator-values-in-consolidated-bar-handler/p1
            # ------------------------
            # Create our consolidators
            self.Consolidators[Symbol]['onDayCon'] = TradeBarConsolidator(timedelta(days=1))
            self.Consolidators[Symbol]['minutesCon'] = TradeBarConsolidator(timedelta(minutes=60))

            # Register our Handlers
            self.Consolidators[Symbol]['onDayCon'].DataConsolidated += self.onDay
            self.Consolidators[Symbol]['minutesCon'].DataConsolidated += self.minutes20

            self.Indicators[Symbol] = dict()
            self.Indicators[Symbol]['SMA'] = dict()
            self.Indicators[Symbol]['Ichimoku'] = dict()
            self.Indicators[Symbol]['ADX']= dict()

            
            self.Indicators[Symbol]['SMA']['SMA200'] = self.SMA(Symbol, 200, Resolution.Daily)
            self.Indicators[Symbol]['SMA']['SMA50'] = self.SMA(Symbol, 50, Resolution.Daily)
            self.Indicators[Symbol]['Ichimoku'] = self.ICHIMOKU(Symbol,9, 26, 26, 52, 26, 26, Resolution.Daily) 
            self.Indicators[Symbol]['ADX'] = self.ADX(Symbol, 14, Resolution.Daily)

            # Register the indicaors with our stock and consolidator

            self.RegisterIndicator(Symbol, self.Indicators[Symbol]['SMA']['SMA50'], self.Consolidators[Symbol]['onDayCon'])
            self.RegisterIndicator(Symbol, self.Indicators[Symbol]['SMA']['SMA200'], self.Consolidators[Symbol]['onDayCon'])
            self.RegisterIndicator(Symbol, self.Indicators[Symbol]['Ichimoku'], self.Consolidators[Symbol]['onDayCon'])
            self.RegisterIndicator(Symbol, self.Indicators[Symbol]['ADX'], self.Consolidators[Symbol]['onDayCon'])


            # Finally add our consolidators to the subscription
            # manager in order to receive updates from the engine
            self.SubscriptionManager.AddConsolidator(Symbol, self.Consolidators[Symbol]['onDayCon'])
            self.SubscriptionManager.AddConsolidator(Symbol, self.Consolidators[Symbol]['minutesCon'])

            self.Charts[Symbol] = dict()
            # Plot the SMA
            SMAChartName = Symbol+" TradePlot"
            self.Charts[Symbol][' TradePlot'] = Chart(SMAChartName, ChartType.Stacked)
            self.Charts[Symbol][' TradePlot'].AddSeries(Series('Buy', SeriesType.Scatter, '$', Color.Green, ScatterMarkerSymbol.Diamond))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series('Sell', SeriesType.Scatter, '$', Color.Red, ScatterMarkerSymbol.Diamond))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series("200", SeriesType.Line,"", Color.Red))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series("50", SeriesType.Line,"", Color.Blue))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series("close", SeriesType.Line,"", Color.Gray))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series("SenkouA", SeriesType.Line,"", Color.Orange))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series('SenkouB', SeriesType.Line,"", Color.Brown))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series('Tenkan', SeriesType.Line, "", Color.Pink))
            self.Charts[Symbol][' TradePlot'].AddSeries(Series('Kijun', SeriesType.Line,"", Color.Purple))
            
            self.AddChart(self.Charts[Symbol][' TradePlot'])
            '''
            ADXChartName = Symbol+" ADXPlot"
            self.Charts[Symbol][' ADXPlot'] = Chart(ADXChartName, ChartType.Stacked)
            self.Charts[Symbol][' ADXPlot'].AddSeries(Series("ADX", SeriesType.Line,"", Color.Blue))
            self.Charts[Symbol][' ADXPlot'].AddSeries(Series("PlusADX", SeriesType.Line,"", Color.Green))
            self.Charts[Symbol][' ADXPlot'].AddSeries(Series("MinusADX", SeriesType.Line,"", Color.Red))
            self.AddChart(self.Charts[Symbol][' ADXPlot'])
            '''
            
            # make rollingWindows
            # contain the different rollingwindows
            
           
            self.SymbolData[Symbol] = dict()
            self.SymbolData[Symbol]['closeRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['senkouARw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['senkouBRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['minusADXRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['plusADXRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['tenkanRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['kijunRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['topCloudlineRw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['sma50Rw'] = RollingWindow[float](2)
            self.SymbolData[Symbol]['sma200Rw'] = RollingWindow[float](2)



            self.SymbolData[Symbol]['recentADXCross'] = False
            self.SymbolData[Symbol]['ADXCrossDayCounter'] = 0
            self.SymbolData[Symbol]['recentCloudCross'] = False
            self.SymbolData[Symbol]['cloudCrossDayCounter'] = 0
            self.SymbolData[Symbol]['invested'] = False
            self.SymbolData[Symbol]['buyPrice'] = 0

            
            '''
            self.SymbolData[Symbol] = dict()
            self.SymbolData[Symbol]["closeRw"]= dict()
            self.SymbolData[Symbol]["Testrw"]= RollingWindow[float](2)
            self.SymbolData[Symbol]["Testrw"]= RollingWindow[float](2)
            '''
            
            
            
                
            
        # Ensure that the Indicator has enough data before trading.
        
        self.SetWarmUp(timedelta(days= 200))
        self.dayCount = 0
        self.countMinutes = 0
        
       
        
    
    def onDay(self,sender,bar):

        
        # Make sure we are not warming up 
        
        if self.IsWarmingUp: return
         
        Symbol = str(bar.get_Symbol())
        close= bar.Close
        Volume = bar.Volume

        #self.Plot(Symbol+" volume", 'Buying Volume', Volume)
        
            
        
        SMA200 = self.Indicators[Symbol]['SMA']['SMA200'].Current.Value
        SMA50 = self.Indicators[Symbol]['SMA']['SMA50'].Current.Value
        tenkan = self.Indicators[Symbol]['Ichimoku'].Tenkan.Current.Value
        kijun = self.Indicators[Symbol]['Ichimoku'].Kijun.Current.Value
        senkouA = self.Indicators[Symbol]['Ichimoku'].SenkouA.Current.Value
        senkouB = self.Indicators[Symbol]['Ichimoku'].SenkouB.Current.Value
        chikou = self.Indicators[Symbol]['Ichimoku'].Chikou.Current.Value
        

        
        ADX =  self.Indicators[Symbol]['ADX'].Current.Value
        minusADX = self.Indicators[Symbol]['ADX'].NegativeDirectionalIndex.Current.Value
        plusADX = self.Indicators[Symbol]['ADX'].PositiveDirectionalIndex.Current.Value
        senkouAFuture = ( self.Indicators[Symbol]['Ichimoku'].Tenkan.Current.Value + self.Indicators[Symbol]['Ichimoku'].Current.Value) / 2 
        senkouBFuture = (self.Indicators[Symbol]['Ichimoku'].SenkouBMaximum.Current.Value + self.Indicators[Symbol]['Ichimoku'].SenkouBMinimum.Current.Value) / 2        
        topCloudline= 0
        if senkouA >= senkouB: 
            topCloudline = senkouA
        if senkouB >= senkouA:
            topCloudline = senkouB
        


        
        #fill rolling windows
        self.SymbolData[Symbol]["closeRw"].Add(close)
        self.SymbolData[Symbol]["senkouBRw"].Add(senkouB)
        self.SymbolData[Symbol]["senkouARw"].Add(senkouA)
        self.SymbolData[Symbol]["minusADXRw"].Add(minusADX)
        self.SymbolData[Symbol]["plusADXRw"].Add(plusADX)
        self.SymbolData[Symbol]["tenkanRw"].Add(tenkan)
        self.SymbolData[Symbol]["kijunRw"].Add(kijun)
        self.SymbolData[Symbol]["sma50Rw"].Add(SMA50)
        self.SymbolData[Symbol]["sma200Rw"].Add(SMA200)

        
        self.SymbolData[Symbol]["topCloudlineRw"].Add(topCloudline)


        if not self.SymbolData[Symbol]["closeRw"].IsReady and not self.SymbolData[Symbol]["senkouBRw"].IsReady: return 
        
        pastSenkouB = self.SymbolData[Symbol]["senkouBRw"][1]
        pastPlusADX = self.SymbolData[Symbol]["plusADXRw"][1]
        pastMinusADX = self.SymbolData[Symbol]['minusADXRw'][1]
        pastTenkan = self.SymbolData[Symbol]['tenkanRw'][1]
        pastKijun = self.SymbolData[Symbol]['kijunRw'][1]

        pastTopCloudline = self.SymbolData[Symbol]['topCloudlineRw'][1]
        pastClose = self.SymbolData[Symbol]['closeRw'][1]
        pastSMA50 = self.SymbolData[Symbol]["sma50Rw"][1]
        pastSMA200 = self.SymbolData[Symbol]["sma200Rw"][1]

        ADXCrossDayCounter = self.SymbolData[Symbol]['ADXCrossDayCounter']
        recentADXCross = self.SymbolData[Symbol]['recentADXCross']
        cloudCrossDayCounter = self.SymbolData[Symbol]['cloudCrossDayCounter']
        recentCloudCross = self.SymbolData[Symbol]['recentCloudCross']        
        

        self.Plot(Symbol +' TradePlot', '200', SMA200)
        self.Plot(Symbol +' TradePlot', '50', SMA50)
        self.Plot(Symbol +' TradePlot', 'close', close)
        self.Plot(Symbol +' TradePlot', 'Tenkan', tenkan)
        self.Plot(Symbol +' TradePlot', 'Kijun', kijun)
        self.Plot(Symbol +' TradePlot', 'SenkouA', senkouA)
        self.Plot(Symbol +' TradePlot', 'SenkouB', senkouB)

        #self.Plot(Symbol +' ADXPlot', "ADX",ADX)
        #self.Plot(Symbol +' ADXPlot', "PlusADX", plusADX)
        #self.Plot(Symbol +' ADXPlot', "MinusADX", minusADX)
        
        # TODO add SMA 50 200
        # how can i pick it up if it falls of? 
        ''' if kijun stop it out and a few days later it picks up again? 
        then buy again.  
        So when if sells start counting. like 3 days.
        and if all the conditions are there then buy 
            what are the conditions: 
            -the close is higher than kijun. 
            - kijun is higher than cloud. 
            - maybe tenkan and kijun are close. 
        
        '''
        # if close > topCloudline and pastClose < pastTopCloudline: 

        if SMA50 > SMA200 and pastSMA50 < pastSMA200: 
            self.SymbolData[Symbol]['recentCloudCross'] = True

                
       # if tenkan > topCloudline and pastTenkan < pastTopCloudline: 
       #     recentCloudCross = True
       #     cloudCrossDayCounter = 0

        if self.SymbolData[Symbol]['recentCloudCross']:
            self.SymbolData[Symbol]['cloudCrossDayCounter'] += 1


        if self.SymbolData[Symbol]['cloudCrossDayCounter'] == 10 or close < topCloudline:
            self.SymbolData[Symbol]['recentCloudCross']  = False 
            self.SymbolData[Symbol]['cloudCrossDayCounter'] = 0
        
        #self.Securities[Symbol].Invested:    
        if not self.SymbolData[Symbol]['invested']:
            # alternative strategy  # https://tradingstrategyguides.com/best-ichimoku-strategy/

            
            # 11 april TO DO ny plan see video https://www.youtube.com/watch?v=8gWIykJgMNY
            # rules : 
            # 0: SMA 50 > 200
            # 0,1 : sma 50 slope is positive or flat. 
            # 1: price close outside the cloud?
            # 2: future cloud green? 
            # 3: is chikou out of cloud? 
            # 4: is tenkan above kijun? 
            # stop loss dedenps on distance to cloud. (maybe not so good?) 
            #   if its "far" from the cloud set stop at kijun current kijun. 
            #   if its close set it at the bottom of cloud.             
            
            
            
            # 1: price close outside the cloud?
            
            
            # TODO 12 apil. change sell conditions:
            # give different sell options. like if its going flat for a long time jump out. and jump on agian. 
            # try strategy. sell when it has reached a certan procentage. 
            # also sell after a certain procentage? 
            # also use the patteren that 200 sma and 50 sma gets wider apart and close when the large trend is over. 
            # buy in the beginning of this trend. 
            # drop the 20 minute time frame. 
            # try this simple strategy:
            # buy when at golden cross. sell when slope of sma50is falling. 
            # SERIUSLY TRY THIS. its better to make money on a long haul then nothing at all. !!! for fuck sake.
            # try also to buy before the golden cross. 
                # if it looks like the golden cross is near. its also ok. 
                # So basicly if the sma50< close. and sma 50 is positive. 
                # try to only using sma50 and the cloud for buying.
                # and dont buy when the sma 200 and sma 50 starts squeezing together in the end. 
            
            # if golden cross buy and wait untill it rises 50 percent. 
            
            # testing simple strategy. 14 april. 
            # buy on golden cross
            # if sma 50 is positive, and out of cloud. 
            # sell if kijun gets crosses * 0.96 %. 
            
            
            
            
            # use clasic ichimoku strategy. on "SPY", or upgoing  other companies. make sure 200 sma moves upwards.invest 100 % each time. 
            
            # aftale med sofus
            
            # køb efter golden cross med classsisk ichimoku. stå først af når death cross eller 5 % under sky. 

            # køb efter golden cross. 
                # if golden cross is recent 
                    # if 
            
            
            
            if self.SymbolData[Symbol]['recentCloudCross']:
                '''if close > SMA50: 
                    if SMA50 >=  pastSMA50: 
                        if close > topCloudline:
                            if senkouAFuture > senkouBFuture:
                                if tenkan > topCloudline:
                '''                
                self.SetHoldings(Symbol, self.Allocate) 
                self.SymbolData[Symbol]['invested'] = True
                self.Plot(Symbol +' TradePlot', 'Buy', close )
                self.SymbolData[Symbol]['buyPrice'] = close

            # sell
        if self.SymbolData[Symbol]['invested']:
            if SMA50 < pastSMA50: 
                self.Debug("sell")
                # Sell
                self.Liquidate(Symbol)
                self.SymbolData[Symbol]['invested'] = False
                self.Plot(Symbol +' TradePlot', 'Sell', close) 
            
            
                                
        
            '''    
            if SMA50 > SMA200:
                if SMA50 >=  pastSMA50: 
                    if self.SymbolData[Symbol]['recentCloudCross']:
                        if senkouAFuture > senkouBFuture:
                            #if chikou > topCloudline:
                                if tenkan > kijun: 
                                    self.SetHoldings(Symbol, self.Allocate) 
                                    self.SymbolData[Symbol]['invested'] = True
                                    self.Plot(Symbol +' TradePlot', 'Buy', close )
                

                          #  if pastSenkouB <=  senkouB: 
            '''
            '''
            # start day counter

                #if  close > tenkan>kijun> topCloudline:# and tenkan> kijun:
                    #if tenkan >= pastTenkan:
                    #if senkouAFuture> senkouBFuture:
                    #self.max = self.MAX(Symbol, [20, 40])

                    #check if max value. # there is no reason to do this. the crossing point is more important
                    #maxVal = max(list(self.SymbolData[Symbol]['closeRw']))
                    #if close >= maxVal: 
            '''
    def minutes20(self,sender,bar):
        pass
        '''
        if self.IsWarmingUp: return
        Symbol = str(bar.get_Symbol())

        if not self.SymbolData[Symbol]["closeRw"].IsReady and not self.SymbolData[Symbol]["senkouBRw"].IsReady: return 

        close = bar.Close
        
        senkouA = self.SymbolData[Symbol]["senkouARw"][0]
        senkouB =  self.SymbolData[Symbol]["senkouBRw"][0]
        kijun =  self.SymbolData[Symbol]["kijunRw"][0]
        pastSMA50 = self.SymbolData[Symbol]["sma50Rw"][1]
        
        SMA50 = self.Indicators[Symbol]['SMA']['SMA50'].Current.Value


        #ADX =  self.Indicators[Symbol]['ADX'].Current.Value
        #minusADX = self.Indicators[Symbol]['ADX'].NegativeDirectionalIndex.Current.Value
        #plusADX = self.Indicators[Symbol]['ADX'].PositiveDirectionalIndex.Current.Value
        
        
        # TODO 12 apil. change sell conditions: 
        # TODO indentify a plane. and stop it when it falls tough. 
        
        #if self.Securities[Symbol].Invested:
        if self.SymbolData[Symbol]['invested']:
            self.Debug(Symbol)
            
            self.Debug("Sell ")
            self.Debug(str( self.Securities[Symbol].Invested))
            self.Debug(str( self.SymbolData[Symbol]['invested']))
            #if close < senkouA or close < senkouB: #or close < kijun*0.96:
                
            if SMA50 <= pastSMA50: 
                self.Debug("sell")
                # Sell
                self.Liquidate(Symbol)
                self.SymbolData[Symbol]['invested'] = False
                self.Plot(Symbol +' TradePlot', 'Sell', close)   
        
        #debug
        
        if self.countMinutes> 3: return

        self.Debug(" 20Minutes")
        Symbol = str(bar.get_Symbol())
        self.Debug(Symbol)
        self.Debug(bar.Close)
        self.countMinutes  = self.countMinutes +  1 

        '''


        
    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        
        # Make sure we are not warming up 
        if self.IsWarmingUp: return
