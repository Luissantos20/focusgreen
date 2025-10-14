from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .utils import (
    get_user_dashboard_data,
    _today_range,
    _breakdown_minutes,
    _last_n_days_series,
    _current_streak,
    CO2_FACTOR_G_PER_HOUR,
    DAILY_NP_GOAL_MINUTES
)

# === View principal do dashboard ===
@login_required
def index(request):
    start_day, end_day, today = _today_range()
    prod_dia, nao_dia, tot_dia = _breakdown_minutes(request.user, start_day, end_day)

    # Semana (últimos 7 dias)
    end_week = timezone.make_aware(
        timezone.datetime.combine(timezone.localdate(), timezone.datetime.max.time())
    )
    start_week = end_week - timedelta(days=6)
    prod_sem, nao_sem, tot_sem = _breakdown_minutes(request.user, start_week, end_week)
    w_start_date, w_end_date = start_week.date(), end_week.date()

    # Série de 7 dias e streak
    series_7d = _last_n_days_series(request.user, n=7)
    streak = _current_streak(request.user, DAILY_NP_GOAL_MINUTES)

    # === Cálculo do CO₂ ===
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

    # === Ajustes de compatibilidade com Chart.js ===
    series_co2_day = [round(co2_dia, 1)]  # apenas um valor
    series_co2_week = co2_semana_series   # lista de dicionários [{date, co2}]

    # === Contexto enviado ao template ===
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


# === Endpoint seguro para IA ===
@login_required
def insights_data(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    data = get_user_dashboard_data(request.user)
    return JsonResponse(data, safe=True, json_dumps_params={'indent': 2})


# === Endpoint auxiliar para gráficos assíncronos ===
@login_required
def data_last_7_days(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    series = _last_n_days_series(request.user, n=7)
    return JsonResponse({'series': series})

