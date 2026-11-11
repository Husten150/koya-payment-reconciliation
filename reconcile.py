#!/usr/bin/env python3
"""Reconcile payments using the latest event for each transaction.

Run: python3 reconcile.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

latest_by_txn = {}

with open("payments.jsonl", encoding="utf-8") as payments:
    for line in payments:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        txn_id = event.get("txn_id")
        timestamp = event.get("ts")
        if not txn_id or not timestamp:
            continue

        event_time = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        previous = latest_by_txn.get(txn_id)

        if previous is None or event_time >= previous[0]:
            latest_by_txn[txn_id] = (event_time, event)

count = 0
total = Decimal("0")

for _, event in latest_by_txn.values():
    if event.get("status") == "success":
        amount = str(event["amount"]).replace(",", "")
        total += Decimal(amount)
        count += 1

with open("expected.txt", encoding="utf-8") as expected_file:
    expected = int(expected_file.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful transactions, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    rounded_total = total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    print(f"Check passed: {count} successful transactions.")
    print(f"Your code: KOYA-{rounded_total}")
