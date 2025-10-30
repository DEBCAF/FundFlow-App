from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Iterable, List, Dict, Optional, Tuple

try:
    import pandas as pd
    import numpy as np
    from scipy.stats import linregress
except Exception:
    pd = None
    np = None
    linregress = None

from home.db_models import GroupTransaction, Group, Goal, GroupGoal, SavingChanges, User


def _to_dataframe(transactions: Iterable[Dict]) -> Optional["pd.Series"]:
    if pd is None:
        return None
    df = pd.DataFrame(transactions)
    if df.empty:
        return pd.Series(dtype=float)
    if 'date' not in df.columns or 'amount' not in df.columns:
        raise ValueError("transactions must include 'date' and 'amount' keys")
    df['date'] = pd.to_datetime(df['date'])
    daily = df.set_index('date').sort_index()['amount'].resample('D').sum()
    return daily


def rate_per_day(transactions: Iterable[Dict], lookback_days: int = 90) -> Optional[float]:
    """
    Estimate net savings rate per day from arbitrary transactions.

    Each transaction: {"date": datetime/date/str, "amount": float}
    Positive amount means inflow to savings; negative means outflow/spend.

    Uses pandas/scipy when available; otherwise a simple average fallback.
    Returns None if rate cannot be inferred (insufficient data).
    """
    daily = _to_dataframe(transactions)
    if daily is not None:
        try:
            recent = daily.loc[daily.index >= (daily.index.max() - pd.Timedelta(days=lookback_days))] if len(daily) else daily
        except Exception:
            recent = daily.last(f'{lookback_days}D') if len(daily) else daily
        if recent is None or len(recent) == 0:
            return None

        # Option B: robust weekly median (preferred)
        weekly = recent.resample('W').sum()
        robust = (weekly.median() / 7.0) if len(weekly) > 0 else None

        # Option C: slope of cumulative balance vs time
        slope_val = None
        if linregress is not None:
            cumsum = recent.cumsum().dropna()
            if len(cumsum) >= 5:
                x = (cumsum.index - cumsum.index[0]).days.values
                y = cumsum.values
                slope, _, _, _, _ = linregress(x, y)
                slope_val = float(slope)

        # Option A: simple mean
        simple = float(recent.mean()) if len(recent) > 0 else None

        for candidate in (robust, slope_val, simple):
            if candidate is not None and candidate == candidate:  # not NaN
                return float(candidate)
        return None

    buckets: Dict[date, float] = {}
    for tx in transactions:
        dt = tx.get('date')
        amt = float(tx.get('amount', 0.0))
        if isinstance(dt, datetime):
            d = dt.date()
        elif isinstance(dt, date):
            d = dt
        elif isinstance(dt, str):
            d = datetime.fromisoformat(dt).date()
        else:
            continue
        buckets[d] = buckets.get(d, 0.0) + amt
    if not buckets:
        return None
    cutoff = date.today() - timedelta(days=lookback_days)
    vals = [v for d, v in buckets.items() if d >= cutoff]
    if not vals:
        vals = list(buckets.values())
    if not vals:
        return None
    return sum(vals) / max(1, len(vals))


def estimate_eta(remaining_amount: float, rate_per_day: Optional[float]) -> Optional[date]:
    """
    Given remaining amount and daily rate, return ETA date or None if not achievable.
    """
    if rate_per_day is None or rate_per_day <= 0:
        return None
    days_needed = remaining_amount / rate_per_day
    days_whole = int(days_needed) if days_needed.is_integer() else int(days_needed) + 1
    return date.today() + timedelta(days=days_whole)

def rate_breakdown(rate_per_day: Optional[float]) -> Dict[str, Optional[float]]:
    """
    Provide per-day/week/month equivalents for a rate.
    """
    if rate_per_day is None:
        return {"per_day": None, "per_week": None, "per_month": None}
    return {
        "per_day": rate_per_day,
        "per_week": rate_per_day * 7.0,
        "per_month": rate_per_day * 30.0,
    }

def required_rate(remaining_amount: float, days: int) -> Optional[float]:
    if days <= 0:
        return None
    return remaining_amount / float(days)

