
// =============================================
// Power Query M - FX Exposure & Hedging Dashboard
// =============================================

// --- Step 1: Load fx_exposures.csv ---
let
    Source = Csv.Document(File.Contents("fx_exposures.csv"), [Delimiter=",", Columns=12, Encoding=1252, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders,{
        {"TradeID", Int64.Type},
        {"Notional", type number},
        {"Maturity_Days", Int64.Type},
        {"Exposure", type number},
        {"Hedgeable", type number},
        {"Hedge_Limit", type number},
        {"Trade_Date", type date}
    }),
    
    // SQL-equivalent: Add hedging flag
    AddedHedgeFlag = Table.AddColumn(ChangedTypes, "IsHedgeable", 
        each if [Maturity_Days] < 90 then 1 else 0, Int64.Type),
    
    // SQL-equivalent: Add scenario columns (for slicer simulation)
    AddedBaseExposure   = Table.AddColumn(AddedHedgeFlag,   "Exposure_Base",   each [Exposure], type number),
    AddedStressExposure = Table.AddColumn(AddedBaseExposure,"Exposure_Stress",  each [Exposure] * 1.5, type number),
    AddedShockExposure  = Table.AddColumn(AddedStressExposure,"Exposure_Shock10",each [Exposure] * 1.1, type number)
    
in AddedShockExposure


// --- Step 2: Load ecb_forwards.csv ---
let
    Source = Csv.Document(File.Contents("ecb_forwards.csv"), [Delimiter=",", Columns=8, Encoding=1252]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders,{
        {"Date", type date},
        {"Spot_Rate", type number},
        {"Forward_1M", type number},
        {"Forward_3M", type number},
        {"Forward_6M", type number},
        {"Implied_Vol_1M", type number},
        {"Implied_Vol_3M", type number}
    }),
    
    // Pivot-equivalent: Add forward spread columns
    AddedSpread1M = Table.AddColumn(ChangedTypes, "Fwd_Spread_1M", 
        each [Forward_1M] - [Spot_Rate], type number),
    AddedSpread3M = Table.AddColumn(AddedSpread1M, "Fwd_Spread_3M", 
        each [Forward_3M] - [Spot_Rate], type number)
        
in AddedSpread3M


// --- Step 3: Aggregated Exposure by Currency (SQL GROUP BY equivalent) ---
let
    Source = Excel.CurrentWorkbook(){[Name="fx_exposures"]}[Content],
    GroupedRows = Table.Group(Source, {"Currency", "Subsidiary", "Counterparty"}, {
        {"Net_Exposure", each List.Sum([Exposure]), type number},
        {"Total_Hedgeable", each List.Sum([Hedgeable]), type number},
        {"Trade_Count", each Table.RowCount(_), Int64.Type},
        {"Avg_Maturity", each List.Average([Maturity_Days]), type number}
    }),
    AddedHedgeRatio = Table.AddColumn(GroupedRows, "Hedge_Ratio",
        each if [Net_Exposure] = 0 then 0 
             else [Total_Hedgeable] / Number.Abs([Net_Exposure]), type number)
in AddedHedgeRatio


// --- Step 4: Date Dimension Table ---
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2024, 12, 31),
    DateList = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1,0,0,0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    ChangedType = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    AddedYear = Table.AddColumn(ChangedType, "Year", each Date.Year([Date]), Int64.Type),
    AddedMonth = Table.AddColumn(AddedYear, "Month", each Date.Month([Date]), Int64.Type),
    AddedMonthName = Table.AddColumn(AddedMonth, "MonthName", each Date.ToText([Date], "MMM"), type text),
    AddedQuarter = Table.AddColumn(AddedMonthName, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text)
in AddedQuarter
