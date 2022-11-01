#!/usr/bin/env python3

import pandas as pd

data = pd.read_csv("db/data/mosru.csv", delimiter="$")
data.to_csv("db/data/mosru_fix.csv", sep="$", index=False)
