
# Commands to generate fixtures

## checkout.Currency

The data dump needs to be performed in [UTF8 mode](https://docs.python.org/3/using/cmdline.html#cmdoption-X) to
preserve character encodings:

```pycon
python -Xutf8 -m manage dumpdata checkout.Currency --indent 4 -o currencies.json
```

## profiles.CountryInfo 

```pycon
python -m manage dumpdata profiles.CountryInfo --indent 4 -o countryinfo.json
```

## auth.Group

```pycon
python -m manage dumpdata auth.Group --indent 4 -o groups.json
```

## subscription.Subscription

```pycon
python -m manage dumpdata subscription.Subscription --indent 4 -o subscription.json
```

## recipes.Measure

```pycon
python -m manage dumpdata recipes.Measure --indent 4 -o data/fixtures/measure.json
```


# Commands to generate test fixtures

## subscription.SubscriptionFeature

```pycon
python -m manage dumpdata subscription.SubscriptionFeature --indent 4 -o subscription_feature_test.json
```

## checkout.CurrencyRate

Currency rates for tests

```pycon
python -m manage dumpdata checkout.CurrencyRate --indent 4 -o currencyrate_test.json
```

## subscription.Subscription

```pycon
python -m manage dumpdata subscription.Subscription --indent 4 -o subscription_test.json
```