def group_transactions_as_movements(group_id: int, approved_only: bool = True) -> List[Dict]:
    """
    Load group transactions as generic movements (positive=inflow, negative=outflow).
    """
    q = GroupTransaction.query.filter_by(group_id=group_id)
    if approved_only:
        q = q.filter_by(status='approved')
    movements: List[Dict] = []
    for tx in q.order_by(GroupTransaction.occurred_at.asc()).all():
        movements.append({
            "date": tx.occurred_at,
            "amount": float(tx.amount),
            "id": tx.id,
            "type": "transaction"
        })
    try:
        completed_goals = GroupGoal.query.filter_by(group_id=group_id).filter_by(status='approved').all()
    except Exception:
        completed_goals = []

    for g in completed_goals:
        dt = getattr(g, 'approved_at', None)
        if dt is None:
            # fallback to now
            dt = datetime.utcnow()
        amount = -float(g.target_amount) if getattr(g, 'target_amount', None) is not None else 0.0
        movements.append({
            "date": dt,
            "amount": amount,
            "id": f"goal:{g.id}",
            "type": "goal_allocation",
            "goal_id": g.id,
            "goal_title": getattr(g, 'title', None)
        })
    try:
        movements.sort(key=lambda m: m.get('date'))
    except Exception:
        pass

    return movements

def user_transactions_as_movements(user: User) -> List[Dict]:
    """
    Load user transactions as generic movements (positive=inflow, negative=outflow).
    """
    q = SavingChanges.query.filter_by(user_id=user.id)
    movements: List[Dict] = []
    for sc in q.order_by(SavingChanges.date_time.asc()).all():
        movements.append({
            "date": sc.date_time,
            "amount": float(sc.amount),
            "id": sc.id
        })
    return movements

def analyse_group(group: Group, goals: Iterable[GroupGoal], group_balance: float) -> Dict[int, Dict[str, Optional[float]]]:
    """
    For a group and its goals, infer current daily savings rate from transactions and
    estimate ETA and rate breakdown for each goal.

    Returns mapping goal_id -> {"remaining", "eta_ts", "rate_per_day", "per_week", "per_month"}
    """
    tx = group_transactions_as_movements(group.id, approved_only=True)
    rate = rate_per_day(tx)
    results: Dict[int, Dict[str, Optional[float]]] = {}
    for g in goals:
        remaining = max(0.0, float(g.target_amount) - float(group_balance))
        eta = estimate_eta(remaining, rate)
        rb = rate_breakdown(rate)
        days = 30
        try:
            if getattr(g, 'deadline', None):
                dl = g.deadline
                if isinstance(dl, datetime):
                    dl_date = dl.date()
                else:
                    dl_date = dl
                days_left = (dl_date - date.today()).days
                days = max(1, days_left) if days_left is not None else 30
        except Exception:
            days = 30
        required_daily = required_rate(remaining, days)
        required_daily_30 = required_daily
        results[g.id] = {
            "remaining": remaining,
            "rate_per_day": rb["per_day"],
            "rate_per_week": rb["per_week"],
            "rate_per_month": rb["per_month"],
            "eta_ts": None if eta is None else int(datetime.combine(eta, datetime.min.time()).timestamp()),
            "required_daily_30": required_daily_30,
            "progress_percent": (group_balance / g.target_amount * 100) if g.target_amount > 0 else 0
        }
    return results

def analyse_user(user: User, goals: Iterable[Goal], current_savings: float) -> Dict[int, Dict[str, Optional[float]]]:
    """
    Analyse a user's goals and transactions.
    """
    tx = user_transactions_as_movements(user)
    rate = rate_per_day(tx)
    results: Dict[int, Dict[str, Optional[float]]] = {}
    for g in goals:
        remaining = max(0.0, float(g.target_amount) - float(current_savings))
        days = 30
        try:
            if getattr(g, 'deadline', None):
                dl = g.deadline
                if isinstance(dl, datetime):
                    dl_date = dl.date()
                else:
                    dl_date = dl
                days_left = (dl_date - date.today()).days
                days = max(1, days_left) if days_left is not None else 30
        except Exception:
            days = 30
        required_daily = required_rate(remaining, days)
        required_daily_30 = required_daily
        eta = estimate_eta(remaining, rate)
        rb = rate_breakdown(rate)
        results[g.id] = {
            "remaining": remaining,
            "rate_per_day": rb["per_day"],
            "rate_per_week": rb["per_week"],
            "rate_per_month": rb["per_month"],
            "eta_ts": None if eta is None else int(datetime.combine(eta, datetime.min.time()).timestamp()),
            "required_daily_30": required_daily_30,
            "progress_percent": (current_savings / g.target_amount * 100) if g.target_amount > 0 else 0
        }
    return results