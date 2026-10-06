# Меры DAX

24 меры извлечены из семантической модели переданного проекта. Имена сохранены для сверки с PBIX.

[Метрики и фильтры](metrics.md) · [Модель данных](data-model.md)

## Total Users

```dax
Total Users =
CALCULATE(COUNTROWS(Users), TREATAS(VALUES('Date'[date]), Users[registration_day]))
```

## Active Users

```dax
Active Users =
CALCULATE(DISTINCTCOUNT(Interactions[user_id]), Interactions[interaction_type] = "viewed", TREATAS(VALUES('Date'[date]), Interactions[event_day]))
```

## Total Recommendations

```dax
Total Recommendations =
CALCULATE(COUNTROWS(Recommendations), TREATAS(VALUES('Date'[date]), Recommendations[recommendation_day]))
```

## Viewed Recommendations

```dax
Viewed Recommendations =
CALCULATE(COUNTROWS(Recommendations), Recommendations[viewed] = 1, TREATAS(VALUES('Date'[date]), Recommendations[recommendation_day]))
```

## Accepted Recommendations

```dax
Accepted Recommendations =
CALCULATE(COUNTROWS(Recommendations), Recommendations[accepted] = 1, TREATAS(VALUES('Date'[date]), Recommendations[recommendation_day]))
```

## Recommendation View Rate

```dax
Recommendation View Rate =
DIVIDE([Viewed Recommendations], [Total Recommendations])
```

## Recommendation Acceptance Rate

```dax
Recommendation Acceptance Rate =
DIVIDE([Accepted Recommendations], [Total Recommendations])
```

## Acceptance After View

```dax
Acceptance After View =
DIVIDE([Accepted Recommendations], [Viewed Recommendations])
```

## Completed Profile Users

```dax
Completed Profile Users =
CALCULATE(COUNTROWS(Users), Users[profile_completed] = 1, TREATAS(VALUES('Date'[date]), Users[registration_day]))
```

## Profile Completion Rate

```dax
Profile Completion Rate =
DIVIDE([Completed Profile Users], [Total Users])
```

## Routine Users

```dax
Routine Users =
CALCULATE(COUNTROWS(Users), Users[has_routine] = 1, TREATAS(VALUES('Date'[date]), Users[registration_day]))
```

## Routine Creation Rate

```dax
Routine Creation Rate =
DIVIDE([Routine Users], [Total Users])
```

## Average Recommendation Score

```dax
Average Recommendation Score =
CALCULATE(AVERAGE(Recommendations[compatibility_percent]), TREATAS(VALUES('Date'[date]), Recommendations[recommendation_day]))
```

## Existing Users

```dax
Existing Users =
CALCULATE(COUNTROWS(Users), Users[registration_day] <= MAX('Date'[date]))
```

## Average Recommendations per User

```dax
Average Recommendations per User =
DIVIDE([Total Recommendations], [Existing Users])
```

## Recommendation Recipients

```dax
Recommendation Recipients =
CALCULATE(DISTINCTCOUNT(Recommendations[user_id]), TREATAS(VALUES('Date'[date]), Recommendations[recommendation_day]))
```

## Average Recommendations per Recipient

```dax
Average Recommendations per Recipient =
DIVIDE([Total Recommendations], [Recommendation Recipients])
```

## Funnel Users

```dax
Funnel Users =
VAR StageNumber = SELECTEDVALUE(FunnelStages[stage_id])
RETURN CALCULATE(COUNTROWS(Users), Users[funnel_level] >= StageNumber, TREATAS(VALUES('Date'[date]), Users[registration_day]))
```

## Previous Stage Users

```dax
Previous Stage Users =
VAR StageNumber = SELECTEDVALUE(FunnelStages[stage_id])
RETURN IF(StageNumber > 1, CALCULATE([Funnel Users], REMOVEFILTERS(FunnelStages), FunnelStages[stage_id] = StageNumber - 1))
```

## Conversion Rate

```dax
Conversion Rate =
DIVIDE([Funnel Users], [Previous Stage Users])
```

## Drop Off Rate

```dax
Drop Off Rate =
VAR Conversion = [Conversion Rate]
RETURN IF(NOT ISBLANK(Conversion), 1 - Conversion)
```

## Overall Conversion

```dax
Overall Conversion =
DIVIDE([Funnel Users], [Total Users])
```

## Catalog Products

```dax
Catalog Products =
COUNTROWS(Products)
```

## Average Price

```dax
Average Price =
AVERAGE(Products[price])
```
