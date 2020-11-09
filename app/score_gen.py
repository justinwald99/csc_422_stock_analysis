import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from pandas.core.frame import DataFrame
import seaborn as sb

model_scores = DataFrame(columns=["ticker", "model", "score"])

# Get tickers from model files:
model_filenames = os.listdir("data/model")
for model_type in ["k_mean", "db_scan"]:
    for model_file in model_filenames:
        if model_file == "results":
            continue
        print(model_file)
        ticker = model_file[0: model_file.index("_")]
        # Load data
        data = pd.read_csv(f"data/model/{ticker}_{model_type}.csv")
        # Drop the id column
        data.drop("id", axis="columns", inplace=True)
        # Drop any columns labeled noise by dbscan
        data = data[data["group"] != -1]

        # Find centers of groups
        centers = pd.DataFrame()
        for group in data["group"].unique():
            group_points = data[data["group"] == group]
            group_center = group_points[["num_positive", "num_negative", "percent_chg"]].mean()
            centers = centers.append(group_center, ignore_index=True)

        # Sort centers by num_positive tweets
        centers.sort_values(by=["num_positive", "num_negative"], ascending=True, inplace=True, ignore_index=True)

        # Plot data with group centers overlaid
        plt.scatter(x=data["num_positive"], y=data["num_negative"])
        plt.scatter(x=centers["num_positive"], y=centers["num_negative"])

        # Label groups after sorted centers
        if len(centers) == 3:
            labels = ["decrease", "neutral", "increase"]
        else:
            labels = ["decrease", "increase"]

        # Annotate centers with percent change
        for index, row in centers.iterrows():
            plt.annotate(f"{labels[index]}: {row['percent_chg']}", (row["num_positive"], row["num_negative"]))

        plt.xlabel("num_positive")
        plt.ylabel("num_negative")

        # Save graph
        plt.savefig(f"data/model/results/{ticker}_{model_type}_groups.jpg",
                    pil_kwargs={"optimize": True, "progressive": True, "quality": 90})
        plt.clf()

        # Create the pearson-moment correlation coefficient matrix
        cov_matrix = pd.DataFrame(np.corrcoef(centers.T))
        cov_matrix.columns = centers.columns
        cov_matrix.index = centers.columns
        sb.heatmap(cov_matrix, annot=True)
        plt.title("Covariance Heatmap")

        plt.savefig(f"data/model/results/{ticker}_{model_type}_cov_heatmap.jpg",
                    pil_kwargs={"optimize": True, "progressive": True, "quality": 90})
        plt.clf()

        # Calculate the correlation score
        score = cov_matrix["percent_chg"]["num_positive"]
        score -= cov_matrix["percent_chg"]["num_negative"]

        # Generate a score from -10 - 10 with negative numbers indicating a negative
        # correlation between sentiment and stock price, and positive a positive.

        score = score / 2 * 10
        model_scores = model_scores.append({"ticker": ticker, "model": model_type,
                                           "score": score}, ignore_index=True)

model_scores.to_csv("data/model/results/scores.csv", index_label="id")
model_scores = model_scores.sort_values(by="score", ignore_index=True, ascending=False)

for model in ["k_mean", "db_scan"]:
    models = model_scores[model_scores["model"] == model]
    plt.scatter(models["ticker"], models["score"], label=model)
plt.legend()
plt.title("Correlation Score by Model")
plt.ylabel("Correlation Score")
plt.xlabel("Company")
plt.savefig("data/model/results/scores_scatter.jpg",
            pil_kwargs={"optimize": True, "progressive": True, "quality": 90})
plt.show()
