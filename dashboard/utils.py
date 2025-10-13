from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from tracker.models import ScreenTimeEntry

# === Constantes (educativas / configuráveis) ===
CO2_FACTOR_G_PER_HOUR = 50        # g de CO₂ emitidos por hora de uso não produtivo (estimativa educativa)
DAILY_NP_GOAL_MINUTES = 90        # meta diária de minutos "não produtivos"


# === Helpers internos ===
def _today_range():
    """Retorna o início e fim do dia atual, no timezone local."""
    today = timezone.localdate()
    start_dt = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    )
    end_dt = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.max.time())
    )
    return start_dt, end_dt, today


def _sum_minutes(qs):
    """Soma segura dos minutos de um queryset."""
    return qs.aggregate(total=Sum('minutes'))['total'] or 0


def _breakdown_minutes(user, start_dt, end_dt):
    """Retorna minutos produtivos, não produtivos e total no intervalo informado."""
    base = ScreenTimeEntry.objects.filter(
        user=user, started_at__range=(start_dt, end_dt)
    )
    prod = _sum_minutes(base.filter(category='PROD'))
    nao = _sum_minutes(base.filter(category='NAO_PROD'))
    return prod, nao, prod + nao


def _last_n_days_series(user, n=7):
    """Gera série dos últimos N dias com tempo produtivo e não produtivo."""
    days = []
    today = timezone.localdate()
    for i in range(n - 1, -1, -1):
        d = today - timedelta(days=i)
        start_dt = timezone.make_aware(
            timezone.datetime.combine(d, timezone.datetime.min.time())
        )
        end_dt = timezone.make_aware(
            timezone.datetime.combine(d, timezone.datetime.max.time())
        )
        prod, nao, tot = _breakdown_minutes(user, start_dt, end_dt)
        days.append({
            'date': d.isoformat(),
            'prod': prod,
            'nao': nao,
            'total': tot,
        })
    return days


def _current_streak(user, goal_minutes=DAILY_NP_GOAL_MINUTES):
    """Conta quantos dias consecutivos o usuário está dentro da meta."""
    streak = 0
    today = timezone.localdate()
    for i in range(0, 365):
        d = today - timedelta(days=i)
        start_dt = timezone.make_aware(
            timezone.datetime.combine(d, timezone.datetime.min.time())
        )
        end_dt = timezone.make_aware(
            timezone.datetime.combine(d, timezone.datetime.max.time())
        )
        _, nao, _ = _breakdown_minutes(user, start_dt, end_dt)
        if nao <= goal_minutes:
            streak += 1
        else:
            break
    return streak


# === Função principal — usada por dashboard e IA ===
def get_user_dashboard_data(user):
    """
    Retorna um resumo completo de uso digital do usuário para consumo do dashboard e do agente de IA.

    Estrutura:
    {
        "today": "2025-10-13",
        "daily": {...},
        "weekly": {...},
        "meta": {...},
        "context_summary": {...},
        "trend": {...}
    }
    """
    start_day, end_day, today = _today_range()
    prod_dia, nao_dia, tot_dia = _breakdown_minutes(user, start_day, end_day)

    # Últimos 7 dias
    series_7d = _last_n_days_series(user, n=7)
    streak = _current_streak(user, DAILY_NP_GOAL_MINUTES)

    # CO₂ diário e semanal
    co2_dia = (nao_dia / 60) * CO2_FACTOR_G_PER_HOUR
    co2_sem = sum([(d['nao'] / 60) * CO2_FACTOR_G_PER_HOUR for d in series_7d])

    # Média diária e taxa de foco (produtivo / total)
    focus_ratio = round(prod_dia / (tot_dia or 1) * 100, 1)

    # === Tendência (comparação dia atual vs média da semana anterior) ===
    if len(series_7d) > 1:
        avg_focus_prev = (sum(d['prod'] for d in series_7d[:-1]) /
                          (sum((d['total'] or 1) for d in series_7d[:-1])))
        focus_today = (series_7d[-1]['prod'] / (series_7d[-1]['total'] or 1))
        focus_change_pct = round((focus_today - avg_focus_prev) * 100, 1)
    else:
        focus_change_pct = 0.0

    trend_data = {
        "focus_change_pct": focus_change_pct,
        "trend_label": (
            "melhorando" if focus_change_pct > 0 else
            "piorando" if focus_change_pct < 0 else
            "estável"
        )
    }

    return {
        "today": today.isoformat(),
        "daily": {
            "prod": prod_dia,
            "nao_prod": nao_dia,
            "total": tot_dia,
            "focus_ratio": focus_ratio,
            "co2": round(co2_dia, 1),
        },
        "weekly": {
            "series": series_7d,
            "co2": round(co2_sem, 1),
            "avg_daily": round(sum(d['total'] for d in series_7d) / len(series_7d), 1),
        },
        "meta": {
            "goal_nao_prod": DAILY_NP_GOAL_MINUTES,
            "streak": streak,
        },
        "context_summary": {
            "days_tracked": len(series_7d),
            "co2_factor": CO2_FACTOR_G_PER_HOUR,
        },
        "trend": trend_data,
    }
