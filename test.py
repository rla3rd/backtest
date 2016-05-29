import data
import Queue
import pgdb
import strategy
import portfolio
import datetime
import execution

db = pgdb.database('django.xml')
(conn, cursor) = db.getConnCursor()

sql = """
    select ticker 
    from signals.master 
    where exchange in ('XNYS', 'XASE', 'XNAS', 'XOTC') 
        and lower(name) like '%etf%' 
        and lower(name) like '%schwab%'
        and lower(name) not like '%bond%' 
    order by ticker
    """
cursor.execute(sql)
results = cursor.fetchall()
tickers = []
tAppend = tickers.append
for row in results:
        tAppend(row['ticker'])

tickers=['DIA']

events = Queue.Queue()

bars = data.HistoricDBDataHandler(events, tickers) 
strategy = strategy.BuyOnDipStrategy(bars, events)
port = portfolio.NaivePortfolio(bars, events, datetime.date(2014,1,1), initial_capital=5000, position_size=5000)
broker = execution.SimulatedExecutionHandler(events)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest == True:
        bars.update_bars()
    else:
        break
    
    # Handle the events
    while True:
        try:
            event = events.get(False)
        except Queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

    # 10-Minute heartbeat
    #    time.sleep(10*60)

port.create_equity_curve_dataframe()
port.output_summary_stats()
