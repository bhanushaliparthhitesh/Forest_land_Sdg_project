from django.shortcuts import render, redirect
from pymongo import MongoClient
import matplotlib.pyplot as plt
import os
from django.conf import settings

# ----------------------------------------
# MongoDB Connection
# ----------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["sdg15_wildlife"]
collection = db["population"]

# ----------------------------------------
# Home Page - Display All Data
# ----------------------------------------
def home(request):
    data = list(collection.find().sort([("species", 1), ("year", 1)]))
    return render(request, 'tracker/home.html', {'data': data})

# ----------------------------------------
# Add or Update Data
# ----------------------------------------
def add_data(request):
    if request.method == "POST":
        species = request.POST['species']
        year = int(request.POST['year'])
        population = int(request.POST['population'])

        collection.update_one(
            {"species": species, "year": year},
            {"$set": {"population": population}},
            upsert=True
        )

        return redirect('home')

    return render(request, 'tracker/add.html')

# ----------------------------------------
# Analyze Population Trend
# ----------------------------------------
def analyze(request):
    trend = None

    if request.method == "POST":
        species = request.POST['species']

        records = list(collection.find({"species": species}).sort("year", 1))

        if len(records) < 2:
            trend = "Not enough data to analyze"
        else:
            start = records[0]["population"]
            end = records[-1]["population"]

            if end > start:
                trend = "INCREASING 📈"
            elif end < start:
                trend = "DECREASING 📉"
            else:
                trend = "STABLE"

    return render(request, 'tracker/analyze.html', {'trend': trend})

# ----------------------------------------
# Predict Future Population
# ----------------------------------------
def predict(request):
    result = None
    error = None

    if request.method == "POST":
        try:
            species = request.POST['species']
            target_year = int(float(request.POST['year']))   # user enters actual year

            records = list(collection.find({"species": species}).sort("year", 1))

            if len(records) < 2:
                error = "Not enough data to predict. Please add at least 2 records."
            else:
                last_year = int(float(records[-1]["year"]))
                start = float(records[0]["population"])
                end = float(records[-1]["population"])

                if target_year <= last_year:
                    error = f"Please enter a year greater than {last_year}."
                else:
                    years_ahead = target_year - last_year
                    avg_change = (end - start) / (len(records) - 1)

                    future_population = int(end + avg_change * years_ahead)

                    if future_population < 0:
                        error = "Predicted population cannot be negative."
                    else:
                        result = f"{future_population} (for year {target_year})"

        except ValueError:
            error = "Please enter valid numeric values."

    return render(request, 'tracker/predict.html', {'result': result, 'error': error})



# ----------------------------------------
# Visualize Population Trend
# ----------------------------------------
def visualize(request):
    image_path = None

    if request.method == "POST":
        species = request.POST['species']

        records = list(collection.find({"species": species}).sort("year", 1))

        if len(records) == 0:
            return render(request, 'tracker/visualize.html', {'image_path': None})

        years = [int(r["year"]) for r in records]
        populations = [int(r["population"]) for r in records]

        plt.figure()
        plt.plot(years, populations, marker='o')
        plt.title(f"{species} Population Trend")
        plt.xlabel("Year")
        plt.ylabel("Population")
        plt.grid()

        # Save graph inside static folder
        static_path = os.path.join(settings.BASE_DIR, 'tracker/static/tracker')
        if not os.path.exists(static_path):
            os.makedirs(static_path)

        file_path = os.path.join(static_path, 'plot.png')
        plt.savefig(file_path)
        plt.close()

        image_path = "tracker/plot.png"

    return render(request, 'tracker/visualize.html', {'image_path': image_path})
