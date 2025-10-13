from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from tracker.models import ScreenTimeEntry

# === Constantes (MVP) ===
CO2_FACTOR_G_PER_HOUR = 50        # g de CO₂ emitidos por hora de uso não produtivo (estimativa educativa)
DAILY_NP_GOAL_MINUTES = 90        # meta diária de minutos "não produtivos"


# === Helpers ===
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
    for i in range(n - 1, -1, -1):  # do mais antigo ao mais novo
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
    for i in range(0, 365):  # limite de segurança
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


# === NOVO: agregador de dados completos (para IA) ===
def get_user_dashboard_data(user):
    """
    Gera um pacote completo de dados para IA ou análises automatizadas.
    Retorna métricas diárias, semanais, de metas e CO₂.
    """
    start_day, end_day, today = _today_range()
    prod_dia, nao_dia, tot_dia = _breakdown_minutes(user, start_day, end_day)

    # Últimos 7 dias
    series_7d = _last_n_days_series(user, n=7)
    streak = _current_streak(user, DAILY_NP_GOAL_MINUTES)

    # CO₂ diário e semanal (apenas tempo não produtivo)
    co2_dia = (nao_dia / 60) * CO2_FACTOR_G_PER_HOUR
    co2_sem = sum([(d['nao'] / 60) * CO2_FACTOR_G_PER_HOUR for d in series_7d])

    # Média diária e taxa de foco
    focus_ratio = round(prod_dia / (tot_dia or 1) * 100, 1)

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
    }


# === Views ===
@login_required
def index(request):
    """
    Renderiza o dashboard principal do usuário.
    Também gera os dados necessários para gráficos e KPIs.
    """
    start_day, end_day, today = _today_range()
    prod_dia, nao_dia, tot_dia = _breakdown_minutes(request.user, start_day, end_day)

    # Semana (últimos 7 dias)
    end_week = timezone.make_aware(
        timezone.datetime.combine(timezone.localdate(), timezone.datetime.max.time())
    )
    start_week = end_week - timedelta(days=6)
    prod_sem, nao_sem, tot_sem = _breakdown_minutes(request.user, start_week, end_week)
    w_start_date, w_end_date = start_week.date(), end_week.date()

    # Série de 7 dias
    series_7d = _last_n_days_series(request.user, n=7)
    streak = _current_streak(request.user, DAILY_NP_GOAL_MINUTES)

    # CO₂
    co2_dia = (nao_dia / 60) * CO2_FACTOR_G_PER_HOUR
    co2_semana_series = []
    co2_semana_total = 0
    for d in series_7d:
        co2_gerado = (d['nao'] / 60) * CO2_FACTOR_G_PER_HOUR
        co2_semana_series.append({
            'date': d['date'],
            'co2': round(co2_gerado, 1)
        })
        co2_semana_total += co2_gerado

    # Dados para os gráficos de CO₂
    series_co2_day = [round(co2_dia, 1), 0]
    series_co2_week = co2_semana_series

    # Contexto enviado ao template
    context = {
        'today': today,
        # dia
        'minutes_prod_day': prod_dia,
        'minutes_nao_day': nao_dia,
        'minutes_total_day': tot_dia,
        # semana
        'minutes_prod_week': prod_sem,
        'minutes_nao_week': nao_sem,
        'minutes_total_week': tot_sem,
        # metas e streak
        'daily_np_goal': DAILY_NP_GOAL_MINUTES,
        'streak_days': streak,
        # co₂
        'co2_factor': CO2_FACTOR_G_PER_HOUR,
        'series_7d': series_7d,
        'series_co2_day': series_co2_day,
        'series_co2_week': series_co2_week,
        'co2_dia': round(co2_dia, 1),
        'co2_semana_total': round(co2_semana_total, 1),
        # gráfico de tempo
        'day_chart_data': [prod_dia, nao_dia],
        'week_range': (w_start_date, w_end_date),
    }
    return render(request, 'dashboard/index.html', context)


# === NOVO: endpoint JSON para IA ou API ===
@login_required
def insights_data(request):
    """
    Endpoint que retorna um JSON completo com todos os dados do dashboard.
    Esse endpoint poderá ser consumido por um agente de IA.
    """
    data = get_user_dashboard_data(request.user)
    return JsonResponse(data)


# === RECRIADO: endpoint auxiliar de compatibilidade ===
@login_required
def data_last_7_days(request):
    """
    Endpoint auxiliar para retornar os últimos 7 dias de uso (produtivo e não produtivo).
    Usado para atualização assíncrona dos gráficos via fetch().
    """
    series = _last_n_days_series(request.user, n=7)
    return JsonResponse({'series': series})
