import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import constants
from .services import prediction_services


def index(request):
    return render(request, "index.html")


def plot_forecast(request):
    dates, values, _, _ ,realDates ,realValues = prediction_services.forecast_btc_from_to()
    # Pass the data to the template
    context = {"dates": dates, "values": values }

    return render(request, "plot_template.html", context)


# Assuming your data is coming from your app's config
@csrf_exempt  # To temporarily disable CSRF protection (only for testing purposes; use CSRF token in production)
def update_forecast(request):
    if request.method == "POST":
        try:
            # Load the JSON body from the request
            body = json.loads(request.body)
            from_date = body.get("from_date")
            to_date = body.get("to_date")

            # Convert the dates to pd.Timestamp for comparison
            if not from_date:
                from_date = constants.DEFAULT_BTC_FROM_DATE
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d")

            dates, values, _, _, _, _ = prediction_services.forecast_btc_from_to(
                from_date=from_date, to_date=to_date
            )
            # Prepare the response data
            response_data = {
                "dates": dates,
                "values": values,
            }
            print(
                "Successfully updated forecast from {} to {}".format(from_date, to_date)
            )

            # Return the filtered data as JSON
            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def plot_forecast_with_high_low(request):
    try:
        dates, values, high_values, low_values, realDates, realValues = prediction_services.forecast_btc_from_to()
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    # Pass the data to the template
    context = {
        "forecastDates": dates,
        "forecastValues": values,
        "highValues": high_values,
        "lowValues": low_values,
        "realDates": realDates,
        "realValues": realValues,
    }

    return render(request, "plot_hl_template.html", context)


# Assuming your data is coming from your app's config
@csrf_exempt  # To temporarily disable CSRF protection (only for testing purposes; use CSRF token in production)
def update_forecast_with_high_low(request):
    if request.method == "POST":
        try:
            # Load the JSON body from the request
            body = json.loads(request.body)
            from_date = body.get("from_date")
            to_date = body.get("to_date")

            # Convert the dates to pd.Timestamp for comparison
            if not from_date:
                from_date = constants.DEFAULT_BTC_FROM_DATE
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                dates, values, high_values, low_values, realDates, realValues = (
                    prediction_services.forecast_btc_from_to(
                        from_date=from_date, to_date=to_date
                    )
                )
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)
            # Prepare the response data
            response_data = {
                "forecastDates": dates,
                "forecastValues": values,
                "highValues": high_values,
                "lowValues": low_values,
                "realDates": realDates,
                "realValues": realValues,
            }
            print(
                "Successfully updated forecast from {} to {}".format(from_date, to_date)
            )

            # Return the filtered data as JSON
            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
